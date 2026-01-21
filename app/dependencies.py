from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, status, Request

from app.app_exception.app_exception import AppException
from app.utils import jwt_verifier
from app.services.user_service import UserService


def get_cognito_config(request: Request):
    return (request.app.state.cognito_client, request.app.state.cognito_client_id)


def get_user_service(request: Request) -> UserService:
    cognito_client, cognito_client_id = get_cognito_config(request)
    return UserService(cognito_client, cognito_client_id)


security = HTTPBearer()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        return jwt_verifier.verify_access_token(creds.credentials)
    except Exception:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired token",
        )
