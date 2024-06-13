from automation.utils import get_action_infos

from .services import PipelineService


class PipelineController:
    def __init__(self):
        self.__pipeline_service = PipelineService()

    def get_action_infos(self):
        action_infos = get_action_infos()

        return {"success": True, "payload": action_infos}

    def get_all(self):
        # Execution at service
        data = self.__pipeline_service.get_all()

        return data

    def get_pipeline_by_id(self, id: str):
        # Execution at service
        pipeline_dto = self.__pipeline_service.get_pipeline_by_id(id)

        # Cast dto to dict object
        pipeline_obj = pipeline_dto.to_dict() if pipeline_dto else None

        return {"success": True, "payload": pipeline_obj}

    def get_pipelines(
        self, text_search, enabled, actived, order, page_number, page_size
    ):
        # Receives request data
        # text_search = request.args.get('text_search')
        # enabled = request.args.get('enabled')
        if enabled in ["0", "1"]:
            enabled = True if enabled == "1" else False
        # actived = request.args.get('actived')
        if actived in ["0", "1"]:
            actived = True if actived == "1" else False
        # order = request.args.get('order')
        # order = request.args.get('order')
        # page_number = request.args.get('page_number')
        page_number = int(page_number) if page_number is not None else None
        # page_size = request.args.get('page_size')
        page_size = int(page_size) if page_size is not None else None

        # Execution at service
        pipeline_dtos, total_records = self.__pipeline_service.get_pipelines(
            text_search=text_search,
            enabled=enabled,
            actived=actived,
            order=order,
            page_number=page_number,
            page_size=page_size,
        )

        # Cast list of dtos to dict objects
        pipeline_objs = list(map(lambda p_dto: p_dto.to_dict(), pipeline_dtos))

        return {
            "success": True,
            "payload": pipeline_objs,
            "metadata": {"total_records": total_records},
        }

    def put_pipeline(self, pipeline_obj):
        # Receives request data
        # pipeline_obj = request.json

        # TODO Validate input request

        # Execution at service
        pipeline_id = self.__pipeline_service.put_pipeline(pipeline_obj)

        if not pipeline_id:
            return {"success": False}

        return {"success": True, "payload": pipeline_id}

    def clone_pipeline(self, from_id: str):
        # Execution at service
        pipeline_id = self.__pipeline_service.clone_pipeline(from_id)

        if not pipeline_id:
            return {"success": False}

        return {"success": True, "payload": pipeline_id}

    def delete_pipeline_by_id(self, id: str):
        # Execution at service
        success = self.__pipeline_service.delete_pipeline_by_id(id)

        return {"success": success}

    # def get_data_crawled(self):
    #     # Receives request data
    #     tbl_name = request.args.get('tbl_name')
    #     # TODO Receive params from client

    #     # Execution at service
    #     records, total_records = self.__pipeline_service \
    #         .get_data_crawled(tbl_name=tbl_name)

    #     return make_response(
    #         jsonify({
    #             'success': True,
    #             'payload': records,
    #             'metadata': {
    #                 'total_records': total_records
    #             }
    #         })
    #     )
