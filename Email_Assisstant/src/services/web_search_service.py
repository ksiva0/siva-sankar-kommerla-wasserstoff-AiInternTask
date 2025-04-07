# Email_Assistant/src/services/web_search_service.py

import requests
import os

SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")


def perform_web_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": SEARCH_API_KEY, "cx": SEARCH_ENGINE_ID, "q": query}
    res = requests.get(url, params=params).json()
    return res.get("items", [])[:3]
