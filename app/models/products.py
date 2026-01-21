from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(..., alias="_id")
    name: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    threshold_quantity: int = Field(..., ge=0)

    model_config = {"populate_by_name": True}
