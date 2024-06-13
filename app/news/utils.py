def news_to_json(news) -> dict:
    news["_id"] = str(news["_id"])

    if "pub_date" in news:
        news["pub_date"] = str(news["pub_date"])

    return news
