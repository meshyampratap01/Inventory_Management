from pydantic import BaseModel, Field


class StockUpdateRequest(BaseModel):
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
