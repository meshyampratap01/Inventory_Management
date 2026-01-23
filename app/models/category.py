from pydantic import BaseModel, ConfigDict, Field


class Category(BaseModel):
    name: str = Field(..., min_length=1)
    default_threshold: int = Field(..., ge=0)
    description: str | None

    model_config = ConfigDict(extra="ignore")
