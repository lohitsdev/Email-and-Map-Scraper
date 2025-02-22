# 🚀 Google Maps & Email Extractor

## 🔍 What is this?
This project helps you extract information from:
1. **Google Maps Business Extractor** 🗺️ - Finds business details (name, rating, phone, etc.) from Google Maps.
2. **Email Extractor** 📧 - Extracts email addresses from websites.

## 🎯 Features
### 🏢 Google Maps Business Extractor
✅ Search for businesses by type & location <br>
✅ Get details like name, rating, reviews, contact info
✅ Scroll & auto-scroll to find more businesses
✅ Save data in JSON format
✅ Easy-to-use graphical interface

### 📩 Email Extractor
✅ Find emails from websites automatically
✅ Prioritizes contact & about pages
✅ Filters out spam & incorrect emails
✅ Saves emails in a text file
✅ User-friendly GUI

## 🔧 Requirements
🔹 **Python 3.7+** 🐍  
🔹 **Playwright** 🎭  
🔹 **BeautifulSoup4** 🍜  
🔹 **Tkinter (GUI)** 🖥️  
🔹 **aiohttp, threading, queue** ⚡  

📌 Install dependencies:
```sh
pip install playwright beautifulsoup4 aiohttp
playwright install
```

## 🛠️ How to Use
### 🌍 Google Maps Extractor
1️⃣ Enter business type & location.
2️⃣ Click **Start Extraction** ▶️
3️⃣ Click **Stop** ⏹️ anytime.
4️⃣ **Load More Results** 🔄 manually.
5️⃣ Enable **Auto-scroll** 🔽 to fetch more results.
6️⃣ Save results **as JSON** 💾

### 📧 Email Extractor
1️⃣ Enter website URL 🌐
2️⃣ Set **max pages** & **tasks** 🛠️
3️⃣ Click **Start Extraction** ▶️
4️⃣ Click **Stop** ⏹️ anytime.
5️⃣ Save emails **as TXT file** 📂

## 📜 Output Example
### 🏢 Business Extractor (JSON)
```json
{
  "extraction_date": "YYYY-MM-DD HH:MM:SS",
  "total_businesses": 10,
  "businesses": [
    {
      "name": "Business Name",
      "rating": "4.5",
      "reviews": "120",
      "type": "Restaurant",
      "location": "New York, NY",
      "phone": "123-456-7890",
      "services": ["Dine-in", "Takeout"]
    }
  ]
}
```

### 📩 Email Extractor (TXT)
```
Email Extraction Results
Date: YYYY-MM-DD HH:MM:SS
Total emails found: 15
Pages crawled: 50

Emails:
example@email.com
contact@company.com
...
```

## ❓ Troubleshooting
🔹 **Playwright not working?** Try:
```sh
playwright install
```
🔹 **Google Maps changes?** Update selectors.
🔹 **Errors?** Install missing dependencies:
```sh
pip install -r requirements.txt
```
🔹 **Rate limits?** Reduce search frequency.

## ❤️ Contribute
Want to help? Feel free to submit issues or pull requests! 🤝

## 📜 License
Licensed under **MIT License** 📝

## 👨‍💻 Author
Developed by **[Your Name](https://github.com/yourusername)** 👨‍💻

