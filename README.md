<<<<<<< HEAD
# 🔒 AI-Based Phishing Website Detection System

A comprehensive Flask-based web application that uses machine learning and advanced security checks to detect phishing websites. 

## ✨ Features

### Core Detection
- **Machine Learning Model**: Pre-trained model for phishing detection
- **URL Analysis**: 30+ feature extraction for ML prediction
- **Risk Scoring**: Comprehensive risk calculation (0-100)
- **Confidence Metrics**: Probability-based confidence scores

### Advanced Security Checks
- **SSL Certificate Validation** ✅ 🔐
  - Verifies SSL certificate validity
  - Displays certificate issuer information
  - Flags invalid or missing certificates

- **Suspicious TLD Detection** ⚠️
  - Detects high-risk top-level domains
  - Monitors: .xyz, .top, .tk, .ml, .ga, .cf, .click, .download, .review, .webcam, .date, .trade, .faith, .accountant

- **WHOIS Lookup** 🔍
  - Retrieves domain registration information
  - Detects private/hidden registrations
  - Shows domain creation date

- **VirusTotal Integration** 🦠
  - Scans URLs against VirusTotal database
  - Shows malicious, suspicious, and undetected counts
  - Requires API key (optional)

### Analytics & Visualization
- **Pie Charts** 📊
  - Visual breakdown of legitimate vs phishing detections
  - Real-time statistics

- **Line Charts** 📈
  - Cumulative tracking of detections over time
  - Trend analysis

- **Scan Statistics** 📋
  - Total scans performed
  - Legitimate count
  - Phishing count
  - Detection rate percentage

### User Experience
- **Dark Mode** 🌙
  - Toggle dark/light theme
  - Persistent preference (localStorage)

- **Scan History** 📜
  - Displays all previous scans
  - Shows URL, result, confidence, and timestamp
  - Sortable and searchable

- **CSV Export** 📥
  - Export entire scan history to CSV
  - Includes URL, result, confidence, and timestamp
  - One-click download

- **Responsive Design** 📱
  - Works on desktop, tablet, and mobile
  - Adaptive grid layouts

### Risk Analysis
- **Detailed Risk Reasons** ⚠️
  - HTTP vs HTTPS status
  - Suspicious keywords detection
  - URL length analysis
  - Subdomain analysis
  - @ symbol detection
  - URL shortener detection
  - IP address usage
  - And more...

## 🚀 Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Optional: Set Up API Keys
For enhanced features, set environment variables:

**VirusTotal API** (for malware scanning):
```bash
# Windows
set VIRUSTOTAL_API_KEY=your_api_key_here

# Linux/Mac
export VIRUSTOTAL_API_KEY=your_api_key_here
```

Get your API key from: https://www.virustotal.com/gui/my-apikey

**WHOIS API** (for domain info):
```bash
# Windows
set WHOIS_API_KEY=your_api_key_here

# Linux/Mac
export WHOIS_API_KEY=your_api_key_here
```

### 3. Run the Application
```bash
python app.py
```

Visit: `http://localhost:5000` in your browser

## 📊 Feature Details

### SSL Certificate Validation
Validates that websites use valid SSL certificates. Legitimate websites typically have proper SSL certificates from trusted CAs.

### Suspicious TLD Detection
Many phishing sites use newer, cheaper TLDs. This feature flags suspicious domain extensions.

### WHOIS Lookup
WHOIS data reveals domain registration information. Phishing domains often use:
- Private/hidden registrations
- Recent creation dates
- Proxy registration services

### VirusTotal Integration
Cross-references URLs against 90+ antivirus engines. Shows:
- **Malicious**: Flagged as malware/phishing
- **Suspicious**: Flagged by some engines
- **Undetected**: Not flagged (could be new threats)

## 📈 Analytics

### Dashboard Metrics
- **Total Scans**: Cumulative scan count
- **Legitimate Sites**: Count of verified legitimate sites
- **Phishing Sites**: Count of detected phishing sites
- **Detection Rate**: Percentage of phishing detections

### Charts
- **Doughnut Chart**: Legitimate vs Phishing ratio
- **Line Chart**: Cumulative trends over time

## 🔧 Configuration

### Sensitive Keyword Lists
Edit the suspicious keywords in `app.py`:
```python
suspicious_words = [
    "login", "verify", "account", "update", "secure",
    "bank", "paypal", "signin", "confirm", "password"
]
```

### URL Shorteners
Add/modify detected shorteners:
```python
shorteners = [
    "bit.ly", "tinyurl.com", "goo.gl", 
    "t.co", "ow.ly", "is.gd"
]
```

### Suspicious TLDs
Customize the list of suspicious TLDs:
```python
SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".tk", ".ml", ".ga", ".cf",
    # Add more as needed
]
```

## 📝 Database

The application stores scan history in memory (session-based). For production use, consider adding:
- SQLite database
- PostgreSQL integration
- Cloud storage (AWS S3, Google Cloud)

## 🔐 Security Considerations

1. **HTTPS Only**: Always use HTTPS in production
2. **API Key Protection**: Never commit API keys to version control
3. **Rate Limiting**: Implement rate limiting for production
4. **Input Validation**: All URLs are validated before scanning
5. **SSL Verification**: Be cautious with verify=False (used for research)

## 📱 Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🎨 Customization

### Dark Mode
Users can toggle dark mode, preference is saved to browser storage.

### Themes
Modify CSS variables in `templates/index.html`:
```css
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --danger-color: #dc3545;
}
```

## 📚 API Endpoints

### HTML Routes
- `GET /` - Home page with statistics
- `POST /predict` - Scan a URL

### JSON APIs
- `GET /api/stats` - Get statistics
- `GET /api/history` - Get scan history
- `GET /export-csv` - Download scan history as CSV

## 🐛 Troubleshooting

### SSL Certificate Errors
If SSL checking fails, the scan continues with a warning. Common issues:
- Self-signed certificates
- Certificate validation environment issues

### WHOIS Lookup Failure
Ensure `whois` command-line tool is installed:
```bash
# Windows: Install from https://www.nirsoft.net/utils/whois.html
# Linux: sudo apt-get install whois
# Mac: brew install whois
```

### VirusTotal Integration Not Working
- Check API key is set correctly
- Verify internet connection
- Check VirusTotal service status

## 📄 License

This project is for educational purposes.

## 🙏 Credits

- Machine Learning Model: scikit-learn
- Web Framework: Flask
- Charts: Chart.js
- Icons: Unicode/Emoji

## 📞 Support

For issues or feature requests, please refer to your course materials or instructor.

---

**Happy Phishing Hunting! 🔒**
=======
# Phishing_Detection
>>>>>>> 86db94e24def193481be4ecd20e4bc231e68ee0d
