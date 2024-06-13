from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder

from .pipelinecontroller import PipelineController

router = APIRouter()
pipeline_controller = PipelineController()


@router.get("/api/get_action_infos")
def get_action_infos():
    return JSONResponse(pipeline_controller.get_action_infos())


@router.get("/api/get_pipeline_by_id/{id}")
def get_pipeline_by_id(id: str):
    return JSONResponse(pipeline_controller.get_pipeline_by_id(id))


@router.get("/api/get_pipelines")
def get_pipelines(
    text_search=None,
    enabled=None,
    actived=None,
    order=None,
    page_number=None,
    page_size=None,
):
    return JSONResponse(
        pipeline_controller.get_pipelines(
            text_search, enabled, actived, order, page_number, page_size
        )
    )


@router.get("/api/get-all")
def get_pipelines():
    return JSONResponse(pipeline_controller.get_all())


@router.post("/api/put_pipeline")
async def put_pipeline(pipeline_obj: Request):
    print(pipeline_obj)
    return JSONResponse(
        pipeline_controller.put_pipeline(jsonable_encoder(await pipeline_obj.json()))
    )


@router.post("/api/clone_pipeline/{from_id}")
def clone_pipeline(from_id: str):
    return JSONResponse(pipeline_controller.clone_pipeline(from_id))


@router.delete("/api/delete_pipeline/{id}")
def delete_pipeline_by_id(id: str):
    return JSONResponse(pipeline_controller.delete_pipeline_by_id(id))
