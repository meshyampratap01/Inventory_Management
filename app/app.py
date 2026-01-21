from contextlib import asynccontextmanager
from app.routes.auth import auth_router
import os
from fastapi import FastAPI, HTTPException, Request
from dotenv import load_dotenv
import boto3
import httpx
from app.app_exception.app_exception import AppException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def fetch_jwks(JWKS_URL):
    async with httpx.AsyncClient() as client:
        resp = await client.get(JWKS_URL)
        return resp.json()


@asynccontextmanager
async def lifespan(app: FastAPI):
    ENV = os.getenv("ENV", "local")
    if ENV == "local":
        load_dotenv()
    cognito = boto3.client("cognito-idp", region_name="ap-south-1")
    app.state.cognito_client = cognito
    app.state.cognito_client_id = os.getenv("COGNITO_CLIENT_ID")
    JWKSURL = os.getenv("JWKS_URL")
    app.state.jwks_url = await fetch_jwks(JWKSURL)
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


app.include_router(auth_router)
