class SelectorBy:
    CSS = "css"
    XPATH = "xpath"

    def to_list() -> list[str]:
        return [SelectorBy.CSS, SelectorBy.XPATH]

    def to_string() -> str:
        return f"{SelectorBy.CSS}|{SelectorBy.XPATH}"
