from decimal import Decimal
from typing import List
from botocore.exceptions import ClientError
from fastapi import Depends, status
from app.dependencies import get_ddb_table
from app.models.products import Product
from app.app_exception.app_exception import AppException


class ProductRepository:
    def __init__(self, table=Depends(get_ddb_table)):
        self.table = table
        self.ddb_client = table.meta.client

    def save_product(self, product: Product):
        try:
            self.ddb_client.transact_write_items(
                TransactItems=[
                    {
                        "Put": {
                            "TableName": self.table.name,
                            "Item": {
                                "pk": f"PRODUCT#{product.id}",
                                "sk": "META",
                                "id": product.id,
                                "name": product.name,
                                "price": Decimal(str(product.price)),
                                "quantity": product.quantity,
                                "category": product.category,
                                "override_threshold": product.override_threshold,
                            },
                            "ConditionExpression": "attribute_not_exists(pk)",
                        }
                    },
                    {
                        "Put": {
                            "TableName": self.table.name,
                            "Item": {
                                "pk": "PRODUCTS",
                                "sk": f"PRODUCT#{product.id}",
                                "id": product.id,
                                "name": product.name,
                                "price": Decimal(str(product.price)),
                                "quantity": product.quantity,
                                "category": product.category,
                            },
                        }
                    },
                ]
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "TransactionCanceledException":
                raise AppException(
                    message="Product already exists",
                    status_code=409,
                    error_code="PRODUCT_ALREADY_EXISTS",
                )

            raise AppException(
                message="Failed to save product",
                status_code=500,
                error_code="DATABASE_ERROR",
                details=e.response,
            )

    def get_all_products(self) -> List[Product]:
        response = self.table.query(
            KeyConditionExpression="pk = :pk",
            ExpressionAttributeValues={":pk": "PRODUCTS"},
        )
        items = response["Items"]
        return [Product(**item) for item in items]

    def get_product_by_id(self, product_id: str) -> Product:
        response = self.table.get_item(
            Key={
                "pk": f"PRODUCT#{product_id}",
                "sk": "META",
            }
        )
        item = response.get("Item")
        if item is None:
            raise AppException(
                message="Product not found",
                error_code="PRODUCT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
                details={"product_id": product_id},
            )
        return Product(**item)

    def stock_in(self, product_id: str, quantity: int):
        try:
            self.ddb_client.transact_write_items(
                TransactItems=[
                    {
                        "Update": {
                            "TableName": self.table.name,
                            "Key": {
                                "pk": f"PRODUCT#{product_id}",
                                "sk": "META",
                            },
                            "UpdateExpression": "ADD quantity :q",
                            "ExpressionAttributeValues": {
                                ":q": Decimal(str(quantity)),
                            },
                            "ConditionExpression": "attribute_exists(pk)",
                        }
                    },
                    {
                        "Update": {
                            "TableName": self.table.name,
                            "Key": {
                                "pk": "PRODUCTS",
                                "sk": f"PRODUCT#{product_id}",
                            },
                            "UpdateExpression": "ADD quantity :q",
                            "ExpressionAttributeValues": {
                                ":q": Decimal(str(quantity)),
                            },
                        }
                    },
                ]
            )

        except ClientError as e:
            raise AppException(
                message="Failed to stock in",
                status_code=500,
                error_code="STOCK_IN_FAILED",
                details=e.response,
            )

    def stock_out(self, product_id: str, quantity: int):
        try:
            self.ddb_client.transact_write_items(
                TransactItems=[
                    {
                        "Update": {
                            "TableName": self.table.name,
                            "Key": {
                                "pk": f"PRODUCT#{product_id}",
                                "sk": "META",
                            },
                            "UpdateExpression": "ADD quantity :neg_q",
                            "ConditionExpression": "quantity >= :q",
                            "ExpressionAttributeValues": {
                                ":neg_q": Decimal(str(-quantity)),
                                ":q": Decimal(str(quantity)),
                            },
                        }
                    },
                    {
                        "Update": {
                            "TableName": self.table.name,
                            "Key": {
                                "pk": "PRODUCTS",
                                "sk": f"PRODUCT#{product_id}",
                            },
                            "UpdateExpression": "ADD quantity :neg_q",
                            "ExpressionAttributeValues": {
                                ":neg_q": Decimal(str(-quantity)),
                            },
                        }
                    },
                ]
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "TransactionCanceledException":
                raise AppException(
                    message="Insufficient stock",
                    status_code=400,
                    error_code="INSUFFICIENT_STOCK",
                )

            raise AppException(
                message="Failed to stock out",
                status_code=500,
                error_code="STOCK_OUT_FAILED",
                details=e.response,
            )
