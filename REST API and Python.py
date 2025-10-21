import requests

# r = requests.get("https://newsapi.org/v2/everything?qInTitle=stock%20market&from=2025-09-27&to=2025-09-28&sortBy=popularity&language=en&apiKey=890603a55bfa47048e4490069ebee18c")

# content = r.json()

# articles = content["articles"]
# print(type("articles"))

# for article in content["articles"]:
#     print("Title\n", article["title"],
#           "\nDESCRIPTION\n", article["description"])


def get_news(topic, from_date, to_date, language="en", api_key="890603a55bfa47048e4490069ebee18c"):

    url = f"https://newsapi.org/v2/everything?qInTitle={topic}&from={from_date}&to={to_date}&sortBy=popularity&language={language}&apiKey={api_key}"
    r = requests.get(url, timeout=15)
    content = r.json()

    results = []
    for article in content["articles"]:
        results.append(
            f"Title\n{article.get("title", "")},\nDESCRIPTION\n{article.get("description", "")}\n")
        return results


print(get_news("space", from_date="2025-10-20", to_date="2025-10-21"))


"""alternat code fix"""

# from datetime import datetime, timedelta
# import os, requests

# API_KEY = os.environ["NEWSAPI_KEY"]

# # last 7 days
# end = datetime.utcnow().date()
# start = end - timedelta(days=7)

# params = {
#     "qInTitle": "stock market",
#     "from": start.isoformat(),  # YYYY-MM-DD
#     "to":   end.isoformat(),
#     "sortBy": "popularity",
#     "language": "en",
#     "pageSize": 20,
# }

# r = requests.get(
#     "https://newsapi.org/v2/everything",
#     params=params,
#     headers={"X-Api-Key": API_KEY},
#     timeout=15,
# )
# data = r.json()

# if data.get("status") != "ok":
# raise RuntimeError(f"NewsAPI error: {data.get('code')} - {data.get('message')}")


# if not data.get("articles"):
#     print("No articles in the selected date window.")
# else:
#     print(data["articles"][0]["title"])
