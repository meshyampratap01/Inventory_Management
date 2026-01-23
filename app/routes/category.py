from fastapi import APIRouter, Depends, status

from app.dependencies import require_any_group
from app.dto.category_request import CreateCategoryRequest, UpdateCategoryRequest
from app.dto.category_response import CategoryResponse
from app.models.user_group import UserGroup
from app.services.category_service import CategoryService

category_router = APIRouter(
    prefix="/category",
    tags=["category"],
    dependencies=[Depends(require_any_group(UserGroup.MANAGER))],
)


@category_router.post(
    "/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED
)
def create_category_handler(
    req: CreateCategoryRequest,
    category_service: CategoryService = Depends(CategoryService),
):
    return category_service.create_category(req)


@category_router.get(
    "/",
    response_model=CategoryResponse | list[CategoryResponse],
    status_code=status.HTTP_200_OK,
)
def get_category_handler(
    category_service: CategoryService = Depends(CategoryService),
    name: str | None = None,
):
    if name:
        return category_service.get_category_by_name(name)
    return category_service.get_all_category()


@category_router.patch("/{name}", status_code=status.HTTP_200_OK)
def update_threshold_handler(
    req: UpdateCategoryRequest,
    name: str,
    category_service: CategoryService = Depends(CategoryService),
):
    return category_service.update_threshold(req, name)
