from pydantic import BaseModel, Field


class CorrelationPayload(BaseModel):
    source: str = Field(description="Producer name, e.g. windows or ubuntu")
    ts: float = Field(description="Unix epoch timestamp")
    state: dict = Field(default_factory=dict, description="Primary metrics")
    d_state: dict = Field(default_factory=dict, description="First derivatives")
    anomaly_score: float = Field(ge=0.0, le=1.0, default=0.0)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

