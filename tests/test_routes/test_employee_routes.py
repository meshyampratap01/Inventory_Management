import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.app import app
from app.dependencies import get_current_user, get_user_service
from app.models.user_group import UserGroup


class TestEmployeeRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        self.mock_user_service = MagicMock()

        # Override UserService dependency
        app.dependency_overrides[get_user_service] = lambda: self.mock_user_service

        # Default: authorized MANAGER user
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [UserGroup.MANAGER],
        }

    def tearDown(self):
        app.dependency_overrides = {}

    # ---------- CREATE MANAGER ----------

    def test_create_manager_success(self):
        self.mock_user_service.create_manager.return_value = {
            "email": "manager@example.com",
            "role": "MANAGER",
        }

        payload = {
            "email": "manager@example.com",
            "name": "Manager One",
            "password": "StrongPass123!",
        }

        response = self.client.post("/employees/manager", json=payload)

        self.assertEqual(response.status_code, 201)

        body = response.json()
        self.assertEqual(body["message"], "Manager created successfully")
        self.assertEqual(body["data"]["role"], "MANAGER")

        self.mock_user_service.create_manager.assert_called_once()

    # ---------- CREATE STAFF ----------

    def test_create_staff_success(self):
        self.mock_user_service.create_staff.return_value = {
            "email": "staff@example.com",
            "role": "STAFF",
        }

        payload = {
            "email": "staff@example.com",
            "name": "Staff One",
            "password": "StrongPass123!",
        }

        response = self.client.post("/employees/staff", json=payload)

        self.assertEqual(response.status_code, 201)

        body = response.json()
        self.assertEqual(body["message"], "Staff created successfully")
        self.assertEqual(body["data"]["role"], "STAFF")

        self.mock_user_service.create_staff.assert_called_once()

    # ---------- CREATE MANAGER (FORBIDDEN) ----------

    def test_create_manager_forbidden(self):
        # Override as non-manager user
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [UserGroup.STAFF],
        }

        payload = {
            "email": "manager@example.com",
            "name": "Manager One",
            "password": "StrongPass123!",
        }

        response = self.client.post("/employees/manager", json=payload)

        self.assertEqual(response.status_code, 403)

    # ---------- CREATE STAFF (FORBIDDEN) ----------

    def test_create_staff_forbidden(self):
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "test-user",
            "email": "test@example.com",
            "cognito:groups": [],
        }

        payload = {
            "email": "staff@example.com",
            "name": "Staff One",
            "password": "StrongPass123!",
        }

        response = self.client.post("/employees/staff", json=payload)

        self.assertEqual(response.status_code, 403)
