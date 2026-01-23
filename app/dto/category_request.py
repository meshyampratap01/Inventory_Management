from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


CATEGORY_NAME_REGEX = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9 _-]{0,48}[A-Za-z0-9])$")


class CreateCategoryRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Category name (letters, numbers, space, -, _)",
    )
    default_threshold: int = Field(..., ge=0)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not CATEGORY_NAME_REGEX.match(value):
            raise ValueError(
                "Category name must contain only letters, numbers, spaces, '-' or '_' "
                "and must start and end with a letter or number"
            )

        # prevent numeric-only names
        if value.isdigit():
            raise ValueError("Category name cannot be only numbers")

        # normalize spacing
        value = re.sub(r"\s+", " ", value)

        return value


class UpdateCategoryRequest(BaseModel):
    default_threshold: Optional[int] = Field(None, ge=0)
    description: Optional[str] = None
