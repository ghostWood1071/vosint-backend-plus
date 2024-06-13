from fastapi import APIRouter
from typing import *
from .models import Catalog
from .services import *
import traceback
from fastapi import HTTPException

router = APIRouter()

@router.get("/get-catalogs")
def route_get_catalogs(search_text:str="", page_size:int=10, page_index:int=1)->Any:
    try: 
        data = get_catalogs(search_text, page_size, page_index)
        
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-catalog-by-id")
def route_get_catalog_by_id(catalog_id:str)->Catalog:
    try: 
        data = get_catalog(catalog_id)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.get("/get-catalog-dropdown")
def route_get_catalog_dropdown()->Any:
    try: 
        data = get_catalog_dropdown()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))
    
@router.post("/insert-catalog")
def route_insert_catalog(catalog: Catalog)->str:
    try: 
        data = insert_catalog(catalog.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/update-catalog")
def route_update_catalog(catalog: Catalog)->int:
    try: 
        data = update_catalog(catalog.catalog_id, catalog.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))

@router.post("/delete-catalog")
def route_delete_catalog(catalog_ids:list[str])->int:
    try: 
        data = delete_catalogs(catalog_ids)
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail = str(e))