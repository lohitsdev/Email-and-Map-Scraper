# 🚀 Google Maps & Email Extractor

## 🔍 What is this?
This project helps you extract information from:
1. **Google Maps Business Extractor** 🗺️ - Finds business details (name, rating, phone, etc.) from Google Maps.
2. **Email Extractor** 📧 - Extracts email addresses from websites.

## 🎯 Features
### 🏢 Google Maps Business Extractor
✅ Search for businesses by type & location <br>
✅ Get details like name, rating, reviews, contact info <br>
✅ Scroll & auto-scroll to find more businesses <br>
✅ Save data in JSON format <br>
✅ Easy-to-use graphical interface <br>

### 📩 Email Extractor
✅ Find emails from websites automatically <br>
✅ Prioritizes contact & about pages <br>
✅ Filters out spam & incorrect emails <br>
✅ Saves emails in a text file <br>
✅ User-friendly GUI <br>

## 🔧 Requirements
🔹 **Python 3.7+** 🐍  <br>
🔹 **Playwright** 🎭  <br>
🔹 **BeautifulSoup4** 🍜  <br>
🔹 **Tkinter (GUI)** 🖥️  <br>
🔹 **aiohttp, threading, queue** ⚡  <br>

📌 Install dependencies:
```sh
pip install playwright beautifulsoup4 aiohttp
playwright install
```

## 🛠️ How to Use
### 🌍 Google Maps Extractor
1️⃣ Enter business type & location. <br>
2️⃣ Click **Start Extraction** ▶️ <br>
3️⃣ Click **Stop** ⏹️ anytime. <br>
4️⃣ **Load More Results** 🔄 manually. <br>
5️⃣ Enable **Auto-scroll** 🔽 to fetch more results. <br>
6️⃣ Save results **as JSON** 💾 <br>

### 📧 Email Extractor
1️⃣ Enter website URL 🌐 <br>
2️⃣ Set **max pages** & **tasks** 🛠️ <br>
3️⃣ Click **Start Extraction** ▶️ <br>
4️⃣ Click **Stop** ⏹️ anytime. <br>
5️⃣ Save emails **as TXT file** 📂 <br>

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
Developed by **[lohitsdev](https://github.com/lohitsdev)** 👨‍💻

