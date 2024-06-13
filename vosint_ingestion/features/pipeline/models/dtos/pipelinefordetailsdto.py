from models.dtos import BaseDto


class PipelineForDetailsDto(BaseDto):
    def __init__(self, record: dict):
        super().__init__(record)
        self.name = record["name"]
        self.cron_expr = record["cron_expr"]
        self.schema = record["schema"]
        self.logs = record["logs"]  # TODO ['running...', 'waiting...', 'finished!']
        self.enabled = record["enabled"]
        self.actived = record["actived"]
        self.source_favicon = record["source_favicon"]
        self.driver = record["driver"]

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            "name": self.name,
            "cron_expr": self.cron_expr,
            "schema": self.schema,
            "logs": self.logs,
            "enabled": self.enabled,
            "actived": self.actived,
            "source_favicon": self.source_favicon,
            "driver": self.driver,
        }
