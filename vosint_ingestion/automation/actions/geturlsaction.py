from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo, SelectorBy
from .baseaction import BaseAction


class GetUrlsAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="get_urls",
            display_name="Get URLs",
            action_type=ActionType.COMMON,
            readme="Lấy danh sách các địa chỉ URLs trong một trang",
            param_infos=[
                ParamInfo(
                    name="by",
                    display_name="Select by",
                    val_type="select",
                    default_val=SelectorBy.CSS,
                    options=SelectorBy.to_list(),
                    validators=["required"],
                ),
                ParamInfo(
                    name="expr",
                    display_name="Expression",
                    val_type="str",
                    default_val="",
                    validators=["required"],
                ),
                ParamInfo(
                    name="origin",
                    display_name="Origin address",
                    val_type="str",
                    default_val="",
                ),
                # ParamInfo(
                #     name="replace",
                #     display_name="Delete string address",
                #     val_type="str",
                #     default_val="",
                # ),
            ],
            z_index=3,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            # TODO Put error msg to logs field (Pipeline mongo)
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["INPUT_URL"], "msg": ["Input URL"]}
            )

        #url = input_val


        by = self.params["by"]
        expr = self.params["expr"]

        #page = self.driver.goto(url)
        page = input_val

        elems = self.driver.select(page, by, expr)

        # Map from elements to urls
        urls = list(map(self.__map_to_url, elems))
        # Ignore None items
        urls = list(filter(lambda url: url is not None, urls))
        # Distinct value
        urls = list(set(urls))
        #print(urls)
        return urls

    def __map_to_url(self, elem):
        origin = self.params["origin"] if "origin" in self.params else None
        href = self.driver.get_attr(elem, "href")

        if href is None:
            return None
        if 'http://' in href or 'www.' in href or 'https://' in href:
            url = href
        else:
            url = f"{origin}{href}" if origin is not None and origin not in href else href
        return url
