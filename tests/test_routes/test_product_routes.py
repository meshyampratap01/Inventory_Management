import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.app import app
from app.models.user_group import UserGroup
from app.services.product_service import ProductService
from app.dependencies import get_current_user


class TestProductRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.mock_product_service = MagicMock()

        app.dependency_overrides[ProductService] = lambda: self.mock_product_service

        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [UserGroup.MANAGER, UserGroup.STAFF],
        }

    def tearDown(self):
        app.dependency_overrides = {}

    def test_create_product_success(self):
        self.mock_product_service.create_product.return_value = {
            "id": "prod-1",
            "name": "Laptop",
            "quantity": 10,
        }

        payload = {
            "name": "Laptop",
            "price": 50000,
            "quantity": 10,
            "category": "ELECTRONICS",
        }

        response = self.client.post("/products/", json=payload)

        self.assertEqual(response.status_code, 201)

        body = response.json()
        self.assertEqual(body["message"], "Product created successfully")
        self.assertEqual(body["data"]["name"], "Laptop")

        self.mock_product_service.create_product.assert_called_once()

    def test_get_all_products(self):
        self.mock_product_service.get_all_products.return_value = [
            {"id": "p1", "name": "Item 1"},
            {"id": "p2", "name": "Item 2"},
        ]

        response = self.client.get("/products/")

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Products found")
        self.assertEqual(len(body["data"]), 2)

        self.mock_product_service.get_all_products.assert_called_once()

    def test_get_product_by_id(self):
        self.mock_product_service.get_product_by_id.return_value = {
            "id": "p1",
            "name": "Item 1",
        }

        response = self.client.get("/products/?product_id=p1")

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Product found")
        self.assertEqual(body["data"]["id"], "p1")

        self.mock_product_service.get_product_by_id.assert_called_once_with("p1")

    def test_stock_in_success(self):
        self.mock_product_service.stock_in.return_value = {
            "id": "p1",
            "quantity": 15,
        }

        payload = {
            "product_id": "p1",
            "quantity": 5,
        }

        response = self.client.patch("/products/stockin", json=payload)

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Product's stock updated successfully")
        self.assertEqual(body["data"]["quantity"], 15)

        self.mock_product_service.stock_in.assert_called_once()

    def test_stock_out_success(self):
        self.mock_product_service.stock_out.return_value = {
            "id": "p1",
            "quantity": 8,
        }

        payload = {
            "product_id": "p1",
            "quantity": 2,
        }

        response = self.client.patch("/products/stockout", json=payload)

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "Product's stock updated successfully")
        self.assertEqual(body["data"]["quantity"], 8)

        self.mock_product_service.stock_out.assert_called_once()


if __name__ == "__main__":
    unittest.main()
