from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_user_service
from app.dto.login_request import LoginRequest
from app.dto.signup_request import ConfirmSignupRequest, SignupRequest
from app.response.response import APIResponse
from app.services.user_service import UserService

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@auth_router.post("/signup", status_code=201)
def signup_handler(
    req: SignupRequest,
    user_service: UserService = Depends(get_user_service),
):
    user_email = req.email
    user_password = req.password
    data = user_service.signup(user_email, user_password)
    return APIResponse(status_code=201, message="User created successfully", data=data)


@auth_router.post("/signup/confirm", status_code=200)
def confirm_signup_handler(
    req: ConfirmSignupRequest, user_service: UserService = Depends(get_user_service)
):
    confirmation_code = req.code
    user_email = req.email
    try:
        data = user_service.confirm_signup(user_email, confirmation_code)
        return APIResponse(
            status_code=200, message="User confirmed successfully", data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/login", status_code=200)
def login_handler(
    req: LoginRequest, user_service: UserService = Depends(get_user_service)
):
    user_email = req.email
    user_password = req.password
    try:
        data = user_service.login(user_email, user_password)
        return APIResponse(
            status_code=200, message="User logged in successfully", data=data
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
