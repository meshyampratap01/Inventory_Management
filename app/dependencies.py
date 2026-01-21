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


async def fetch_jwks(JWKS_URL):
    async with httpx.AsyncClient() as client:
        resp = await client.get(JWKS_URL)
        return resp


@asynccontextmanager
async def lifespan(app: FastAPI):
    ENV = os.getenv("ENV", "local")
    if ENV == "local":
        load_dotenv()
    cognito = boto3.client("cognito-idp", region_name="ap-south-1")
    app.state.cognito_client = cognito
    app.state.cognito_client_id = os.getenv("COGNITO_CLIENT_ID")
    JWKSURL = os.getenv("JWKS_URL")
    app.state.jwks = await fetch_jwks(JWKSURL)
    app.state.cognito_issuer = os.getenv("COGNITO_ISSUER")
    yield


def get_cognito_config(request: Request):
    return (request.app.state.cognito_client, request.app.state.cognito_client_id)


def get_user_service(request: Request) -> UserService:
    cognito_client, cognito_client_id = get_cognito_config(request)
    return UserService(cognito_client, cognito_client_id)


security = HTTPBearer()


def get_current_user(
    req: Request,
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    jwks = req.app.state.jwks
    cognito_issuer = req.app.state.cognito_issuer
    try:
        return jwt_verifier.verify_access_token(creds.credentials, jwks, cognito_issuer)
    except Exception:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired token",
        )
