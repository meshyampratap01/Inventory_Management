from fastapi import APIRouter, Depends

from app.dependencies import get_user_service, require_any_group
from app.dto.create_employee_request import CreateEmployeeRequest
from app.models.user_group import UserGroup
from app.response.response import APIResponse
from app.services.user_service import UserService

employee_router = APIRouter(
    prefix="/employees",
    tags=["employees"],
)


@employee_router.post("/manager", status_code=201, response_model=APIResponse)
def create_manager_handler(
    req: CreateEmployeeRequest,
    _=Depends(require_any_group(UserGroup.MANAGER)),
    user_service: UserService = Depends(get_user_service),
):
    data = user_service.create_manager(req)
    return APIResponse(
        status_code=201, message="Manager created successfully", data=data
    )


@employee_router.post("/staff", status_code=201, response_model=APIResponse)
def create_staff_handler(
    req: CreateEmployeeRequest,
    _=Depends(require_any_group(UserGroup.MANAGER)),
    user_service: UserService = Depends(get_user_service),
):
    data = user_service.create_staff(req)
    return APIResponse(status_code=201, message="Staff created successfully", data=data)
