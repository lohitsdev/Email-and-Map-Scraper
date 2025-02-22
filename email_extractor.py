import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
import asyncio
from playwright.async_api import async_playwright
import re
import logging
from urllib.parse import urljoin, urlparse
import aiohttp
from bs4 import BeautifulSoup
import threading
import queue
from datetime import datetime
import concurrent.futures
import asyncio
from functools import partial

class EmailExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Email Extractor")
        self.root.geometry("1000x700")
        
        # Configure styling
        self.style = ttk.Style()
        self.style.configure("Modern.TButton", padding=10, font=('Helvetica', 10))
        self.style.configure("Modern.TLabel", font=('Helvetica', 10))
        self.style.configure("Red.TButton", background="red")
        
        self.setup_ui()
        self.emails_found = set()
        self.processing = False
        self.visited_urls = set()
        self.url_queue = queue.Queue()
        self.max_pages = 50
        self.should_stop = False
        self.concurrent_tasks = 5  # Number of concurrent pages to process
        
    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for inputs
        top_frame = ttk.LabelFrame(main_container, text="Configuration", padding="10")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # URL input
        url_frame = ttk.Frame(top_frame)
        url_frame.pack(fill=tk.X, pady=5)
        ttk.Label(url_frame, text="Website URL:", style="Modern.TLabel").pack(side=tk.LEFT)
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Controls frame
        controls_frame = ttk.Frame(top_frame)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Left controls
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side=tk.LEFT)
        
        ttk.Label(left_controls, text="Max Pages:", style="Modern.TLabel").pack(side=tk.LEFT, padx=5)
        self.max_pages_entry = ttk.Entry(left_controls, width=5)
        self.max_pages_entry.insert(0, "50")
        self.max_pages_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(left_controls, text="Concurrent Tasks:", style="Modern.TLabel").pack(side=tk.LEFT, padx=5)
        self.concurrent_entry = ttk.Entry(left_controls, width=5)
        self.concurrent_entry.insert(0, "5")
        self.concurrent_entry.pack(side=tk.LEFT)
        
        # Right controls
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT)
        
        self.extract_btn = ttk.Button(
            right_controls,
            text="Start Extraction",
            style="Modern.TButton",
            command=self.start_extraction
        )
        self.extract_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            right_controls,
            text="Stop",
            style="Modern.TButton",
            command=self.stop_extraction,
            state='disabled'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(
            right_controls,
            text="Save Results",
            style="Modern.TButton",
            command=self.save_results
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
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
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Stats frame
        self.stats_frame = ttk.Frame(progress_frame)
        self.stats_frame.pack(side=tk.RIGHT)
        
        self.stats_var = tk.StringVar(value="Pages: 0 | Emails: 0")
        ttk.Label(
            self.stats_frame,
            textvariable=self.stats_var,
            style="Modern.TLabel"
        ).pack(side=tk.RIGHT)
        
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

    def is_valid_url(self, url, base_url):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            base_parsed = urlparse(base_url)
            return parsed.netloc == base_parsed.netloc and parsed.scheme in ['http', 'https']
        except:
            return False

    def is_valid_email(self, email):
        """Enhanced email validation to filter out false positives"""
        if len(email) > 254 or len(email) < 5:
            return False
            
        # Reject if contains common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if any(ext in email.lower() for ext in image_extensions):
            return False
            
        # Reject if contains dimensions (like 768x960)
        if re.search(r'\d+x\d+', email):
            return False
            
        # Reject if contains @2x or similar scale markers
        if re.search(r'@\d+x', email):
            return False
            
        # Check for common file naming patterns
        invalid_patterns = [
            r'-\d+x\d+',  # Dimension markers
            r'_\d+x\d+',  # Underscore dimensions
            r'[\w-]+shot',  # Screenshot/headshot
            r'head-shot',
            r'thumbnail',
            r'avatar',
            r'profile-pic'
        ]
        
        if any(re.search(pattern, email.lower()) for pattern in invalid_patterns):
            return False
        
        # Basic email pattern validation
        email_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
            
        # Additional checks for valid email
        parts = email.split('@')
        if len(parts) != 2:
            return False
            
        local_part, domain = parts
        
        # Check domain part
        if not all(part.isalnum() or part == '-' for part in domain.split('.')):
            return False
            
        # Check for consecutive special characters
        if re.search(r'[._%+-]{2,}', local_part):
            return False
            
        # Check for common valid email domains (optional)
        common_domains = ['.com', '.org', '.net', '.edu', '.gov', '.mil', '.biz', '.info']
        if not any(domain.lower().endswith(d) for d in common_domains):
            # If not a common domain, be more strict
            if len(domain) > 50:  # Unusually long domain
                return False
        
        return True

    def extract_emails_from_text(self, text):
        """Extract emails using multiple regex patterns with improved filtering"""
        email_patterns = [
            # Standard email format
            r'\b[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            
            # Protected email formats
            r'\b[A-Za-z0-9][A-Za-z0-9._%+-]*\s*[\[\(]\s*at\s*[\]\)]\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            r'\b[A-Za-z0-9][A-Za-z0-9._%+-]*\s+at\s+[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            
            # Spaced email format
            r'\b[A-Za-z0-9][A-Za-z0-9._%+-]*\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b',
        ]
        
        emails = set()
        for pattern in email_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            for email in found:
                # Clean and normalize email
                clean_email = re.sub(r'\s+|\[at\]|\(at\)|\s*at\s*', '@', email)
                clean_email = clean_email.strip().lower()
                if self.is_valid_email(clean_email):
                    emails.add(clean_email)
        return emails

    async def extract_urls_from_page(self, page_content, base_url):
        """Extract all URLs from page content"""
        soup = BeautifulSoup(page_content, 'html.parser')
        urls = set()
        
        for anchor in soup.find_all('a', href=True):
            url = anchor['href']
            full_url = urljoin(base_url, url)
            if self.is_valid_url(full_url, base_url):
                urls.add(full_url)
        return urls

    async def extract_emails_from_page(self, url):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = await context.new_page()
                
                # Set timeout and handle navigation
                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                except:
                    await browser.close()
                    return set(), set()
                
                # Get page content after JavaScript execution
                content = await page.content()
                
                # Extract emails from visible content
                emails = self.extract_emails_from_text(content)
                
                # Extract emails from page source
                urls = await self.extract_urls_from_page(content, url)
                
                # Check for contact/about pages
                priority_urls = {u for u in urls if any(x in u.lower() for x in ['contact', 'about', 'team', 'staff'])}
                
                # Add remaining URLs
                urls = priority_urls | urls
                
                await browser.close()
                return emails, urls
                
        except Exception as e:
            logging.error(f"Error extracting from {url}: {str(e)}")
            return set(), set()

    async def process_url(self, base_url):
        self.should_stop = False
        self.visited_urls = set()
        self.url_queue = queue.Queue()
        self.url_queue.put(base_url)
        self.emails_found = set()
        
        max_pages = int(self.max_pages_entry.get())
        concurrent_tasks = int(self.concurrent_entry.get())
        
        self.progress_bar['maximum'] = max_pages
        
        while not self.url_queue.empty() and len(self.visited_urls) < max_pages and not self.should_stop:
            # Process multiple URLs concurrently
            tasks = []
            for _ in range(min(concurrent_tasks, max_pages - len(self.visited_urls))):
                if self.url_queue.empty() or self.should_stop:
                    break
                current_url = self.url_queue.get()
                if current_url not in self.visited_urls:
                    self.visited_urls.add(current_url)
                    tasks.append(self.extract_emails_from_page(current_url))
            
            if not tasks:
                break
                
            # Update progress
            self.progress_bar['value'] = len(self.visited_urls)
            self.stats_var.set(f"Pages: {len(self.visited_urls)} | Emails: {len(self.emails_found)}")
            
            # Process batch of URLs
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for emails, new_urls in (r for r in results if isinstance(r, tuple)):
                self.emails_found.update(emails)
                if emails:
                    self.root.after(0, self.update_results, emails)
                
                # Add new URLs to queue
                for url in new_urls:
                    if url not in self.visited_urls:
                        self.url_queue.put(url)

    def stop_extraction(self):
        self.should_stop = True
        self.progress_var.set("Stopping...")
        self.stop_btn.state(['disabled'])

    def save_results(self):
        if not self.emails_found:
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if filename:
            with open(filename, 'w') as f:
                f.write(f"Email Extraction Results\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total emails found: {len(self.emails_found)}\n")
                f.write(f"Pages crawled: {len(self.visited_urls)}\n")
                f.write("\nEmails:\n")
                for email in sorted(self.emails_found):
                    f.write(f"{email}\n")

    def start_extraction(self):
        if self.processing:
            return
            
        url = self.url_entry.get().strip()
        if not url:
            self.results_text.insert(tk.END, "Please enter a valid URL\n")
            return
            
        self.processing = True
        self.progress_bar['value'] = 0
        self.extract_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self.results_text.delete(1.0, tk.END)
        
        threading.Thread(target=self.run_extraction, args=(url,), daemon=True).start()

    def run_extraction(self, url):
        asyncio.run(self.process_url(url))
        self.root.after(0, self.finish_processing)

    def update_results(self, new_emails):
        self.results_text.insert(tk.END, f"Found {len(new_emails)} new email(s):\n")
        for email in sorted(new_emails):
            self.results_text.insert(tk.END, f"• {email}\n")
        self.results_text.see(tk.END)

    def finish_processing(self):
        self.processing = False
        self.progress_bar['value'] = self.progress_bar['maximum']
        self.progress_var.set(f"Completed! Total emails found: {len(self.emails_found)}")
        self.extract_btn.state(['!disabled'])
        self.stop_btn.state(['disabled'])
        
        # Show final summary
        self.results_text.insert(tk.END, "\n=== Final Summary ===\n")
        self.results_text.insert(tk.END, f"Pages crawled: {len(self.visited_urls)}\n")
        self.results_text.insert(tk.END, f"Total unique emails found: {len(self.emails_found)}\n")
        
        if self.should_stop:
            self.results_text.insert(tk.END, "Extraction was stopped by user\n")

def main():
    root = tk.Tk()
    app = EmailExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 