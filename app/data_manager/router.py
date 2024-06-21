from fastapi import APIRouter, File, UploadFile, Depends
from typing import *
from .model import SearchItemParams, Doc
from .service import *
import traceback
from fastapi import HTTPException
from fastapi_jwt_auth import AuthJWT
import os

router = APIRouter()

@router.get("/statistic")
def statistic_route():
    try:
        data = statistic()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))

@router.post("/search")
def search_route(searchParams:SearchItemParams):
    try:
        data = search_item(**searchParams.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))

@router.post("/add-news")
def route_add_news(ids:List[str] = []):
    try:
        inserteds = add_news(ids)
        return inserteds
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))    
    
@router.post("/add-doc")
def route_add_doc(doc: Doc):
    try:
        inserted_id = add_doc(doc.dict())
        return inserted_id
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/delete-news")
def route_add_news(ids:List[str] = []):
    try:
        deleted_count = delete_news(ids)
        return deleted_count
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))  
    
@router.post("/file-data")
async def upload_file_data(file: UploadFile = File(...), catalog_id:str = "" ,authorize: AuthJWT = Depends()):
    # authorize.jwt_required()
    # user_id = ObjectId(authorize.get_jwt_subject())
    if not os.path.exists(f"static/{catalog_id}"):
        os.mkdir(f"static/{catalog_id}")
    try:
        content = await file.read()
        path = f"static/{catalog_id}/{file.filename}"
        with open(path, "wb") as f:
            f.write(content)
        add_file(path, catalog_id, file.filename)
        return path
    except Exception as error:
        traceback.print_exc()
        return HTTPException(
            status_code=400,
            detail="There was an error when uploading the file",
        )
    finally:
        await file.close()

@router.post("/delete-file-data")
def delete_file_data_route(file_id:str = ""):
    try:
        file_data = get_item(file_id)
        if os.path.exists(file_data.get("file_path")):
            os.remove(file_data.get("file_path"))
        delete_file(file_id)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))