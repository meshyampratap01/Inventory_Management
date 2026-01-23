from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    id: str
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    category: str
    override_threshold: Optional[int] = Field(None, ge=0)
    low_stock_alert_sent: Optional[bool] = Field(False)

    model_config = ConfigDict(extra="ignore")
