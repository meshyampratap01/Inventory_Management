from fastapi import APIRouter, Depends

from app.dependencies import require_any_group
from app.dto.create_product_request import CreateProductRequest
from app.dto.stock_update_request import StockUpdateRequest
from app.models.user_group import UserGroup
from app.response.response import APIResponse
from app.services.product_service import ProductService

products_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@products_router.post("/", status_code=201, response_model=APIResponse)
def create_product_handler(
    req: CreateProductRequest,
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER)),
):
    data = product_service.create_product(req)
    return APIResponse(
        status_code=201, message="Product created successfully", data=data
    )


@products_router.get("/", status_code=200, response_model=APIResponse)
def get_products_handler(
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER, UserGroup.STAFF)),
    product_id: str | None = None,
):
    if product_id:
        data = product_service.get_product_by_id(product_id)
        return APIResponse(status_code=200, message="Product found", data=data)
    data = product_service.get_all_products()
    return APIResponse(status_code=200, message="Products found", data=data)


@products_router.patch("/stockin", status_code=200, response_model=APIResponse)
def stock_in_handler(
    req: StockUpdateRequest,
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER)),
):
    data = product_service.stock_in(req)
    return APIResponse(
        status_code=200, message="Product's stock updated successfully", data=data
    )


@products_router.patch("/stockout", status_code=200, response_model=APIResponse)
def stock_out_handler(
    req: StockUpdateRequest,
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER, UserGroup.STAFF)),
):
    data = product_service.stock_out(req)
    return APIResponse(
        status_code=200, message="Product's stock updated successfully", data=data
    )
