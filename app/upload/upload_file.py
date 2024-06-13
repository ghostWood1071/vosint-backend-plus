from fastapi import APIRouter, File, UploadFile
from datetime import datetime, timedelta

router = APIRouter()


@router.post("")
async def upload(file: UploadFile = File(...)):
    try:
        content = await file.read()
        with open(f"static/{file.filename}", "wb") as f:
            f.write(content)
    except Exception as error:
        return {"message": "There was an error when uploading the file"}
    finally:
        await file.close()
    # return {"file_url": "http://0.0.0.0:6082/static/" + file.filename}, 200
    return {"file_url": f"static/{file.filename}"}, 200


@router.post("/favicon")
async def uploadFavicon(file: UploadFile = File(...)):
    now = datetime.now()
    date_current = now.strftime("%Y%m%d_%H%M%S")
    try:
        content = await file.read()
        with open(f"static/{date_current}_{file.filename}", "wb") as f:
            f.write(content)
    except Exception as error:
        return {"message": "There was an error when uploading the file"}
    finally:
        await file.close()
    # return {"file_url": "http://0.0.0.0:6082/static/" + file.filename}, 200
    return {"file_url": f"static/{date_current}_{file.filename}"}, 200
