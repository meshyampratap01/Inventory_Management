from typing import List
import uuid

from fastapi import Depends, status

from app.app_exception.app_exception import AppException
from app.dto.create_product_request import CreateProductRequest
from app.dto.stock_update_request import StockUpdateRequest
from app.models.products import Product
from app.repository.category_repository import CategoryRepository
from app.repository.product_repository import ProductRepository
from app.sns_event_publisher.sns_event_publisher import SNSEventPublisher


class ProductService:
    def __init__(
        self,
        product_repo: ProductRepository = Depends(ProductRepository),
        category_repo: CategoryRepository = Depends(CategoryRepository),
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo

    def _is_low_stock(self, product: Product, category) -> bool:
        effective_threshold = (
            product.override_threshold
            if product.override_threshold is not None
            else category.default_threshold
        )

        return product.quantity <= effective_threshold

    def create_product(self, req: CreateProductRequest):
        _ = self.category_repo.get_category(req.category)
        product_id = str(uuid.uuid4())

        product = Product(
            id=product_id,
            name=req.name,
            price=req.price,
            quantity=req.quantity,
            category=req.category,
            override_threshold=req.override_threshold,
        )

        self.product_repo.save_product(product)

        return product

    def get_all_products(self) -> List[Product]:
        return self.product_repo.get_all_products()

    def get_product_by_id(self, product_id: str) -> Product:
        return self.product_repo.get_product_by_id(product_id)

    def stock_in(self, req: StockUpdateRequest):
        product_id = req.product_id
        quantity = req.quantity
        return self.product_repo.stock_in(product_id, quantity)

    def stock_out(self, req: StockUpdateRequest):
        product_id = req.product_id
        quantity = req.quantity
        product = self.product_repo.get_product_by_id(product_id)
        category = self.category_repo.get_category(product.category)
        if quantity > product.quantity:
            raise AppException(
                message=f"Insufficient stock for product {product_id}",
                error_code="INSUFFICIENT_STOCK",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"available_stock": product.quantity},
            )

        default_threshold = category.default_threshold

        self.product_repo.stock_out(product_id, quantity)

        if self._is_low_stock(product, category):
            print("is low stock")
            sns_publisher = SNSEventPublisher()
            payload = {
                "event_type": "LOW_STOCK",
                "product_id": product_id,
                "product_name": product.name,
                "category": product.category,
                "current_quantity": product.quantity,
                "threshold": default_threshold,
                "manager_email": "singhshyampratap900@gmail.com",
            }
            sns_publisher.publish_event(payload)
