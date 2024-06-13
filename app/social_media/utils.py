def object_to_json(object) -> dict:
    object["_id"] = str(object["_id"])

    return object
