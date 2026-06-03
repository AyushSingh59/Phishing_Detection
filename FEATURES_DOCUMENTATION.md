# Enhanced Phishing Detection Features

## Overview
This document describes all the features extracted by the improved phishing detection engine. The model uses 30 features total, combining URL-based and domain-based analysis.

---

## URL-Based Features

### 1. **Having IP Address** (Index 0)
- **Values**: -1 (has IP), 1 (no IP)
- **Description**: Detects if URL uses IP address instead of domain name
- **Phishing Indicator**: IP addresses (e.g., 192.168.1.1) are common in phishing attacks
- **Example**: `http://192.168.1.100` vs `https://google.com`

### 2. **URL Length** (Index 1)
- **Values**: -1 (>75 chars), 0 (54-75), 1 (<54)
- **Description**: Analyzes overall URL length
- **Phishing Indicator**: Extremely long URLs often hide malicious domains or parameters
- **Example**: Short legitimate URLs typically <54 chars, phishing URLs often >75 chars

### 3. **URL Shortener Service** (Index 2)
- **Values**: -1 (uses shortener), 1 (no shortener)
- **Description**: Checks for URL shortening services (bit.ly, tinyurl, goo.gl, etc.)
- **Phishing Indicator**: Shorteners hide the true destination
- **Detected Services**: bit.ly, tinyurl.com, goo.gl, t.co, ow.ly, is.gd, buff.ly

### 4. **@ Symbol** (Index 3)
- **Values**: -1 (has @), 1 (no @)
- **Description**: Detects @ symbol in URL
- **Phishing Indicator**: URLs with @ symbol trick users (user@phishing.com appears legitimate)
- **Example**: `http://google.com@phishing.com`

### 5. **Double Slash Redirecting** (Index 4)
- **Values**: -1 (has //), 1 (no //)
- **Description**: Checks for // appearing after the protocol
- **Phishing Indicator**: `http://http://google.com` or `http:///google.com` indicates redirect tricks
- **Valid**: `https://www.google.com` (protocol-standard //)

### 6. **Prefix/Suffix with Hyphen** (Index 5)
- **Values**: -1 (has hyphen), 1 (no hyphen)
- **Description**: Detects hyphen (-) in domain name
- **Phishing Indicator**: `goog-le.com` mimics `google.com`
- **Note**: Legitimate domains can have hyphens, but suspicious registration practice

### 7. **Subdomains** (Index 6)
- **Values**: -1 (>2 dots), 0 (2 dots), 1 (≤1 dot)
- **Description**: Counts number of dots indicating subdomain depth
- **Phishing Indicator**: Too many subdomains suggest obfuscation
- **Examples**: 
  - `google.com` = 1 dot (legitimate)
  - `mail.google.com` = 2 dots (legitimate)
  - `fake.paypal.attacker.com` = 3+ dots (suspicious)

### 8. **HTTPS Protocol** (Index 7)
- **Values**: 1 (HTTPS), -1 (HTTP)
- **Description**: Checks for secure HTTPS protocol
- **Phishing Indicator**: HTTP sites (without SSL) are more likely phishing
- **Note**: HTTPS alone doesn't guarantee legitimacy (phishing sites now use HTTPS)

### 9. **Suspicious Keywords** (Index 8)
- **Values**: -1 (found), 1 (not found)
- **Description**: Detects phishing-related keywords in URL
- **Detected Keywords**: login, verify, account, update, secure, bank, paypal, signin, confirm, password, webscr
- **Example**: `https://secure-login-verify.com` triggers multiple keywords

### 10. **Dot Count in URL** (Index 9)
- **Values**: -1 (>6), 0 (4-6), 1 (<4)
- **Description**: Counts total dots in full URL (domain + path)
- **Phishing Indicator**: Excessive dots often indicate obfuscation
- **Example**: `https://google.com/search?q=test` = 3 dots (normal)

### 11. **Special Characters** (Index 10)
- **Values**: -1 (>7), 0 (3-7), 1 (≤3)
- **Description**: Counts suspicious special characters (@, !, #, $, %, ^, &, etc.)
- **Phishing Indicator**: Excessive special characters are suspicious
- **Tracked Chars**: @, !, #, $, %, ^, &, *, (, ), =, +, [, ], {, }, |, ;, :, ", ', <, >, ,, ?

### 12. **Port Number** (Index 11)
- **Values**: -1 (non-standard port), 1 (standard)
- **Description**: Checks for non-standard port numbers in URL
- **Phishing Indicator**: `http://google.com:8080` looks suspicious
- **Note**: Standard ports: 80 (HTTP), 443 (HTTPS)

### 13. **Digits in Domain Name** (Index 12)
- **Values**: -1 (has digits), 1 (no digits)
- **Description**: Detects numbers in main domain name
- **Phishing Indicator**: `g00gle.com` or `paypa1.com` mimic legitimate brands
- **Note**: Some legitimate domains have numbers

### 14. **Query Parameters** (Index 13)
- **Values**: -1 (>4), 0 (2-4), 1 (≤2)
- **Description**: Counts URL query parameters
- **Phishing Indicator**: Too many parameters can hide redirect targets
- **Example**: `?param1=val1&param2=val2&param3=val3&param4=val4` = 4 params

### 15. **URL Fragments/Anchors** (Index 14)
- **Values**: 1 (has fragment), -1 (no fragment)
- **Description**: Detects URL fragments (#something)
- **Phishing Indicator**: Fragments are often used to hide true destination
- **Example**: `http://phishing.com#https://google.com` - user might not notice

### 16. **Domain Age** (Index 15)
- **Values**: -1 (<30 days), 0 (30-180 days), 1 (>180 days)
- **Description**: Calculates domain age from WHOIS registration date
- **Phishing Indicator**: Very new domains are often phishing
- **Note**: Requires WHOIS data availability

### 17. **DNS Records Exist** (Index 16)
- **Values**: 1 (exists), -1 (not found), 0 (unavailable)
- **Description**: Checks if DNS 'A' records exist
- **Phishing Indicator**: Missing DNS records indicate fake domain
- **Technical**: Uses dnspython library for DNS lookup

### 18. **MX Records** (Index 17)
- **Values**: 1 (found), 0 (unavailable), -1 (none)
- **Description**: Counts mail server (MX) records for domain
- **Phishing Indicator**: Missing MX records often indicate fake domains
- **Note**: Legitimate email services need MX records

### 19. **Suspicious TLD** (Index 18)
- **Values**: -1 (suspicious), 1 (legitimate)
- **Description**: Detects suspicious top-level domains
- **Suspicious TLDs**: .xyz, .top, .tk, .ml, .ga, .cf, .click, .download, .review, .webcam, .date, .trade, .faith, .accountant, .win, .loan, .science
- **Reason**: These TLDs are frequently used for phishing and abuse

### 20. **Common TLD** (Index 19)
- **Values**: 1 (common), 0 (uncommon)
- **Description**: Checks if domain uses common TLD
- **Common TLDs**: .com, .org, .net, .edu, .gov, .co.uk, and country codes
- **Phishing Indicator**: Missing from common TLDs but has suspicious one

### 21. **Domain Length** (Index 20)
- **Values**: -1 (>40), 0 (20-40), 1 (<20)
- **Description**: Analyzes domain name length
- **Phishing Indicator**: Very long domains suggest obfuscation
- **Example**: `google.com` = 10 chars (normal), `supercalifragilisticexpialidocious.com` = 34 chars (suspicious)

### 22. **Path Length** (Index 21)
- **Values**: -1 (>50), 0 (10-50), 1 (<10)
- **Description**: Analyzes URL path component length
- **Phishing Indicator**: Very long paths often hide malicious redirects
- **Example**: `/search` = 7 chars (normal), `/long/path/to/phishing/page?params...` = 50+ (suspicious)

### 23. **WWW Prefix** (Index 22)
- **Values**: 1 (has www), 0 (no www)
- **Description**: Checks if domain starts with "www."
- **Phishing Indicator**: Legitimate domains commonly use www prefix
- **Note**: Not all legitimate sites use www

### 24. **Subdomain Count** (Index 23)
- **Values**: -1 (>1), 0 (1), 1 (0)
- **Description**: Counts number of subdomains
- **Phishing Indicator**: Multiple subdomains suggest complex obfuscation
- **Examples**:
  - `google.com` = 0 subdomains
  - `mail.google.com` = 1 subdomain
  - `ssl.mail.google.com` = 2 subdomains (suspicious)

---

## Domain-Based Features (24-30)

Indices 24-30 are reserved for additional domain-based analysis and future enhancements.

---

## Feature Value System

All features use a **-1, 0, 1** scale:
- **-1**: Strong phishing indicator (high risk)
- **0**: Neutral or uncertain indicator
- **1**: Strong legitimate indicator (low risk)

---

## Implementation Notes

1. **WHOIS Dependency**: Domain age requires the `python-whois` library
2. **DNS Dependency**: DNS checking requires the `dnspython` library
3. **Error Handling**: If external data unavailable, features default to 0
4. **Performance**: Domain lookups can be slow; consider caching
5. **Accuracy**: Features are engineered based on common phishing patterns

---

## Feature Correlation with Model

The ML model (Random Forest) analyzes these 30 features to predict:
- **1**: Legitimate Website
- **-1**: Phishing Website

Feature importance varies; some are weighted more heavily by the model based on training data.

---

## Testing the Features

To see extracted features for any URL:

```python
from app import extract_features
url = "https://suspicious-login-verify.com"
features = extract_features(url)
print(f"Extracted {len(features)} features: {features}")
```

---

## Future Enhancements

Potential features to add:
- Page content analysis (HTML/CSS patterns)
- SSL certificate issuer reputation
- IP geolocation
- Domain registrar reputation
- Historical abuse reports
- Similar domain detection
- Content-based machine learning
