import unittest
from unittest.mock import MagicMock

from app.models.category import Category
from app.services.category_service import CategoryService
from app.app_exception.app_exception import AppException
from app.dto.category_request import CreateCategoryRequest, UpdateCategoryRequest
from app.dto.category_response import CategoryResponse


class TestCategoryService(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.service = CategoryService(category_repository=self.mock_repo)

    def test_create_category_success(self):
        self.mock_repo.get_category.return_value = None

        req = CreateCategoryRequest(
            name="ELECTRONICS",
            description="Electronic items",
            default_threshold=10,
        )

        result = self.service.create_category(req)

        self.assertIsInstance(result, CategoryResponse)
        self.assertEqual(result.name, "ELECTRONICS")
        self.assertEqual(result.default_threshold, 10)

        self.mock_repo.get_category.assert_called_once_with("ELECTRONICS")
        self.mock_repo.create_category.assert_called_once_with(req)

    def test_create_category_already_exists(self):
        self.mock_repo.get_category.return_value = MagicMock()

        req = CreateCategoryRequest(
            name="ELECTRONICS",
            description="Electronic items",
            default_threshold=10,
        )

        with self.assertRaises(AppException) as ctx:
            self.service.create_category(req)

        exc = ctx.exception
        self.assertEqual(exc.status_code, 409)
        self.assertEqual(exc.error_code, "CATEGORY_ALREADY_EXISTS")

        self.mock_repo.create_category.assert_not_called()

    def test_get_category_by_name_success(self):
        self.mock_repo.get_category.return_value = MagicMock(
            description="Electronic items",
            default_threshold=10,
        )

        result = self.service.get_category_by_name("ELECTRONICS")

        self.assertIsInstance(result, CategoryResponse)
        self.assertEqual(result.name, "ELECTRONICS")
        self.assertEqual(result.default_threshold, 10)

        self.mock_repo.get_category.assert_called_once_with("ELECTRONICS")

    def test_get_category_by_name_not_found(self):
        self.mock_repo.get_category.return_value = None

        with self.assertRaises(AppException) as ctx:
            self.service.get_category_by_name("UNKNOWN")

        exc = ctx.exception
        self.assertEqual(exc.status_code, 404)
        self.assertEqual(exc.error_code, "CATEGORY_NOT_FOUND")

    def test_get_all_category_success(self):
        self.mock_repo.get_all_categories.return_value = [
            Category(
                name="ELECTRONICS",
                description="Electronic items",
                default_threshold=10,
            ),
            Category(
                name="GROCERY",
                description="Groceries",
                default_threshold=5,
            ),
        ]

        result = self.service.get_all_category()

        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], CategoryResponse)
        self.assertEqual(result[0].name, "ELECTRONICS")
        self.assertEqual(result[1].name, "GROCERY")

        self.mock_repo.get_all_categories.assert_called_once()

    def test_update_threshold_success(self):
        req = UpdateCategoryRequest(
            default_threshold=20,
            description=None,
        )

        self.service.update_threshold(req, "ELECTRONICS")

        self.mock_repo.update_category.assert_called_once_with("ELECTRONICS", req)


if __name__ == "__main__":
    unittest.main()
