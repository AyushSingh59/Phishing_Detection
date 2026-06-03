import os
import pickle
import re
import socket
from urllib.parse import urlparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception:
    model = None

HIGH_RISK_KEYWORDS = [
    "login",
    "verify",
    "account",
    "update",
    "secure",
    "bank",
    "paypal",
    "signin",
    "confirm",
    "password",
    "ebay",
    "apple",
    "google",
    "amazon"
]


def normalize_url(url):
    url = url.strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url
    return url


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.scheme in ("http", "https") and parsed.netloc)


def _domain_from_url(parsed):
    domain = parsed.netloc.lower()
    if ":" in domain:
        domain = domain.split(":" )[0]
    return domain


def count_special_characters(url):
    suspicious_chars = "@!#$%^&*()=+[]{}|;:\\'\"<>,?"
    return sum(url.count(ch) for ch in suspicious_chars)


def count_query_parameters(parsed):
    return len(parsed.query.split("&")) if parsed.query else 0


def count_fragments(parsed):
    return 1 if parsed.fragment else 0


def _safe_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def extract_features(url):
    if not url:
        return [0] * 30

    parsed = urlparse(url)
    domain = _domain_from_url(parsed)
    path = parsed.path or ""
    query_count = count_query_parameters(parsed)
    fragment_flag = count_fragments(parsed)

    features = []
    # 1. IP address in domain
    try:
        socket.inet_aton(domain)
        features.append(-1)
    except Exception:
        features.append(1)

    # 2. URL length
    if len(url) < 54:
        features.append(1)
    elif len(url) <= 75:
        features.append(0)
    else:
        features.append(-1)

    # 3. Shortening service
    shorteners = [
        "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "short.link", "buff.ly"
    ]
    features.append(-1 if any(shortener in domain for shortener in shorteners) else 1)

    # 4. @ symbol
    features.append(-1 if "@" in url else 1)

    # 5. Double slash redirecting
    features.append(-1 if "//" in url[8:] else 1)

    # 6. Prefix/Suffix hyphen in domain
    features.append(-1 if "-" in domain else 1)

    # 7. Subdomain count
    dots = domain.count(".")
    if dots <= 1:
        features.append(1)
    elif dots == 2:
        features.append(0)
    else:
        features.append(-1)

    # 8. HTTPS usage
    features.append(1 if url.lower().startswith("https://") else -1)

    # 9. Suspicious keywords
    features.append(-1 if any(word in url.lower() for word in HIGH_RISK_KEYWORDS) else 1)

    # 10. Number of dots
    if url.count(".") < 4:
        features.append(1)
    elif url.count(".") <= 6:
        features.append(0)
    else:
        features.append(-1)

    # 11. Special characters
    special_count = count_special_characters(url)
    if special_count <= 3:
        features.append(1)
    elif special_count <= 7:
        features.append(0)
    else:
        features.append(-1)

    # 12. Port in domain
    features.append(-1 if ":" in parsed.netloc else 1)

    # 13. Digits in domain
    features.append(-1 if any(char.isdigit() for char in domain.split(".")[0]) else 1)

    # 14. Query parameters
    if query_count <= 2:
        features.append(1)
    elif query_count <= 4:
        features.append(0)
    else:
        features.append(-1)

    # 15. Fragment usage
    features.append(1 if fragment_flag else -1)

    # 16. Domain length
    if len(domain) < 20:
        features.append(1)
    elif len(domain) <= 40:
        features.append(0)
    else:
        features.append(-1)

    # 17. Path length
    if len(path) < 10:
        features.append(1)
    elif len(path) <= 50:
        features.append(0)
    else:
        features.append(-1)

    # 18. www prefix
    features.append(1 if domain.startswith("www.") else 0)

    # 19. Subdomain count more precise
    subdomain_count = max(0, domain.count(".") - 1)
    if subdomain_count == 0:
        features.append(1)
    elif subdomain_count == 1:
        features.append(0)
    else:
        features.append(-1)

    # 20. Suspicious TLDs
    suspicious_tlds = [
        ".xyz", ".top", ".tk", ".ml", ".ga", ".cf", ".click",
        ".download", ".review", ".webcam", ".date", ".trade", ".faith", ".accountant",
        ".win", ".loan", ".science"
    ]
    features.append(-1 if any(domain.endswith(tld) for tld in suspicious_tlds) else 1)

    # 21. Common TLD
    common_tlds = [
        ".com", ".org", ".net", ".edu", ".gov", ".co.uk", ".de", ".fr", ".it", ".ru", ".br", ".in", ".au"
    ]
    features.append(1 if any(domain.endswith(tld) for tld in common_tlds) else 0)

    # 22. Digit count in URL
    digits = sum(ch.isdigit() for ch in url)
    if digits < 3:
        features.append(1)
    elif digits <= 6:
        features.append(0)
    else:
        features.append(-1)

    # 23. URL path depth
    features.append(-1 if path.count("/") > 3 else 1)

    # 24. Length of hostname
    features.append(1 if len(domain) <= 20 else -1)

    # 25. Percentage of letters
    letters = sum(ch.isalpha() for ch in url)
    ratio = letters / len(url) if len(url) > 0 else 0
    features.append(1 if ratio > 0.5 else -1)

    # 26. Numeric ratio
    numbers = sum(ch.isdigit() for ch in url)
    features.append(-1 if numbers / len(url) > 0.2 else 1)

    # 27. Domain entropy proxy: repeated characters
    features.append(-1 if any(domain.count(ch) > 4 for ch in set(domain)) else 1)

    # 28. URL contains login keywords
    features.append(-1 if any(word in domain for word in ["login", "signin", "secure", "account"]) else 1)

    # 29. Relative path usage
    features.append(-1 if path.endswith(".php") or path.endswith(".exe") else 1)

    # 30. Empty fragment indicator
    features.append(1 if not fragment_flag else -1)

    while len(features) < 30:
        features.append(0)

    return features


def _safe_prediction(prediction, probability):
    result = "Legitimate" if prediction == 1 else "Phishing"
    confidence = round(max(probability) * 100, 2)
    return result, confidence


def predict_url(url):
    if model is None:
        return {
            "prediction": "Unknown",
            "confidence": 0,
            "probability": [0, 0],
            "raw": None,
            "features": []
        }

    normalized = normalize_url(url)
    features = extract_features(normalized)
    raw = model.predict([features])[0]
    probability = model.predict_proba([features])[0]
    result, confidence = _safe_prediction(raw, probability)

    return {
        "prediction": result,
        "confidence": confidence,
        "probability": probability.tolist(),
        "raw": int(raw),
        "features": features
    }
