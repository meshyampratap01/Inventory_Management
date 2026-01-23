from fastapi import APIRouter, Depends

from app.dependencies import require_any_group
from app.dto.create_product_request import CreateProductRequest
from app.dto.stock_update_request import StockUpdateRequest
from app.models.user_group import UserGroup
from app.services.product_service import ProductService

products_router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@products_router.post("/", status_code=201)
def create_product_handler(
    req: CreateProductRequest,
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER)),
):
    return product_service.create_product(req)


@products_router.get("/", status_code=200)
def get_products_handler(
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER, UserGroup.STAFF)),
    product_id: str | None = None,
):
    if product_id:
        return product_service.get_product_by_id(product_id)
    return product_service.get_all_products()


@products_router.patch("/stockin", status_code=200)
def stock_in_handler(
    req: StockUpdateRequest,
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER)),
):
    return product_service.stock_in(req)


@products_router.patch("/stockout", status_code=200)
def stock_out_handler(
    req: StockUpdateRequest,
    product_service: ProductService = Depends(ProductService),
    _=Depends(require_any_group(UserGroup.MANAGER, UserGroup.STAFF)),
):
    return product_service.stock_out(req)
