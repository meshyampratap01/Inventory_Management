from botocore.utils import ClientError

from app.app_exception.app_exception import AppException


class UserService:
    def __init__(self, cognito_client, cognito_client_id: str):
        self.cognito_client = cognito_client
        self.cognito_client_id = cognito_client_id

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

            raise RuntimeError("Signup failed and reason is", e)

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

            raise RuntimeError("Signup failed and reason is", e)

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

            raise RuntimeError("Login failed and reason is", e)
