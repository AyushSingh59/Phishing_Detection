import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        f"sqlite:///{INSTANCE_DIR / 'phishing.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")
    VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY", "")
    GOOGLE_SAFEBROWSING_KEY = os.getenv("GOOGLE_SAFEBROWSING_KEY", "")
    EXTERNAL_CACHE_TTL = int(os.getenv("EXTERNAL_CACHE_TTL", 60 * 60 * 12))
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "60 per minute")
    JSON_SORT_KEYS = False
