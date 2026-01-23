from fastapi import APIRouter, Depends, status

from app.dependencies import require_any_group
from app.dto.category_request import CreateCategoryRequest, UpdateCategoryRequest
from app.models.user_group import UserGroup
from app.response.response import APIResponse
from app.services.category_service import CategoryService

category_router = APIRouter(
    prefix="/category",
    tags=["category"],
    dependencies=[Depends(require_any_group(UserGroup.MANAGER))],
)


@category_router.post(
    "/", response_model=APIResponse, status_code=status.HTTP_201_CREATED
)
def create_category_handler(
    req: CreateCategoryRequest,
    category_service: CategoryService = Depends(CategoryService),
):
    data = category_service.create_category(req)
    return APIResponse(
        status_code=201, message="Category created successfully", data=data
    )


@category_router.get(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
def get_category_handler(
    category_service: CategoryService = Depends(CategoryService),
    name: str | None = None,
):
    if name:
        data = category_service.get_category_by_name(name)
        return APIResponse(status_code=200, message="Category found", data=data)
    data = category_service.get_all_category()
    return APIResponse(status_code=200, message="Categories found", data=data)


@category_router.patch(
    "/{name}", status_code=status.HTTP_200_OK, response_model=APIResponse
)
def update_threshold_handler(
    req: UpdateCategoryRequest,
    name: str,
    category_service: CategoryService = Depends(CategoryService),
):
    category_service.update_threshold(req, name)
    return APIResponse(status_code=200, message="Category updated successfully")
