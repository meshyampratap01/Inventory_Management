from contextlib import asynccontextmanager
import os
import boto3
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, status, FastAPI, Request
import httpx

from app.app_exception.app_exception import AppException
from app.utils import jwt_verifier
from app.services.user_service import UserService


async def fetch_jwks(jwks_url) -> dict:
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(jwks_url)
        resp.raise_for_status()
        return resp.json()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ENV = os.getenv("ENV", "local")
    if ENV == "local":
        load_dotenv()

    cognito = boto3.client("cognito-idp", region_name="ap-south-1")
    app.state.cognito_client = cognito
    app.state.cognito_client_id = os.getenv("COGNITO_CLIENT_ID")
    app.state.user_pool_id = os.getenv("USER_POOL_ID")

    app.state.cognito_issuer = os.getenv("COGNITO_ISSUER")
    if app.state.cognito_issuer is None:
        raise Exception("COGNITO_ISSUER is not set")
    JWKSURL = os.getenv("JWKS_URL")
    if JWKSURL is None:
        raise Exception("JWKS_URL is not set")
    app.state.jwks = await fetch_jwks(JWKSURL)

    ddb_resource = boto3.resource(
        "dynamodb", region_name=os.getenv("AWS_REGION", "ap-south-1")
    )
    app.state.ddb_resource = ddb_resource
    app.state.table_name = str(os.getenv("table_name"))
    yield


def get_cognito_config(request: Request):
    return (
        request.app.state.cognito_client,
        request.app.state.cognito_client_id,
        request.app.state.user_pool_id,
    )


def get_user_service(request: Request) -> UserService:
    cognito_client, cognito_client_id, user_pool_id = get_cognito_config(request)
    return UserService(cognito_client, cognito_client_id, user_pool_id)


security = HTTPBearer()


def get_current_user(
    req: Request,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    jwks = req.app.state.jwks
    cognito_issuer = req.app.state.cognito_issuer
    try:
        return jwt_verifier.verify_access_token(creds.credentials, jwks, cognito_issuer)
    except Exception as e:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired token",
            error_code="INVALID_TOKEN",
            details={"error": str(e)},
        )


def require_any_group(*allowed_groups: str):
    def group_checker(current_user=Depends(get_current_user)):
        user_groups = set(current_user.get("cognito:groups", []))

        if not user_groups.intersection(allowed_groups):
            raise AppException(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Forbidden",
                error_code="FORBIDDEN",
            )

        return current_user

    return group_checker


def get_ddb_table(request: Request):
    ddb_resource = request.app.state.ddb_resource
    table_name = request.app.state.table_name
    return ddb_resource.Table(table_name)


def get_sns_topic_arn():
    topic_arn = os.getenv("topic_arn")
    return topic_arn


def get_cognito_client(request: Request):
    cognito_client = request.app.state.cognito_client
    return cognito_client
