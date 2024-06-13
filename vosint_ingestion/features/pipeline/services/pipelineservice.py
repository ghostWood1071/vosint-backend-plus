from bson.objectid import ObjectId
from common.internalerror import *
from vosint_ingestion.models import HBaseRepository, MongoRepository
from scheduler import Scheduler
from utils import norm_text

from ..models.dtos import PipelineForDetailsDto, PipelineForListDto
from datetime import datetime, timedelta


class PipelineService:
    def __init__(self):
        self.__collection_name = "pipelines"
        self.__mongo_repo = MongoRepository()

        self.__hbase_repo = HBaseRepository()

    def get_pipeline_by_id(self, id: str) -> PipelineForDetailsDto:
        # Query from the database
        pipeline = self.__mongo_repo.get_one(self.__collection_name, {"_id": id})
        # Map to dto
        jobs = Scheduler.instance().get_jobs()
        pipeline["actived"] = str(pipeline["_id"]) in jobs
        pipeline["driver"] = pipeline.get("driver")

        if "source_favicon" not in pipeline:
            pipeline["source_favicon"] = ""

        pipeline_dto = PipelineForDetailsDto(pipeline) if pipeline else None
        return pipeline_dto

    def get_all(self) -> PipelineForDetailsDto:
        # Query from the database
        data = self.__mongo_repo.aggregate(
            self.__collection_name,
            [{"$project": {"_id": 1, "name": 1, "cron_expr": 1}}],
        )

        for row in data:
            row["_id"] = str(row["_id"])

        return data

    def get_pipeline_state(self, date):
        query = [
            {"$match": {"created_at": {"$gte": date}}},
            {
                "$lookup": {
                    "from": "jobstore",
                    "localField": "pipeline_id",
                    "foreignField": "_id",
                    "as": "pipeline",
                }
            },
            {
                "$addFields": {
                    "active": {"$cond": [{"$gt": [{"$size": "$pipeline"}, 0]}, 1, 0]}
                }
            },
            {
                "$group": {
                    "_id": "$pipeline_id",
                    "complete": {
                        "$max": {
                            "$cond": [
                                {"$eq": ["$log", "completed"]},
                                1,
                                {"$cond": [{"$eq": ["$active", 0]}, -1, 0]},
                            ]
                        }
                    },
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "working": {
                        "$cond": [
                            {"$gt": ["$complete", 0]},
                            1,
                            {"$cond": [{"$eq": ["$complete", 0]}, 0, -1]},
                        ]
                    },
                    "last_success": 1,
                }
            },
            {"$match"}
            # {"$sort": {"last_sucess": -1}},
        ]
        data = self.__mongo_repo.aggregate("his_log", query)
        mapping = {}
        for row in data:
            mapping[row["_id"]] = row
        return mapping

    def get_pipelines(
        self,
        text_search: str = None,
        enabled: bool = None,
        actived: bool = None,
        order: str = None,
        page_number: int = None,
        page_size: int = None,
    ) -> tuple[list[PipelineForListDto], int]:
        # Create filter conditions
        filter_spec = {}
        if text_search:
            text_search = norm_text(text_search)
            filter_spec["$or"] = [
                {"text_search": {"$regex": text_search}},
                {"schema.params.url": {"$regex": text_search}} 
            ]
            #filter_spec["text_search"] = {"$regex": text_search}

        # Filter enabled pipelines
        if isinstance(enabled, bool):
            filter_spec["enabled"] = enabled

        # Filter actived pipelines
        jobs = Scheduler.instance().get_jobs()
        if isinstance(actived, bool):
            pipeline_ids = list(map(lambda p_id: ObjectId(p_id), jobs))
            filter_spec["_id"] = (
                {"$in": pipeline_ids} if actived else {"$not": {"$in": pipeline_ids}}
            )

        pipelines, total_docs = self.__get_pipelines(
            filter_spec, order, page_number, page_size
        )

        # Map to dtos
        # Map actived from jobs to pipelines
        jobs = Scheduler.instance().get_jobs()

        def _map_active(pipeline, job_ids):
            return PipelineForListDto(
                {**pipeline, "actived": str(pipeline["_id"]) in job_ids}
            )

        pipeline_dtos = list(map(lambda p: _map_active(p, jobs), pipelines))

        return pipeline_dtos, total_docs

    def get_pipelines_for_run(
        self, ids: list[str] = None
    ) -> list[PipelineForDetailsDto]:
        # Create filter conditions
        filter_spec = {"enabled": True}

        if ids:
            ids = list(map(lambda p_id: ObjectId(p_id), ids))
            filter_spec["_id"] = {"$in": ids}

        pipelines, _ = self.__get_pipelines(filter_spec)

        # Map to dtos
        # Map actived from jobs to pipelines
        jobs = Scheduler.instance().get_jobs()

        def _map_active(pipeline, job_ids):
            return PipelineForDetailsDto(
                {
                    **pipeline,
                    "actived": str(pipeline["_id"]) in job_ids,
                    "source_favicon": str(pipeline.get("source_favicon"))
                    # if (
                    #     "source_favicon" in pipeline
                    #     and pipeline["source_favicon"] != ""
                    # )
                    # else "",
                }
            )

        pipeline_dtos = list(map(lambda p: _map_active(p, jobs), pipelines))

        return pipeline_dtos

    def get_pipelines_off(self, ids: list[str] = None):
        # Create filter conditions
        filter_spec = {"enabled": True}

        if ids:
            ids = list(map(lambda p_id: ObjectId(p_id), ids))
            filter_spec["_id"] = {"$in": ids}

        raw_pipelines, _ = MongoRepository().find(
            "pipelines", filter_spec, {"_id": 1, "cron_expr": 1}
        )
        pipelines = [
            {"_id": str(pipeline.get("_id")), "cron": pipeline.get("cron_expr")}
            for pipeline in raw_pipelines
        ]

        # Map to dtos
        # Map actived from jobs to pipelines
        job_ids = [job_id for job_id in Scheduler.instance().get_jobs()]

        pipeline_dtos = list(filter(lambda x: x.get("_id") not in job_ids, pipelines))

        return pipeline_dtos

    def get_pipelines_on(self, ids: list[str] = None):
        filter_spec = {"enabled": True}

        if ids:
            ids = list(map(lambda p_id: ObjectId(p_id), ids))
            filter_spec["_id"] = {"$in": ids}

        raw_pipelines, _ = MongoRepository().find("pipelines", filter_spec, {"_id": 1})
        pipelines = [{"_id": str(pipeline.get("_id"))} for pipeline in raw_pipelines]

        # Map to dtos
        # Map actived from jobs to pipelines
        job_ids = [job_id for job_id in Scheduler.instance().get_jobs()]

        pipeline_dtos = list(filter(lambda x: x.get("_id") in job_ids, pipelines))

        return pipeline_dtos

    def __get_pipelines(
        self,
        filter_spec: dict = {},
        order: str = None,
        page_number: int = None,
        page_size: int = None,
    ) -> tuple[list, int]:
        # Create sort condition
        order_spec = order.split(",") if order else []

        # Calculate pagination information
        page_number = page_number if page_number else 1
        page_size = page_size if page_size else 20
        pagination_spec = {"skip": page_size * (page_number - 1), "limit": page_size}
        pipelines, total_docs = self.__mongo_repo.get_many(
            collection_name=self.__collection_name,
            filter_spec=filter_spec,
            order_spec=order_spec,
            pagination_spec=pagination_spec,
        )
        # Query from the database

        # time = datetime.strftime(
        #     datetime.now() - timedelta(days=1), "%Y-%m-%d %H:%M:%S"
        # )
        # state_mapping = self.get_pipeline_state(time)
        # # pipeline_ids = [ObjectId(pl_id) for pl_id in state_mapping.keys()]
        # # filter_spec["_id"] = {"$in": pipeline_ids}

        # for pipeline in pipelines:
        #     state = state_mapping.get(str(pipeline.get("_id")))
        #     if state is not None:
        #         pipeline["working"] = state.get("working")
        #         pipeline["last_success"] = state.get("last_success")
        #     else:
        #         pipeline["working"] = 0
        #         pipeline["last_success"] = ""

        return pipelines, total_docs

    def put_pipeline(self, pipeline: dict) -> str:
        if not pipeline:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["PIPELINE"], "msg": ["Pipeline"]}
            )

        # Get the necessary fields
        norm_pipeline = self.__norm_pipeline_for_put(pipeline)

        pipeline_id = None

        # Check exists data
        existed = None
        if "_id" in norm_pipeline and norm_pipeline["_id"]:
            existed = self.__mongo_repo.get_one(
                self.__collection_name, {"_id": norm_pipeline["_id"]}
            )

        if existed is None:
            # Create text content for search
            text_search = ""
            if "name" in norm_pipeline and norm_pipeline["name"]:
                text_search += norm_text(norm_pipeline["name"]) + " "
            if text_search:
                norm_pipeline["text_search"] = text_search

            # Set default values
            norm_pipeline["schema"] = []
            norm_pipeline["logs"] = []

            # Insert
            pipeline_id = self.__mongo_repo.insert_one(
                collection_name=self.__collection_name, doc=norm_pipeline
            )
        else:
            # Recreate text content for search
            text_search = ""
            if "name" in norm_pipeline and norm_pipeline["name"]:
                text_search = norm_text(norm_pipeline["name"]) + " "
            if text_search:
                norm_pipeline["text_search"] = text_search

            # Update
            update_success = self.__mongo_repo.update_one(
                collection_name=self.__collection_name, doc=norm_pipeline
            )
            if update_success == True:
                pipeline_id = str(existed["_id"])

        return pipeline_id

    def clone_pipeline(self, from_id: str) -> str:
        # Query from the database
        pipeline = self.__mongo_repo.get_one(self.__collection_name, {"_id": from_id})

        if not pipeline:
            raise InternalError(
                ERROR_NOT_FOUND,
                params={"code": ["PIPELINE"], "msg": [f"Pipeline with id: {from_id}"]},
            )

        # Insert new pipeline into the database
        new_pipeline = pipeline.copy()
        del new_pipeline["_id"]
        new_pipeline["logs"] = []

        # Insert
        pipeline_id = self.__mongo_repo.insert_one(
            collection_name=self.__collection_name, doc=new_pipeline
        )

        return pipeline_id

    def __norm_pipeline_for_put(self, pipeline: dict) -> dict:
        # Get the necessary fields
        norm_pipeline = {}
        if "_id" in pipeline:
            norm_pipeline["_id"] = pipeline["_id"]
        if "name" in pipeline:
            norm_pipeline["name"] = pipeline["name"]
        if "cron_expr" in pipeline:
            norm_pipeline["cron_expr"] = pipeline["cron_expr"]
        if "schema" in pipeline:
            norm_pipeline["schema"] = pipeline["schema"]
        if "logs" in pipeline:
            norm_pipeline["logs"] = pipeline["logs"]
        if "enabled" in pipeline:
            norm_pipeline["enabled"] = pipeline["enabled"]
        if "source_favicon" in pipeline:
            norm_pipeline["source_favicon"] = pipeline["source_favicon"]
        if "driver" in pipeline:
            norm_pipeline["driver"] = pipeline["driver"]

        return norm_pipeline

    def delete_pipeline_by_id(self, id: str) -> bool:
        return self.__mongo_repo.delete_one(self.__collection_name, {"_id": id})

    def get_data_crawled(self, tbl_name: str) -> tuple[list[dict], int]:
        # TODO Paging page_number, page_size, order by date desc
        return self.__hbase_repo.get_many(tbl_name)
