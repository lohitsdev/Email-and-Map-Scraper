import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import re
import logging
from urllib.parse import quote
import threading

class GMapsExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Maps Business Extractor")
        self.root.geometry("1000x800")
        
        # Configure styling
        self.style = ttk.Style()
        self.style.configure("Modern.TButton", padding=10, font=('Helvetica', 10))
        self.style.configure("Modern.TLabel", font=('Helvetica', 10))
        
        self.setup_ui()
        self.businesses = []
        self.processing = False
        self.should_stop = False
        
    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Search configuration frame
        search_frame = ttk.LabelFrame(main_container, text="Search Configuration", padding="10")
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Business type input
        type_frame = ttk.Frame(search_frame)
        type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(type_frame, text="Business Type:", style="Modern.TLabel").pack(side=tk.LEFT)
        self.type_entry = ttk.Entry(type_frame, width=30)
        self.type_entry.pack(side=tk.LEFT, padx=5)
        
        # Location input
        location_frame = ttk.Frame(search_frame)
        location_frame.pack(fill=tk.X, pady=5)
        ttk.Label(location_frame, text="Location:", style="Modern.TLabel").pack(side=tk.LEFT)
        self.location_entry = ttk.Entry(location_frame, width=30)
        self.location_entry.pack(side=tk.LEFT, padx=5)
        
        # Controls frame
        controls_frame = ttk.Frame(search_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Left side controls
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side=tk.LEFT)
        
        self.extract_btn = ttk.Button(
            left_controls,
            text="Start Extraction",
            style="Modern.TButton",
            command=self.start_extraction
        )
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            left_controls,
            text="Stop",
            style="Modern.TButton",
            command=self.stop_extraction,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side controls
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT)
        
        self.clear_btn = ttk.Button(
            right_controls,
            text="Clear Results",
            style="Modern.TButton",
            command=self.clear_results
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(
            right_controls,
            text="Save Results",
            style="Modern.TButton",
            command=self.save_results
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Add scroll control frame
        scroll_frame = ttk.Frame(search_frame)
        scroll_frame.pack(fill=tk.X, pady=5)
        
        self.scroll_btn = ttk.Button(
            scroll_frame,
            text="Load More Results",
            style="Modern.TButton",
            command=self.scroll_and_fetch,
            state='disabled'
        )
        self.scroll_btn.pack(side=tk.LEFT, padx=5)
        
        self.auto_scroll_var = tk.BooleanVar(value=False)
        self.auto_scroll_check = ttk.Checkbutton(
            scroll_frame,
            text="Auto-scroll",
            variable=self.auto_scroll_var,
            command=self.toggle_auto_scroll
        )
        self.auto_scroll_check.pack(side=tk.LEFT, padx=5)
        
        # Add results count display
        self.count_var = tk.StringVar(value="Results: 0")
        ttk.Label(
            scroll_frame,
            textvariable=self.count_var,
            style="Modern.TLabel"
        ).pack(side=tk.RIGHT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_container, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(
            progress_frame,
            textvariable=self.progress_var,
            style="Modern.TLabel"
        ).pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Results frame
        results_frame = ttk.LabelFrame(main_container, text="Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=('Courier', 10)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)

    async def extract_business_info(self, page):
        """Extract business information from the current page"""
        businesses = []
        
        # Wait for business listings to load
        await page.wait_for_selector('.bfdHYd', timeout=30000)
        
        # Get all business elements
        business_elements = await page.query_selector_all('.bfdHYd')
        
        for element in business_elements:
            try:
                business = {}
                
                # Extract business name
                name_elem = await element.query_selector('.qBF1Pd')
                if name_elem:
                    business['name'] = await name_elem.inner_text()
                
                # Extract rating and reviews
                rating_elem = await element.query_selector('.MW4etd')
                reviews_elem = await element.query_selector('.UY7F9')
                if rating_elem:
                    business['rating'] = await rating_elem.inner_text()
                if reviews_elem:
                    reviews_text = await reviews_elem.inner_text()
                    business['reviews'] = re.search(r'\((\d+)\)', reviews_text).group(1)
                
                # Extract business type and location
                type_location = await element.query_selector_all('.W4Efsd span')
                if type_location:
                    business['type'] = await type_location[0].inner_text()
                    if len(type_location) > 2:
                        business['location'] = await type_location[2].inner_text()
                
                # Extract hours and phone
                details = await element.query_selector_all('.W4Efsd .W4Efsd span')
                for detail in details:
                    text = await detail.inner_text()
                    if 'Open' in text or 'Closed' in text:
                        business['hours'] = text
                    if re.match(r'\d{3}[\s-]?\d{3}[\s-]?\d{4}', text):
                        business['phone'] = text
                
                # Extract additional services
                services = await element.query_selector_all('.ah5Ghc span')
                if services:
                    business['services'] = [await service.inner_text() for service in services]
                
                if business:
                    businesses.append(business)
                    
            except Exception as e:
                logging.error(f"Error extracting business info: {str(e)}")
                continue
                
        return businesses

    async def scroll_page(self, page):
        """Scroll the page to load more results"""
        prev_height = 0
        while True:
            curr_height = await page.evaluate('document.documentElement.scrollHeight')
            if curr_height == prev_height:
                break
            await page.evaluate('window.scrollTo(0, document.documentElement.scrollHeight)')
            await page.wait_for_timeout(2000)  # Wait for content to load
            prev_height = curr_height

    async def auto_scroll_and_fetch(self):
        """Continuously scroll and fetch while auto-scroll is enabled"""
        try:
            while not self.should_stop and self.auto_scroll_var.get():
                await self.scroll_and_fetch_async()
                await asyncio.sleep(2)  # Wait between scrolls
        except Exception as e:
            self.root.after(0, lambda err=e: self.results_text.insert(tk.END, f"Auto-scroll error: {str(err)}\n"))

    async def process_search(self, business_type, location):
        try:
            async with async_playwright() as p:
                self.browser = await p.chromium.launch(headless=False)
                self.page = await self.browser.new_page()
                
                # Set viewport size for better scrolling
                await self.page.set_viewport_size({"width": 1280, "height": 800})
                
                # Construct search URL
                search_query = f"{business_type} {location}"
                encoded_query = quote(search_query)
                url = f"https://www.google.com/maps/search/{encoded_query}"
                
                await self.page.goto(url, wait_until="networkidle")
                await self.page.wait_for_timeout(3000)
                
                try:
                    # Wait for the feed to be available
                    await self.page.wait_for_selector('[role="feed"]', timeout=10000)
                    
                    # Enable scroll button after initial load
                    self.root.after(0, lambda: self.scroll_btn.state(['!disabled']))
                    
                    # Extract initial results
                    new_businesses = await self.extract_business_info(self.page)
                    if new_businesses:
                        self.businesses.extend(new_businesses)
                        self.root.after(0, lambda b=new_businesses: self.update_results(b))
                        self.root.after(0, lambda: self.count_var.set(f"Results: {len(self.businesses)}"))
                    
                    # Start auto-scroll if enabled
                    if self.auto_scroll_var.get():
                        await self.auto_scroll_and_fetch()
                        
                except Exception as inner_e:
                    self.root.after(0, lambda err=inner_e: self.results_text.insert(tk.END, f"Error during extraction: {str(err)}\n"))
                
        except Exception as outer_e:
            self.root.after(0, lambda err=outer_e: self.results_text.insert(tk.END, f"Error starting search: {str(err)}\n"))

    def start_extraction(self):
        if self.processing:
            return
            
        business_type = self.type_entry.get().strip()
        location = self.location_entry.get().strip()
        
        if not business_type or not location:
            self.results_text.insert(tk.END, "Please enter both business type and location\n")
            return
            
        self.processing = True
        self.businesses = []
        self.progress_bar.start()
        self.extract_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self.clear_btn.state(['disabled'])
        self.results_text.delete(1.0, tk.END)
        
        threading.Thread(target=self.run_extraction, args=(business_type, location), daemon=True).start()

    def run_extraction(self, business_type, location):
        asyncio.run(self.process_search(business_type, location))
        self.root.after(0, self.finish_processing)

    def update_results(self, new_businesses):
        self.results_text.insert(tk.END, f"\nFound {len(new_businesses)} new businesses:\n")
        for business in new_businesses:
            self.results_text.insert(tk.END, "\n-------------------\n")
            for key, value in business.items():
                if isinstance(value, list):
                    self.results_text.insert(tk.END, f"{key}: {', '.join(value)}\n")
                else:
                    self.results_text.insert(tk.END, f"{key}: {value}\n")
        self.results_text.see(tk.END)

    def stop_extraction(self):
        self.should_stop = True
        self.auto_scroll_var.set(False)  # Disable auto-scroll
        self.progress_var.set("Stopping...")
        self.stop_btn.state(['disabled'])
        self.scroll_btn.state(['disabled'])
        
        # Close browser if it exists
        if hasattr(self, 'browser'):
            asyncio.run(self.browser.close())

    def save_results(self):
        if not self.businesses:
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=f"businesses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_businesses': len(self.businesses),
                    'businesses': self.businesses
                }, f, ensure_ascii=False, indent=2)

    def clear_results(self):
        """Clear all results and reset the display"""
        self.results_text.delete(1.0, tk.END)
        self.businesses = []
        self.progress_var.set("Ready")
        self.progress_bar.stop()
        self.progress_bar['value'] = 0
        self.stats_var.set("Pages: 0 | Emails: 0")
        
        # Add confirmation message
        self.results_text.insert(tk.END, "Results cleared.\n")

    def finish_processing(self):
        self.processing = False
        self.progress_bar.stop()
        self.progress_var.set(f"Completed! Total businesses found: {len(self.businesses)}")
        self.extract_btn.state(['!disabled'])
        self.stop_btn.state(['disabled'])
        self.scroll_btn.state(['disabled'])
        self.clear_btn.state(['!disabled'])
        self.auto_scroll_var.set(False)  # Disable auto-scroll
        
        # Show final summary
        self.results_text.insert(tk.END, "\n=== Final Summary ===\n")
        self.results_text.insert(tk.END, f"Total businesses found: {len(self.businesses)}\n")
        
        if self.should_stop:
            self.results_text.insert(tk.END, "Extraction was stopped by user\n")

    def toggle_auto_scroll(self):
        """Handle auto-scroll checkbox changes"""
        if self.auto_scroll_var.get() and self.processing:
            # Start auto-scrolling in a separate thread
            threading.Thread(
                target=lambda: asyncio.run(self.auto_scroll_and_fetch()),
                daemon=True
            ).start()

    def scroll_and_fetch(self):
        """Trigger a single scroll and fetch operation"""
        if not self.processing:
            return
        
        # Run in separate thread to prevent UI freeze
        threading.Thread(
            target=lambda: asyncio.run(self.scroll_and_fetch_async()),
            daemon=True
        ).start()

    async def scroll_and_fetch_async(self):
        """Scroll once and fetch new results"""
        try:
            # Scroll down
            await self.page.evaluate('''
                let feed = document.querySelector('[role="feed"]');
                if (feed) {
                    feed.scrollBy(0, 800);
                } else {
                    window.scrollBy(0, 800);
                }
            ''')
            await self.page.wait_for_timeout(1500)  # Wait for content to load
            
            # Extract new results
            new_businesses = await self.extract_business_info(self.page)
            
            # Update results
            if new_businesses:
                new_unique = [b for b in new_businesses if b not in self.businesses]
                if new_unique:
                    self.businesses.extend(new_unique)
                    self.root.after(0, lambda b=new_unique: self.update_results(b))
                    self.root.after(0, lambda: self.count_var.set(f"Results: {len(self.businesses)}"))
            
        except Exception as e:
            self.root.after(0, lambda err=e: self.results_text.insert(tk.END, f"Error during scroll: {str(err)}\n"))

def main():
    root = tk.Tk()
    app = GMapsExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 