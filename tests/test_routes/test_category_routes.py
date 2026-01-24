import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.app import app
from app.services.category_service import CategoryService
from app.dependencies import get_current_user
from app.models.user_group import UserGroup


class TestCategoryRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.mock_category_service = MagicMock()

        # Override CategoryService
        app.dependency_overrides[CategoryService] = lambda: self.mock_category_service

        # Authorized MANAGER user by default
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [UserGroup.MANAGER],
        }

    def tearDown(self):
        app.dependency_overrides = {}

    # ---------- CREATE CATEGORY ----------

    def test_create_category_success(self):
        self.mock_category_service.create_category.return_value = {
            "name": "ELECTRONICS",
            "default_threshold": 10,
        }

        payload = {
            "name": "ELECTRONICS",
            "default_threshold": 10,
        }

        response = self.client.post("/category/", json=payload)

        self.assertEqual(response.status_code, 201)

        body = response.json()
        self.assertEqual(body["message"], "Category created successfully")
        self.assertEqual(body["data"]["name"], "ELECTRONICS")

        self.mock_category_service.create_category.assert_called_once()

    # ---------- CREATE CATEGORY (FORBIDDEN) ----------

    def test_create_category_forbidden(self):
        # Override user WITHOUT MANAGER role
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [],
        }

        payload = {
            "name": "GROCERY",
            "default_threshold": 5,
        }

        response = self.client.post("/category/", json=payload)

        self.assertEqual(response.status_code, 403)

    # ---------- GET ALL CATEGORIES ----------

    def test_get_all_categories(self):
        self.mock_category_service.get_all_category.return_value = [
            {"name": "ELECTRONICS"},
            {"name": "GROCERY"},
        ]

        response = self.client.get("/category/")

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Categories found")
        self.assertEqual(len(body["data"]), 2)

        self.mock_category_service.get_all_category.assert_called_once()

    # ---------- GET CATEGORY BY NAME ----------

    def test_get_category_by_name(self):
        self.mock_category_service.get_category_by_name.return_value = {
            "name": "ELECTRONICS",
            "default_threshold": 10,
        }

        response = self.client.get("/category/?name=ELECTRONICS")

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Category found")
        self.assertEqual(body["data"]["name"], "ELECTRONICS")

        self.mock_category_service.get_category_by_name.assert_called_once_with(
            "ELECTRONICS"
        )

    # ---------- UPDATE CATEGORY ----------

    def test_update_category_success(self):
        self.mock_category_service.update_threshold.return_value = None

        payload = {
            "default_threshold": 20,
        }

        response = self.client.patch("/category/ELECTRONICS", json=payload)

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Category updated successfully")

        self.mock_category_service.update_threshold.assert_called_once()

    # ---------- GET CATEGORY (FORBIDDEN) ----------

    def test_get_category_forbidden(self):
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [],
        }

        response = self.client.get("/category/")

        self.assertEqual(response.status_code, 403)
