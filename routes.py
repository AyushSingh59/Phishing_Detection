import json
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from models import db, ScanRecord
from ml_utils import normalize_url, is_valid_url, predict_url
from threat_intel import get_domain_info, calculate_reputation
from utils import build_scan_steps

main_bp = Blueprint("main", __name__)


def _scan_category(risk_score):
    if risk_score <= 33:
        return "Safe"
    if risk_score <= 66:
        return "Suspicious"
    return "Dangerous"


def _merge_detection(url, prediction, domain_info):
    reasons = []
    risk_score = 100 - prediction.get("confidence", 0)

    if not domain_info.get("reachable"):
        reasons.append("Website unreachable or DNS lookup failed")
        risk_score += 10

    if not domain_info.get("ssl_valid"):
        reasons.append("Invalid or missing SSL certificate")
        risk_score += 18

    if domain_info.get("whois_age") is not None and domain_info.get("whois_age") < 30:
        reasons.append("Very new domain registration")
        risk_score += 12

    vt_info = domain_info.get("virustotal")
    if vt_info and vt_info.get("malicious", 0) > 0:
        reasons.append("VirusTotal flagged the URL as malicious")
        risk_score += 30

    gsb_info = domain_info.get("safe_browsing")
    if gsb_info and gsb_info.get("matches"):
        reasons.append("Google Safe Browsing reported the URL as unsafe")
        risk_score += 30

    if prediction.get("raw") == -1:
        reasons.append("ML model classified URL as phishing")
        risk_score += 10

    for keyword in ["login", "verify", "secure", "account", "password", "bank", "paypal"]:
        if keyword in url.lower():
            reasons.append(f"Suspicious keyword present: {keyword}")
            break

    risk_score = min(max(round(risk_score, 2), 0), 100)
    category = _scan_category(risk_score)
    final_result = "Phishing" if risk_score >= 50 else "Legitimate"
    if risk_score >= 75:
        final_result = "Dangerous"

    return {
        "result": final_result,
        "confidence": round(prediction.get("confidence", 0), 2),
        "risk_score": risk_score,
        "category": category,
        "reasons": reasons,
        "prediction": prediction,
    }


def _get_history(limit=100):
    recent = ScanRecord.query.order_by(ScanRecord.id.desc()).limit(limit).all()
    return [record.to_dict() for record in recent]


def _build_stats():
    total = ScanRecord.query.count()
    legitimate = ScanRecord.query.filter(ScanRecord.result.ilike("%Legitimate%")) .count()
    phishing = ScanRecord.query.filter(ScanRecord.result.ilike("%Phishing%")) .count()
    dangerous = ScanRecord.query.filter(ScanRecord.result.ilike("%Dangerous%")) .count()
    bad_count = phishing + dangerous
    return {
        "total": total,
        "legitimate": legitimate,
        "phishing": phishing,
        "dangerous": dangerous,
        "safe_percentage": round((legitimate / total * 100), 2) if total else 0,
        "danger_percentage": round((bad_count / total * 100), 2) if total else 0,
    }


@main_bp.route("/")
def home():
    stats = _build_stats()

    return render_template(
        "index.html",
        history=_get_history(100),
        stats=stats,
        domain_info=None,
        scan=None,
        steps=build_scan_steps(),
        error_message=None,
    )


@main_bp.route("/scan", methods=["POST"])
def scan():
    original_url = request.form.get("url", "").strip()
    if not original_url:
        return home()

    url = normalize_url(original_url)
    if not is_valid_url(url):
        return render_template(
            "index.html",
            history=_get_history(100),
            stats=_build_stats(),
            domain_info=None,
            scan=None,
            steps=build_scan_steps(),
            error_message="Enter a valid https:// or http:// URL.",
        )

    prediction = predict_url(url)
    domain_info = get_domain_info(url)
    reputation_score, reputation_notes = calculate_reputation(domain_info, domain_info.get("virustotal"), domain_info.get("safe_browsing"))
    final = _merge_detection(url, prediction, domain_info)
    final["reputation_score"] = reputation_score
    final["reputation_notes"] = reputation_notes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        record = ScanRecord(
            url=url,
            result=final["result"],
            confidence=final["confidence"],
            risk_score=final["risk_score"],
            timestamp=timestamp,
            domain_info=json.dumps(domain_info),
        )
        db.session.add(record)
        db.session.commit()
    except Exception:
        db.session.rollback()

    stats = _build_stats()

    return render_template(
        "index.html",
        history=_get_history(100),
        stats=stats,
        domain_info=domain_info,
        scan=final,
        steps=build_scan_steps(),
        error_message=None,
    )
