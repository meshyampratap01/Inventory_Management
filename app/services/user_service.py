from botocore.utils import ClientError

from app.app_exception.app_exception import AppException
from app.dto.create_employee_request import CreateEmployeeRequest
from app.models.user_group import UserGroup


class UserService:
    def __init__(self, cognito_client, cognito_client_id: str, user_pool_id: str):
        self.cognito_client = cognito_client
        self.cognito_client_id = cognito_client_id
        self.user_pool_id = user_pool_id

    def _add_user_to_group(self, user_sub: str, group_name: str):
        try:
            self.cognito_client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=user_sub,
                GroupName=group_name,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "UserNotFoundException":
                raise AppException(message="User not found", status_code=400)

            raise AppException(
                status_code=500,
                message="Failed to add user to group",
                details={"error": str(e)},
            )

    def signup(self, email: str, password: str) -> dict:
        try:
            response = self.cognito_client.sign_up(
                ClientId=self.cognito_client_id,
                Username=email,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )
            return {
                "user_sub": response["UserSub"],
                "confirmed": response["UserConfirmed"],
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "UsernameExistsException":
                raise AppException(message="User already exists", status_code=400)

            raise AppException(
                status_code=500,
                message="Failed to signup",
                details={"error": str(e)},
            )

    def confirm_signup(self, email: str, code: str):
        try:
            return self.cognito_client.confirm_sign_up(
                ClientId=self.cognito_client_id,
                Username=email,
                ConfirmationCode=code,
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "UserNotFoundException":
                raise AppException(message="User not found", status_code=400)

            raise AppException(
                status_code=500,
                message="Failed to confirm signup",
                details={"error": str(e)},
            )

    def login(self, email: str, password: str):
        try:
            return self.cognito_client.initiate_auth(
                ClientId=self.cognito_client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": email, "PASSWORD": password},
            )
        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "UserNotFoundException":
                raise AppException(message="User not found", status_code=400)

            raise AppException(
                status_code=500,
                message="Failed to login",
                details={"error": str(e)},
            )

    def create_manager(self, req: CreateEmployeeRequest):
        try:
            name = req.name.capitalize()
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=req.email,
                UserAttributes=[
                    {"Name": "email", "Value": req.email},
                    {"Name": "name", "Value": name},
                    {"Name": "email_verified", "Value": "True"},
                ],
                DesiredDeliveryMediums=["EMAIL"],
                TemporaryPassword=req.password,
            )
            self._add_user_to_group(req.email, UserGroup.MANAGER)
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=req.email,
                Password=req.password,
                Permanent=True,
            )

            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "UsernameExistsException":
                raise AppException(message="User already exists", status_code=400)

            raise AppException(
                status_code=500,
                message="Failed to create user",
                details={"error": str(e)},
            )

    def create_staff(self, req: CreateEmployeeRequest):
        try:
            name = req.name.capitalize()
            response = self.cognito_client.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=req.email,
                UserAttributes=[
                    {"Name": "email", "Value": req.email},
                    {"Name": "name", "Value": name},
                    {"Name": "email_verified", "Value": "True"},
                ],
                DesiredDeliveryMediums=["EMAIL"],
                TemporaryPassword=req.password,
            )
            self._add_user_to_group(req.email, UserGroup.STAFF)
            self.cognito_client.admin_set_user_password(
                UserPoolId=self.user_pool_id,
                Username=req.email,
                Password=req.password,
                Permanent=True,
            )
            return response
        except ClientError as e:
            error_code = e.response["Error"]["Code"]

            if error_code == "UsernameExistsException":
                raise AppException(message="User already exists", status_code=400)

            raise AppException(
                status_code=500,
                message="Failed to create user",
                details={"error": str(e)},
            )
