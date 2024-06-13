from .actions import BaseAction


def get_action_infos() -> list[dict]:
    action_classes = BaseAction.__subclasses__()
    action_infos = list(
        map(lambda action_cls: action_cls.get_action_info().to_json(), action_classes)
    )
    action_infos.sort(key=lambda ai: ai["z_index"])
    return action_infos


def get_action_info(name) -> dict:
    action_infos = get_action_infos()
    action_info = next(filter(lambda ai: ai["name"] == name, action_infos), None)
    return action_info
