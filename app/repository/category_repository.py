from botocore.exceptions import ClientError
from datetime import datetime, timezone
from fastapi import Depends, status

from app.app_exception.app_exception import AppException
from app.dependencies import get_ddb_table
from app.dto.category_request import CreateCategoryRequest, UpdateCategoryRequest
from app.models.category import Category


class CategoryRepository:
    def __init__(self, table=Depends(get_ddb_table)):
        self.table = table

    def create_category(self, req: CreateCategoryRequest) -> Category:
        try:
            item = {
                "pk": "CATEGORY",
                "sk": f"CATEGORY#{req.name}",
                "name": req.name,
                "default_threshold": req.default_threshold,
                "description": req.description,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(pk)",
            )

            return Category(**item)

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise AppException(
                    message=f"Category '{req.name}' already exists",
                    error_code="CATEGORY_ALREADY_EXISTS",
                    status_code=status.HTTP_409_CONFLICT,
                )

            raise AppException(
                message="Failed to create category",
                error_code="CATEGORY_CREATION_FAILED",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)},
            )

    def get_category(self, name: str) -> Category:
        try:
            response = self.table.get_item(
                Key={
                    "pk": "CATEGORY",
                    "sk": f"CATEGORY#{name}",
                }
            )
            item = response.get("Item")
            if item is None:
                raise AppException(
                    message="Category not found",
                    error_code="CATEGORY_NOT_FOUND",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            return Category(**item)

        except ClientError as e:
            raise AppException(
                message="Failed to fetch category",
                error_code="DATABASE_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)},
            )

    def get_all_categories(self) -> list[Category]:
        try:
            response = self.table.query(
                KeyConditionExpression="pk = :pk",
                ExpressionAttributeValues={":pk": "CATEGORY"},
            )

            return [Category(**item) for item in response.get("Items", [])]

        except ClientError as e:
            raise AppException(
                message="Failed to fetch categories",
                error_code="DATABASE_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)},
            )

    def update_category(self, name: str, req: UpdateCategoryRequest):
        update_expressions = []
        expression_values = {}

        if req.default_threshold is not None:
            update_expressions.append("default_threshold = :threshold")
            expression_values[":threshold"] = req.default_threshold

        if req.description is not None:
            update_expressions.append("description = :description")
            expression_values[":description"] = req.description

        # 🚫 Nothing to update
        if not update_expressions:
            return

        try:
            self.table.update_item(
                Key={
                    "pk": "CATEGORY",
                    "sk": f"CATEGORY#{name}",
                },
                UpdateExpression="SET " + ", ".join(update_expressions),
                ExpressionAttributeValues=expression_values,
                ConditionExpression="attribute_exists(pk) AND attribute_exists(sk)",
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                raise AppException(
                    message="Category not found",
                    error_code="CATEGORY_NOT_FOUND",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            raise AppException(
                message="Failed to update category",
                error_code="DATABASE_ERROR",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error": str(e)},
            )
