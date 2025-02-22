# Google Maps Business Extractor

## Overview
Google Maps Business Extractor is a Python-based GUI application that automates the extraction of business information from Google Maps using Playwright. It retrieves details such as business names, ratings, reviews, location, contact information, and services offered.

## Features
- Search for businesses based on type and location
- Extract business details including:
  - Name
  - Rating
  - Number of reviews
  - Business type
  - Location
  - Contact details (phone, hours, etc.)
  - Services offered
- Scroll and auto-scroll functionality for loading more results
- Save extracted data in JSON format
- User-friendly GUI built with Tkinter

## Requirements
### Dependencies
Ensure you have the following installed:

- Python 3.7+
- Playwright
- Tkinter (pre-installed with Python on Windows)
- asyncio
- json
- datetime
- re
- logging
- urllib.parse
- threading

### Install Playwright
```sh
pip install playwright
playwright install
```

### Install Other Dependencies
```sh
pip install -r requirements.txt
```

## Installation
Clone this repository:
```sh
git clone https://github.com/yourusername/gmaps-business-extractor.git
cd gmaps-business-extractor
```

Run the application:
```sh
python main.py
```

## Usage
1. Enter the business type (e.g., "restaurants", "plumbers") and location.
2. Click "Start Extraction" to begin scraping business details.
3. Click "Stop" to halt extraction at any time.
4. Use "Load More Results" to manually scroll and fetch more businesses.
5. Enable "Auto-scroll" to continuously fetch more businesses automatically.
6. Click "Save Results" to export data to a JSON file.

## Output Format
The extracted data is saved in JSON format with the following structure:
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
      "hours": "Open until 10 PM",
      "phone": "123-456-7890",
      "services": ["Dine-in", "Takeout"]
    }
  ]
}
```

## Troubleshooting
- Ensure Playwright is installed and updated (`playwright install`).
- If Google Maps layout changes, the selectors may need updating.
- For errors related to missing dependencies, reinstall them using:
  ```sh
  pip install -r requirements.txt
  ```
- If you encounter rate limits from Google, try reducing the request frequency.

## Contributing
Feel free to contribute by submitting issues or pull requests. Please ensure your code follows PEP8 standards and includes comments where necessary.

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author
Developed by [Your Name](https://github.com/yourusername)
