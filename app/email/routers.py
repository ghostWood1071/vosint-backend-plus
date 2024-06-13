from fastapi import APIRouter
from app.email.models import EmailModel

from app.email.services import (
    exec_forgot_password
)
from app.email import services
from fastapi import Depends
from fastapi_jwt_auth import AuthJWT

router = APIRouter()

@router.post("/forgot-password")
async def forgot_password(req: EmailModel, authorize: AuthJWT = Depends()):
    return await exec_forgot_password(req, authorize)
