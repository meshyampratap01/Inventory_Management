import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.app import app
from app.dependencies import get_user_service


class TestAuthRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.mock_user_service = MagicMock()

        app.dependency_overrides[get_user_service] = lambda: self.mock_user_service

    def tearDown(self):
        app.dependency_overrides = {}

    def test_signup_success(self):
        self.mock_user_service.signup.return_value = {
            "user_id": "123",
            "email": "test@example.com",
        }

        payload = {
            "name": "test_user",
            "email": "test@example.com",
            "password": "StrongPass123!",
        }

        response = self.client.post("/auth/signup", json=payload)

        self.assertEqual(response.status_code, 201)

        body = response.json()
        self.assertEqual(body["message"], "User created successfully")
        self.assertEqual(body["data"]["email"], "test@example.com")

        self.mock_user_service.signup.assert_called_once_with(
            "test@example.com", "StrongPass123!"
        )

    def test_confirm_signup_success(self):
        self.mock_user_service.confirm_signup.return_value = {"status": "CONFIRMED"}

        payload = {
            "email": "test@example.com",
            "code": "123456",
        }

        response = self.client.post("/auth/signup/confirm", json=payload)

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "User confirmed successfully")
        self.assertEqual(body["data"]["status"], "CONFIRMED")

        self.mock_user_service.confirm_signup.assert_called_once_with(
            "test@example.com", "123456"
        )

    def test_confirm_signup_failure(self):
        self.mock_user_service.confirm_signup.side_effect = Exception(
            "Invalid confirmation code"
        )

        payload = {
            "email": "test@example.com",
            "code": "000000",
        }

        response = self.client.post("/auth/signup/confirm", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid confirmation code")

    def test_login_success(self):
        self.mock_user_service.login.return_value = {
            "access_token": "token123",
            "refresh_token": "refresh123",
        }

        payload = {
            "email": "test@example.com",
            "password": "StrongPass123!",
        }

        response = self.client.post("/auth/login", json=payload)

        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertEqual(body["message"], "User logged in successfully")
        self.assertIn("access_token", body["data"])

        self.mock_user_service.login.assert_called_once_with(
            "test@example.com", "StrongPass123!"
        )

    def test_login_failure(self):
        self.mock_user_service.login.side_effect = Exception("Invalid credentials")

        payload = {
            "email": "test@example.com",
            "password": "wrongpass",
        }

        response = self.client.post("/auth/login", json=payload)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid credentials")
