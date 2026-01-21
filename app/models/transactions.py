from datetime import datetime, UTC
import enum

from pydantic import BaseModel, Field


class TransactionReason(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"


class Transaction(BaseModel):
    id: str = Field(..., alias="_id")
    product_id: str = Field(..., alias="product_id")
    reason: TransactionReason
    quantity: int = Field(..., ge=0)
    performed_by: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"populate_by_name": True, "use_enum_values": True}

