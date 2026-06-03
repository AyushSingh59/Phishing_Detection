import os
import time
import socket
import ssl
import json
from urllib.parse import urlparse

try:
    import whois
except ImportError:
    whois = None

try:
    import dns.resolver
except ImportError:
    dns = None

import requests

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
GOOGLE_SAFEBROWSING_KEY = os.getenv("GOOGLE_SAFEBROWSING_KEY", "")
CACHE_TTL = int(os.getenv("EXTERNAL_CACHE_TTL", 60 * 60 * 12))

_vt_cache = {}
_gsb_cache = {}


def _normalize_domain(netloc):
    domain = netloc.lower()
    if ":" in domain:
        domain = domain.split(":")[0]
    return domain


def _safe_get_json(response):
    try:
        return response.json()
    except Exception:
        return {}


def check_dns_records(url):
    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc)
    try:
        if dns is not None:
            dns.resolver.resolve(domain, "A", lifetime=5)
        else:
            socket.gethostbyname(domain)
        return True
    except Exception:
        return False


def get_domain_age(url):
    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc)
    if whois is None:
        return None
    try:
        record = whois.whois(domain)
        creation = record.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        if creation:
            age = (time.time() - creation.timestamp()) / 86400
            return int(age)
    except Exception:
        return None
    return None


def check_ssl_certificate(url):
    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc)
    data = {"valid": False, "issuer": None, "subject": None, "error": None}
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=6) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                data["valid"] = True
                issuer = dict(x[0] for x in cert.get("issuer", []))
                subject = dict(x[0] for x in cert.get("subject", []))
                data["issuer"] = issuer.get("organizationName") or issuer.get("commonName")
                data["subject"] = subject.get("commonName")
                data["expires"] = cert.get("notAfter")
    except Exception as exc:
        data["error"] = str(exc)
    return data


def get_whois_data(url):
    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc)
    if whois is None:
        return {"found": False, "error": "python-whois not installed"}
    try:
        record = whois.whois(domain)
        raw = str(record)
        privacy = "privacy" in raw.lower() or "private" in raw.lower()
        creation = record.creation_date
        if isinstance(creation, list):
            creation = creation[0]
        return {
            "found": bool(raw.strip()),
            "creation_date": creation.isoformat() if creation else None,
            "private_registration": privacy,
            "registrar": getattr(record, "registrar", None),
            "name_servers": getattr(record, "name_servers", None)
        }
    except Exception as exc:
        return {"found": False, "error": str(exc)}


def check_virustotal(url):
    if not VIRUSTOTAL_API_KEY:
        return None
    now = time.time()
    cached = _vt_cache.get(url)
    if cached and now - cached["ts"] < CACHE_TTL:
        return cached["data"]
    try:
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        response = requests.post(
            "https://www.virustotal.com/api/v3/urls",
            headers=headers,
            data={"url": url},
            timeout=10,
        )
        if response.status_code in (200, 201):
            data = _safe_get_json(response)
            scan_id = data.get("data", {}).get("id")
            if scan_id:
                analysis = requests.get(
                    f"https://www.virustotal.com/api/v3/analyses/{scan_id}",
                    headers=headers,
                    timeout=10,
                )
                analysis_json = _safe_get_json(analysis)
                stats = analysis_json.get("data", {}).get("attributes", {}).get("stats", {})
                result = {
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "undetected": stats.get("undetected", 0),
                    "total": sum(stats.values()) if stats else 0,
                }
                _vt_cache[url] = {"ts": now, "data": result}
                return result
    except Exception:
        pass
    return None


def check_google_safe_browsing(url):
    if not GOOGLE_SAFEBROWSING_KEY:
        return None
    now = time.time()
    cached = _gsb_cache.get(url)
    if cached and now - cached["ts"] < CACHE_TTL:
        return cached["data"]
    try:
        endpoint = (
            f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFEBROWSING_KEY}"
        )
        payload = {
            "client": {"clientId": "phishing-detector", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION",
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}],
            },
        }
        response = requests.post(endpoint, json=payload, timeout=10)
        data = _safe_get_json(response)
        matches = data.get("matches")
        result = {"matches": bool(matches), "details": matches or []}
        _gsb_cache[url] = {"ts": now, "data": result}
        return result
    except Exception:
        return None


def calculate_reputation(domain_info, vt_info, gsb_info):
    score = 100
    notes = []
    if domain_info.get("ssl_valid") is False:
        score -= 25
        notes.append("Missing or invalid SSL certificate")
    if domain_info.get("dns_ok") is False:
        score -= 15
        notes.append("DNS lookup failed")
    if domain_info.get("whois_age") is not None and domain_info.get("whois_age") < 60:
        score -= 15
        notes.append("New domain registration")
    if vt_info is not None and vt_info.get("malicious", 0) > 0:
        score -= 35
        notes.append("VirusTotal detected malicious engines")
    if gsb_info is not None and gsb_info.get("matches"):
        score -= 35
        notes.append("Google Safe Browsing flagged the URL")
    return max(0, score), notes


def get_domain_info(url):
    parsed = urlparse(url)
    domain = _normalize_domain(parsed.netloc)
    if not domain:
        return {
            "domain": None,
            "ip_address": None,
            "reachable": False,
            "ssl_valid": False,
            "ssl_details": None,
            "whois": None,
            "whois_age": None,
            "dns_ok": False,
            "virustotal": None,
            "safe_browsing": None,
        }
    ip_address = None
    reachable = False
    try:
        ip_address = socket.gethostbyname(domain)
        reachable = True
    except Exception:
        reachable = False

    ssl_info = check_ssl_certificate(url)
    whois_data = get_whois_data(url)
    domain_age = get_domain_age(url)
    dns_ok = check_dns_records(url)
    vt_info = check_virustotal(url)
    gsb_info = check_google_safe_browsing(url)

    return {
        "domain": domain,
        "ip_address": ip_address,
        "reachable": reachable,
        "ssl_valid": ssl_info.get("valid", False),
        "ssl_details": ssl_info,
        "whois": whois_data,
        "whois_age": domain_age,
        "dns_ok": dns_ok,
        "virustotal": vt_info,
        "safe_browsing": gsb_info,
    }
