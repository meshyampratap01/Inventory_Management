import unittest
from unittest.mock import MagicMock
from botocore.exceptions import ClientError

from app.services.user_service import UserService
from app.app_exception.app_exception import AppException
from app.dto.create_employee_request import CreateEmployeeRequest
from app.models.user_group import UserGroup


def cognito_error(code: str):
    return ClientError(
        error_response={"Error": {"Code": code, "Message": "error"}},
        operation_name="CognitoOperation",
    )


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mock_cognito = MagicMock()
        self.service = UserService(
            cognito_client=self.mock_cognito,
            cognito_client_id="client-id",
            user_pool_id="pool-id",
        )

    def test_add_user_to_group_success(self):
        self.service._add_user_to_group("user@example.com", UserGroup.MANAGER)

        self.mock_cognito.admin_add_user_to_group.assert_called_once_with(
            UserPoolId="pool-id",
            Username="user@example.com",
            GroupName=UserGroup.MANAGER,
        )

    def test_add_user_to_group_user_not_found(self):
        self.mock_cognito.admin_add_user_to_group.side_effect = cognito_error(
            "UserNotFoundException"
        )

        with self.assertRaises(AppException) as ctx:
            self.service._add_user_to_group("user@example.com", UserGroup.MANAGER)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_add_user_to_group_generic_failure(self):
        self.mock_cognito.admin_add_user_to_group.side_effect = cognito_error(
            "InternalError"
        )

        with self.assertRaises(AppException) as ctx:
            self.service._add_user_to_group("user@example.com", UserGroup.MANAGER)

        self.assertEqual(ctx.exception.status_code, 500)

    def test_signup_success(self):
        self.mock_cognito.sign_up.return_value = {
            "UserSub": "sub-123",
            "UserConfirmed": False,
        }

        result = self.service.signup("test@example.com", "Password123!")

        self.assertEqual(result["user_sub"], "sub-123")
        self.assertFalse(result["confirmed"])

        self.mock_cognito.sign_up.assert_called_once()

    def test_signup_user_already_exists(self):
        self.mock_cognito.sign_up.side_effect = cognito_error("UsernameExistsException")

        with self.assertRaises(AppException) as ctx:
            self.service.signup("test@example.com", "Password123!")

        self.assertEqual(ctx.exception.status_code, 400)

    def test_signup_generic_failure(self):
        self.mock_cognito.sign_up.side_effect = cognito_error("InternalError")

        with self.assertRaises(AppException) as ctx:
            self.service.signup("test@example.com", "Password123!")

        self.assertEqual(ctx.exception.status_code, 500)

    def test_confirm_signup_success(self):
        self.mock_cognito.confirm_sign_up.return_value = {"Status": "SUCCESS"}

        result = self.service.confirm_signup("test@example.com", "123456")

        self.assertEqual(result["Status"], "SUCCESS")
        self.mock_cognito.confirm_sign_up.assert_called_once()

    def test_confirm_signup_user_not_found(self):
        self.mock_cognito.confirm_sign_up.side_effect = cognito_error(
            "UserNotFoundException"
        )

        with self.assertRaises(AppException) as ctx:
            self.service.confirm_signup("test@example.com", "123456")

        self.assertEqual(ctx.exception.status_code, 400)

    def test_confirm_signup_generic_failure(self):
        self.mock_cognito.confirm_sign_up.side_effect = cognito_error("InternalError")

        with self.assertRaises(AppException) as ctx:
            self.service.confirm_signup("test@example.com", "123456")

        self.assertEqual(ctx.exception.status_code, 500)

    def test_login_success(self):
        self.mock_cognito.initiate_auth.return_value = {
            "AuthenticationResult": {"AccessToken": "token"}
        }

        result = self.service.login("test@example.com", "Password123!")

        self.assertIn("AuthenticationResult", result)
        self.mock_cognito.initiate_auth.assert_called_once()

    def test_login_user_not_found(self):
        self.mock_cognito.initiate_auth.side_effect = cognito_error(
            "UserNotFoundException"
        )

        with self.assertRaises(AppException) as ctx:
            self.service.login("test@example.com", "Password123!")

        self.assertEqual(ctx.exception.status_code, 400)

    def test_login_generic_failure(self):
        self.mock_cognito.initiate_auth.side_effect = cognito_error("InternalError")

        with self.assertRaises(AppException) as ctx:
            self.service.login("test@example.com", "Password123!")

        self.assertEqual(ctx.exception.status_code, 500)

    def test_create_manager_success(self):
        req = CreateEmployeeRequest(
            email="manager@example.com",
            name="manager",
            password="Password123!",
        )

        self.mock_cognito.admin_create_user.return_value = {"User": "created"}

        result = self.service.create_manager(req)

        self.assertEqual(result["User"], "created")
        self.mock_cognito.admin_create_user.assert_called_once()
        self.mock_cognito.admin_set_user_password.assert_called_once()

    def test_create_manager_user_exists(self):
        self.mock_cognito.admin_create_user.side_effect = cognito_error(
            "UsernameExistsException"
        )

        req = CreateEmployeeRequest(
            email="manager@example.com",
            name="manager",
            password="Password123!",
        )

        with self.assertRaises(AppException) as ctx:
            self.service.create_manager(req)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_create_manager_generic_failure(self):
        self.mock_cognito.admin_create_user.side_effect = cognito_error("InternalError")

        req = CreateEmployeeRequest(
            email="manager@example.com",
            name="manager",
            password="Password123!",
        )

        with self.assertRaises(AppException) as ctx:
            self.service.create_manager(req)

        self.assertEqual(ctx.exception.status_code, 500)

    def test_create_staff_success(self):
        req = CreateEmployeeRequest(
            email="staff@example.com",
            name="staff",
            password="Password123!",
        )

        self.mock_cognito.admin_create_user.return_value = {"User": "created"}

        result = self.service.create_staff(req)

        self.assertEqual(result["User"], "created")
        self.mock_cognito.admin_set_user_password.assert_called_once()

    def test_create_staff_user_exists(self):
        self.mock_cognito.admin_create_user.side_effect = cognito_error(
            "UsernameExistsException"
        )

        req = CreateEmployeeRequest(
            email="staff@example.com",
            name="staff",
            password="Password123!",
        )

        with self.assertRaises(AppException) as ctx:
            self.service.create_staff(req)

        self.assertEqual(ctx.exception.status_code, 400)

    def test_create_staff_generic_failure(self):
        self.mock_cognito.admin_create_user.side_effect = cognito_error("InternalError")

        req = CreateEmployeeRequest(
            email="staff@example.com",
            name="staff",
            password="Password123!",
        )

        with self.assertRaises(AppException) as ctx:
            self.service.create_staff(req)

        self.assertEqual(ctx.exception.status_code, 500)


if __name__ == "__main__":
    unittest.main()
