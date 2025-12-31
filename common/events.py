"""Shared event models for all microservices."""
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Any, Optional


class RawEvent(BaseModel):
    """Raw data ingested from external sources."""
    source: str  # "nsdc", "opensanctions", "whois", "onchain"
    subject_id: str
    subject_type: str  # "person", "company", "url", "address"
    raw_data: dict[str, Any]
    ingested_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "nsdc",
                "subject_id": "person_123",
                "subject_type": "person",
                "raw_data": {"name": "John Doe", "country": "RU"},
                "ingested_at": "2025-12-31T16:00:00Z"
            }
        }


class FactorSignal(BaseModel):
    """Single factor score for risk assessment."""
    subject_type: str
    subject_id: str
    factor: str  # "sanctions", "rf_links", "site_risk", "predictive_risk", etc
    raw_score: float  # 0..1
    bucket: str  # "HIGH", "MEDIUM", "LOW"
    features: dict[str, Any]
    model_version: str
    computed_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject_type": "person",
                "subject_id": "person_123",
                "factor": "sanctions",
                "raw_score": 0.95,
                "bucket": "HIGH",
                "features": {"lists": ["NSDC"], "country": "RU"},
                "model_version": "sanctions_v1",
                "computed_at": "2025-12-31T16:00:00Z"
            }
        }


class AggregateEvent(BaseModel):
    """Combined risk score from all factors."""
    subject_id: str
    subject_type: str
    aggregate_score: float  # 0..1
    bucket: str  # "HIGH", "MEDIUM", "LOW"
    factors: dict[str, float]  # {"sanctions": 0.95, "rf_links": 0.5, ...}
    explain: dict[str, Any]  # JSON explanation
    computed_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject_id": "person_123",
                "subject_type": "person",
                "aggregate_score": 0.8,
                "bucket": "HIGH",
                "factors": {"sanctions": 0.95, "rf_links": 0.6},
                "explain": {"weights": {"sanctions": 0.7, "rf_links": 0.3}},
                "computed_at": "2025-12-31T16:00:00Z"
            }
        }
