class BaseDto(object):
    def __init__(self, record: dict):
        self._id = str(record["_id"])
        self.created_at = record["created_at"]
        self.modified_at = record["modified_at"]

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
        }
