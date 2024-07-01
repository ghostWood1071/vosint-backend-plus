from fastapi import APIRouter, File, UploadFile, Form
from typing import *
from .model import SearchParams, TrainParams
from .sentiment import service as sentiment_service
import traceback
from fastapi import HTTPException
import os
import requests
from core.config import settings
import json

router = APIRouter()

@router.post("/add-sentiment-dataset")
def add_sentiment_dataset(doc_ids:List[str]=[]):
    try:
        inserted_ids = sentiment_service.add(doc_ids)
        return inserted_ids
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-sentitment-from-file")
async def add_sentiment_dataset(data_file:UploadFile = File(...)):
    try:
        path = "static/sentiment-data"
        if not os.path.exists(path):
            os.mkdir(path)
        file_path = path + "/" + data_file.filename
        with open(file_path, mode = "wb") as f:
             data = await data_file.read()
             f.write(data)      
        inserted = sentiment_service.add_from_file(file_path)
        return inserted
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/split-sentiment-data")
def split_sentiment_route(train_size:float):
    try:
        if train_size > 1:
            train_size = train_size/100
        result = sentiment_service.split(train_size)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/search")
def search_route(params: SearchParams):
    try:
        data = sentiment_service.search(**params.dict())
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e)) 

@router.get("/get-task")
def get_task_route():
    try:
        data = sentiment_service.get_task()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e)) 
    
@router.post("/train")
def train_route(train_params:TrainParams):
    try:
        data = sentiment_service.train()
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e)) 

@router.get("/get-model-name")
def get_model_name():
    try:
        res = requests.get(f"{settings.TOPIC_SENTIMENT_API}/get_model_name")
        if res.ok:
            return res.json()
        raise Exception(res.json())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/change-model")
def get_model_name(model_name:str):
    try:
        res = requests.post(f"{settings.TOPIC_SENTIMENT_API}/change_model", data={"model_name": model_name})
        if res.ok:
            return res.json()
        raise Exception(res.json())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/test-model")
async def test_model(model_name:str, dataset:UploadFile = File(...)):
    try:
        file_content = await dataset.read()
        # # # Make a POST request to another server with the file
        files = {'file_test': (dataset.filename, file_content, dataset.content_type)}
        res = requests.post(
            f"{settings.TOPIC_SENTIMENT_API}/test_model", 
            data=
                {
                    "model_name": model_name,
                },
            files=files
        )
        if res.ok:
            return res.json()
        raise Exception(res.json())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))
    
@router.post("/predict")
def predict_route(model_name: str = Form(...),
                   title: str = Form(...),
                   text: str = Form(...)):
    try:
        res = requests.post(f"{settings.TOPIC_SENTIMENT_API}/predict", data={
            "model_name": model_name,
            "title": title,
            "text": text
        })
        if res.ok:
            return res.json()
        raise Exception(res.json())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))

@router.post("/delete-model")
def get_model_name(model_name:str):
    try:
        res = requests.post(f"{settings.TOPIC_SENTIMENT_API}/delete_model", data={"model_name": model_name})
        if res.ok:
            return res.json()
        raise Exception(res.json())
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(500, str(e))

