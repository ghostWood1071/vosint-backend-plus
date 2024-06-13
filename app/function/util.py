from typing import *

def get_function_tree(data: List[Any], level, root) -> List[Any]:
    result = []
    for i in range(len(data)):
        if data[i]["level"] == level and (data[i]["parent_id"] == root or str(data[i]["parent_id"]) == root):
            row = data[i].copy()
            lower_level = get_function_tree(data, level + 1, row["_id"])
            is_leaf = len(lower_level) == 0
            level_result = {
                "title": row["function_name"],
                "title_eng": row["function_name_eng"],
                "key": row["_id"],
                "value": row["_id"],
                "parent_id": row["parent_id"],
                "level": row["level"],
                "url": row["url"],
                "children": lower_level,
                "sort_order": row["sort_order"],
                "is_leaf": is_leaf,
            }
            result.append(level_result)
    return result