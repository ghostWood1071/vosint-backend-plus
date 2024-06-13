class StorageType:
    HBASE = "hbase"

    def to_list() -> list[str]:
        return [StorageType.HBASE]

    def to_string() -> str:
        return f"{StorageType.HBASE}"
