from pydantic import BaseModel


class CategoryResponse(BaseModel):
    name: str
    description: str | None = None
    default_threshold: int
