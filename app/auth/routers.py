from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pydash import pick

from app.auth.password import get_password_hash, verify_and_update, verify_password_hash
from app.user.models import UserChangePasswordModel, UserLoginModel, ResetPasswordModel
from app.user.services import read_user_by_username, update_user
from db.init_db import get_collection_client
import jwt

router = APIRouter()


@router.post("/login")
async def login(body: UserLoginModel, authorize: AuthJWT = Depends()):
    user = await read_user_by_username(body.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản hoặc mật khẩu của bạn không hợp lệ",
        )

    if user.get("active") == -1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản của bạn đang bị khoá",
        )

    verified, updated_password_hash = verify_and_update(
        body.password, user["hashed_password"]
    )

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tài khoản hoặc mật khẩu của bạn không hợp lệ",
        )

    # Update password has to a more robust one if needed
    if updated_password_hash is not None:
        await update_user(user["_id"], {"hashed_password": user["hashed_password"]})

    access_token = authorize.create_access_token(subject=str(user["_id"]))
    refresh_token = authorize.create_refresh_token(subject=str(user["_id"]))

    if(user.get("role") is None):
        role_collection = get_collection_client("role")
        role = await role_collection.find_one({"_id": ObjectId(user.get("role_id"))})
        user["role"] = role["role_code"]

    detail = pick(user, "role", "username", "full_name", "avatar_url")

    authorize.set_access_cookies(access_token)
    authorize.set_refresh_cookies(refresh_token)

    return HTTPException(status_code=status.HTTP_200_OK, detail=detail)

@router.put("/change-password")
async def change_user_password(body: UserChangePasswordModel):
    user = await read_user_by_username(body.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tìm thấy tài khoản của bạn",
        )


    verified = verify_password_hash(body.password, user["hashed_password"])

    if verified is False:   
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu không chính xác.",
        )

    # TODO: check schemas password
    hashed_password = get_password_hash(body.new_password)


    try:
        result = update_user(user["_id"], {"hashed_password": hashed_password})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể thay đổi mật khẩu. Vui lòng thử lại sau.",
        )

    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=None)

@router.post("/refresh")
def refresh(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=current_user)

    authorize.set_access_cookies(new_access_token)
    return HTTPException(status_code=status.HTTP_200_OK)

@router.delete("/logout")
def logout(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    authorize.unset_jwt_cookies()
    return HTTPException(status_code=status.HTTP_200_OK)

@router.post("/reset-password")
async def reset_password(body: ResetPasswordModel, authorize: AuthJWT = Depends()):
    users_client = get_collection_client("users")
    find_user_by_username = await users_client.find_one({"username": body.username})
    
    user_id = authorize._verified_token(body.token)['sub']   
    find_user_by_id = await users_client.find_one({"_id": ObjectId(user_id)})

    if find_user_by_username is None or find_user_by_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đường dẫn không hợp lệ hoặc đã hết hạn",
        )

    hashed_password = get_password_hash(body.new_password)
    find_user_by_id["hashed_password"] = hashed_password
    await users_client.update_one({"_id": ObjectId(user_id)}, {"$set": find_user_by_id})

    return HTTPException(status_code=status.HTTP_200_OK)

