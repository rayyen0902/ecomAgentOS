"""Pydantic schemas for the health check endpoint."""

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Response model for GET /api/v1/health."""

    status: str = Field(..., description="Service status indicator.")
    version: str = Field(..., description="Application version.")
    timestamp: str = Field(..., description="UTC timestamp in ISO 8601 format.")
