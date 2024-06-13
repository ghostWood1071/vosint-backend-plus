from common.internalerror import *

from ..common import ActionInfo, ActionType, ParamInfo, SelectorBy
from .baseaction import BaseAction
from models import HBaseRepository, MongoRepository
import feedparser

rss_version_2_0 = {
    "author": "author",
    "link": "link",
    "pubDate": "pubDate",
    "titile": "title",
}


def feed(
    url: str = None,
    link_key: str = rss_version_2_0["link"],
    title_key: str = rss_version_2_0["titile"],
    pubDate_key: str = rss_version_2_0["pubDate"],
    author_key: str = rss_version_2_0["author"],
):
    if not url:
        raise InternalError(
            ERROR_REQUIRED, params={"code": ["FROM_ELEM"], "msg": ["From element"]}
        )
    # Parse the feed
    feed = feedparser.parse(url)
    # Loop through the entries and print the link and title of each news article
    data_feeds = []
    for entry in feed.entries:
        data_feed = {}
        try:
            link = getattr(entry, link_key)
            if link != None:
                data_feed["link"] = link
        except:
            data_feed["link"] = ""
        try:
            title = getattr(entry, title_key)
            if title != None:
                data_feed["title"] = title
        except:
            data_feed["title"] = ""
        try:
            pubDate = getattr(entry, pubDate_key)
            if pubDate != None:
                data_feed["pubDate"] = pubDate
        except:
            data_feed["pubDate"] = ""
        try:
            author = getattr(entry, author_key)
            if author != None:
                data_feed["author"] = author
        except:
            data_feed["author"] = ""

        data_feeds.append(data_feed)
        return data_feeds


class FeedAction(BaseAction):
    @classmethod
    def get_action_info(cls) -> ActionInfo:
        return ActionInfo(
            name="feed new",
            display_name="Feed new",
            action_type=ActionType.COMMON,
            readme="Lấy thông tin bài viết",
            param_infos=[
                ParamInfo(
                    name="by",
                    display_name="Select by",
                    # val_type="str",
                    val_type="select",
                    default_val=SelectorBy.CSS,
                    options=SelectorBy.to_list(),
                    validators=["required"],
                ),
                ParamInfo(
                    name="title_expr",
                    display_name="Title Expression",
                    val_type="str",
                    default_val="None",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="author_expr",
                    display_name="Author Expression",
                    val_type="str",
                    default_val="None",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="time",
                    display_name="Time Expression",
                    val_type="pubdate",
                    default_val={
                        "time_expr": "None",
                        "time_format": ["***", ",", "dd", ",", "mm", ",", "yyyy"],
                    },
                    options=["***", "dd", "mm", "yyyy", ",", ".", "/", "_", "-", " "],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="content_expr",
                    display_name="Content Expression",
                    val_type="str",
                    default_val="None",
                    validators=["required_"],
                ),
                ParamInfo(
                    name="send_queue",
                    display_name="Send_Queue",
                    val_type="select",
                    default_val="True",
                    # options=["False", "True"],
                    validators=["required_"],
                ),
                ParamInfo(
                    name="is_root",
                    display_name="Is root",
                    val_type="bool",
                    default_val="True",
                ),
                ParamInfo(
                    name="data_feed",
                    display_name="Data Feed",
                    val_type="any",
                    default_val="True",
                ),
            ],
            z_index=4,
        )

    def exec_func(self, input_val=None, **kwargs):
        if not input_val:
            raise InternalError(
                ERROR_REQUIRED, params={"code": ["URL"], "msg": ["URL"]}
            )

        url = str(input_val)
        by = self.params["by"]
        title_expr = self.params["title_expr"]
        author_expr = self.params["author_expr"]
        time_expr = self.params["time_expr"]
        content_expr = self.params["content_expr"]

        data_feeds = feed(url=url)

        for data_feed in data_feeds:
            news_info = {}
            page = self.driver.goto(url=data_feed["link"])

            check_content = False
            if title_expr != "None" and title_expr != "" and data_feed["title"] != "":
                elems = self.driver.select(page, by, title_expr)
                if len(elems) > 0:
                    news_info["data:title"] = self.driver.get_content(elems[0])
            if (
                author_expr != "None"
                and author_expr != ""
                and data_feed["author"] != ""
            ):
                elems = self.driver.select(page, by, author_expr)
                if len(elems) > 0:
                    news_info["data:author"] = self.driver.get_content(elems[0])
            if time_expr != "None" and time_expr != "" and data_feed["pubDate"] != "":
                elems = self.driver.select(page, by, time_expr)
                if len(elems) > 0:
                    news_info["data:time"] = self.driver.get_content(elems[0])
            if content_expr != "None" and content_expr != "":
                elems = self.driver.select(page, by, content_expr)
                if len(elems) > 0:
                    news_info["data:content"] = self.driver.get_content(elems[0])
                    check_content = True
                news_info["data:url"] = url
            if content_expr != "None" and content_expr != "":
                elems = self.driver.select(page, by, content_expr)
                if len(elems) > 0:
                    news_info["data:html"] = self.driver.get_html(elems[0])
            news_info["data:class_chude"] = []
            news_info["data:class_linhvuc"] = []

            news_info["source_name"] = kwargs["source_name"]
            news_info["source_host_name"] = kwargs["source_host_name"]
            news_info["source_language"] = kwargs["source_language"]
            news_info["source_publishing_country"] = kwargs["source_publishing_country"]
            news_info["source_source_type"] = kwargs["source_source_type"]

            if check_content:
                try:
                    MongoRepository().insert_one(
                        collection_name="News__", doc=news_info
                    )

                except:
                    print("An error occurred while pushing data to the database!")

        return news_info
