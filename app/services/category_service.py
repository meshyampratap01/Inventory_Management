from fastapi import Depends, status

from app.app_exception.app_exception import AppException
from app.dto.category_request import CreateCategoryRequest, UpdateCategoryRequest
from app.dto.category_response import CategoryResponse
from app.repository.category_repository import CategoryRepository


class CategoryService:
    def __init__(
        self,
        category_repository: CategoryRepository = Depends(),
    ):
        self.category_repository = category_repository

    def create_category(self, req: CreateCategoryRequest) -> CategoryResponse:
        existing = self.category_repository.get_category(req.name)
        if existing:
            raise AppException(
                message=f"Category {req.name} already exists",
                error_code="CATEGORY_ALREADY_EXISTS",
                status_code=status.HTTP_409_CONFLICT,
            )

        self.category_repository.create_category(req)

        return CategoryResponse(
            name=req.name,
            description=req.description,
            default_threshold=req.default_threshold,
        )

    def get_category_by_name(self, name: str) -> CategoryResponse:
        category = self.category_repository.get_category(name)
        if not category:
            raise AppException(
                message=f"Category {name} not found",
                error_code="CATEGORY_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return CategoryResponse(
            name=name,
            description=category.description,
            default_threshold=category.default_threshold,
        )

    def get_all_category(self) -> list[CategoryResponse]:
        categories = self.category_repository.get_all_categories()
        return [
            CategoryResponse(
                name=category.name,
                description=category.description,
                default_threshold=category.default_threshold,
            )
            for category in categories
        ]

    def update_threshold(self, req: UpdateCategoryRequest, name):
        self.category_repository.update_category(name, req)
