from pydantic import BaseModel, Field
from typing import Optional


class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    category: str = Field(..., min_length=1)
    override_threshold: Optional[int] = Field(None, ge=0)
