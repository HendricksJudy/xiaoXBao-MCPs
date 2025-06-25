from pydantic import BaseModel, ConfigDict


class PsychologyResponse(BaseModel):
    """Response schema for the Psychology MCP."""

    result: str | None = None

    model_config = ConfigDict(extra="forbid")


class OncologyKBResponse(BaseModel):
    """Response schema for the OncologyKB MCP."""

    result: str | None = None

    model_config = ConfigDict(extra="forbid")


class RadiologyResponse(BaseModel):
    """Response schema for the Radiology MCP."""

    result: str | None = None

    model_config = ConfigDict(extra="forbid")


class VisionResponse(BaseModel):
    """Response schema for the Vision MCP."""

    result: str | None = None

    model_config = ConfigDict(extra="forbid")
