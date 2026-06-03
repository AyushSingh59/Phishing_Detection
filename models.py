import json
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ScanRecord(db.Model):
    __tablename__ = "scan_records"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(64), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    risk_score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.String(64), nullable=False)
    domain_info = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "result": self.result,
            "confidence": self.confidence,
            "risk_score": self.risk_score,
            "timestamp": self.timestamp,
            "domain_info": json.loads(self.domain_info) if self.domain_info else None,
        }
