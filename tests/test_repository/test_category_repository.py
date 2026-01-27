import unittest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

from app.repository.category_repository import CategoryRepository
from app.app_exception.app_exception import AppException
from app.dto.category_request import CreateCategoryRequest, UpdateCategoryRequest
from app.models.category import Category


def ddb_error(code: str):
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "error"}},
        operation_name="DynamoDBOperation",
    )


class TestCategoryRepository(unittest.TestCase):
    def setUp(self):
        self.mock_table = MagicMock()
        self.repo = CategoryRepository(table=self.mock_table)

    def test_create_category_success(self):
        req = CreateCategoryRequest(
            name="ELECTRONICS",
            description="Electronic items",
            default_threshold=10,
        )

        category = self.repo.create_category(req)

        self.assertIsInstance(category, Category)
        self.assertEqual(category.name, "ELECTRONICS")
        self.assertEqual(category.default_threshold, 10)

        self.mock_table.put_item.assert_called_once()
        args = self.mock_table.put_item.call_args[1]
        self.assertEqual(args["Item"]["pk"], "CATEGORY")

    def test_create_category_already_exists(self):
        self.mock_table.put_item.side_effect = ddb_error(
            "ConditionalCheckFailedException"
        )

        req = CreateCategoryRequest(
            name="ELECTRONICS",
            description="Electronic items",
            default_threshold=10,
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.create_category(req)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 409)
        self.assertEqual(exc.error_code, "CATEGORY_ALREADY_EXISTS")

    def test_create_category_generic_failure(self):
        self.mock_table.put_item.side_effect = ddb_error("InternalServerError")

        req = CreateCategoryRequest(
            name="ELECTRONICS",
            description="Electronic items",
            default_threshold=10,
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.create_category(req)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "CATEGORY_CREATION_FAILED")

    def test_get_category_success(self):
        self.mock_table.get_item.return_value = {
            "Item": {
                "pk": "CATEGORY",
                "sk": "CATEGORY#ELECTRONICS",
                "name": "ELECTRONICS",
                "description": "Electronic items",
                "default_threshold": 10,
            }
        }

        category = self.repo.get_category("ELECTRONICS")

        self.assertIsInstance(category, Category)
        self.assertEqual(category.name, "ELECTRONICS")

        self.mock_table.get_item.assert_called_once()

    def test_get_category_ddb_failure(self):
        self.mock_table.get_item.side_effect = ddb_error("InternalServerError")

        with self.assertRaises(AppException) as ctx:
            self.repo.get_category("ELECTRONICS")

        exc = ctx.exception
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "DATABASE_ERROR")

    def test_get_all_categories_success(self):
        self.mock_table.query.return_value = {
            "Items": [
                {
                    "pk": "CATEGORY",
                    "sk": "CATEGORY#ELECTRONICS",
                    "name": "ELECTRONICS",
                    "description": "Electronic items",
                    "default_threshold": 10,
                },
                {
                    "pk": "CATEGORY",
                    "sk": "CATEGORY#GROCERY",
                    "name": "GROCERY",
                    "description": "Groceries",
                    "default_threshold": 5,
                },
            ]
        }

        result = self.repo.get_all_categories()

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], Category)
        self.assertEqual(result[1].name, "GROCERY")

        self.mock_table.query.assert_called_once()

    def test_get_all_categories_ddb_failure(self):
        self.mock_table.query.side_effect = ddb_error("InternalServerError")

        with self.assertRaises(AppException) as ctx:
            self.repo.get_all_categories()

        exc = ctx.exception
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "DATABASE_ERROR")

    def test_update_category_success_threshold(self):
        req = UpdateCategoryRequest(default_threshold=20, description=None)

        self.repo.update_category("ELECTRONICS", req)

        self.mock_table.update_item.assert_called_once()
        args = self.mock_table.update_item.call_args[1]
        self.assertIn("default_threshold", args["UpdateExpression"])

    def test_update_category_success_description(self):
        req = UpdateCategoryRequest(default_threshold=None, description="New desc")

        self.repo.update_category("ELECTRONICS", req)

        self.mock_table.update_item.assert_called_once()
        args = self.mock_table.update_item.call_args[1]
        self.assertIn("description", args["UpdateExpression"])

    def test_update_category_nothing_to_update(self):
        req = UpdateCategoryRequest(default_threshold=None, description=None)

        self.repo.update_category("ELECTRONICS", req)

        self.mock_table.update_item.assert_not_called()

    def test_update_category_not_found(self):
        self.mock_table.update_item.side_effect = ddb_error(
            "ConditionalCheckFailedException"
        )

        req = UpdateCategoryRequest(default_threshold=10, description=None)

        with self.assertRaises(AppException) as ctx:
            self.repo.update_category("UNKNOWN", req)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "CATEGORY_NOT_FOUND")

    def test_update_category_ddb_failure(self):
        self.mock_table.update_item.side_effect = ddb_error("InternalServerError")

        req = UpdateCategoryRequest(default_threshold=10, description=None)

        with self.assertRaises(AppException) as ctx:
            self.repo.update_category("ELECTRONICS", req)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.error_code, "DATABASE_ERROR")

    def test_delete_category_success(self):
        self.repo.delete_category("ELECTRONICS")

        self.mock_table.delete_item.assert_called_once()

    def test_delete_category_not_found(self):
        self.mock_table.delete_item.side_effect = ddb_error(
            "ConditionalCheckFailedException"
        )

        with self.assertRaises(AppException) as ctx:
            self.repo.delete_category("UNKNOWN")

        exc = ctx.exception
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "CATEGORY_NOT_FOUND")
