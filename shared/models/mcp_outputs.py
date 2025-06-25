from pydantic import BaseModel, ConfigDict


class PsychologyResponse(BaseModel):
    """Response schema for the Psychology MCP."""

    result: str | None = None

    model_config = ConfigDict(extra="forbid")


class OncologyKBResponse(BaseModel):
    """Response schema for the OncologyKB MCP."""

    answer: str | None = None
    citations: list[str] | None = None
    evidence_level: str | None = None
    update_timestamp: str | None = None

    model_config = ConfigDict(extra="forbid")


class RadiologyResponse(BaseModel):
    """Response schema for the Radiology MCP."""

    findings: str | None = None
    impression: str | None = None
    follow_up: str | None = None
    modalities_detected: list[str] | None = None
    uncertainty_flags: list[str] | None = None

    model_config = ConfigDict(extra="forbid")


class VisionResponse(BaseModel):
    """Response schema for the Vision MCP."""

    labels: list[dict] | None = None
    bbox: list | None = None
    nsfw_flag: bool | None = None

    model_config = ConfigDict(extra="forbid")
