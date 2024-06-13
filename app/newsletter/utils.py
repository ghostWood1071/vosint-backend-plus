from bson.objectid import ObjectId


def newsletter_to_json(newsletter) -> dict:
    newsletter["_id"] = str(newsletter["_id"])

    if "user_id" in newsletter:
        newsletter["user_id"] = str(newsletter["user_id"])

    if "parent_id" in newsletter:
        newsletter["parent_id"] = str(newsletter["parent_id"])

    return newsletter


def newsletter_to_object_id(newsletter):
    news_samples = []
    # if "news_samples" in newsletter:
    #     if newsletter["news_samples"] is None:
    #         newsletter.pop("news_samples")
    #     else:
    #         for news in newsletter["news_samples"]:
    #             news_samples.append(ObjectId(news))
    #         newsletter["news_samples"] = news_samples

    if "user_id" in newsletter:
        if newsletter["user_id"] is None:
            newsletter.pop("user_id")
        else:
            newsletter["user_id"] = ObjectId(newsletter["user_id"])

    if "parent_id" in newsletter:
        if newsletter["parent_id"] is None:
            newsletter.pop("parent_id")
        else:
            newsletter["parent_id"] = ObjectId(newsletter["parent_id"])

    return newsletter
