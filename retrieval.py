from dotenv import load_dotenv
import os
import requests

load_dotenv()

def search_google_cse(query: str, num_results=5) -> list:
    api_key = os.getenv("GOOGLE_SEARCH_1")
    cx = os.getenv("GOOGLE_CX_1")

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": cx,
        "num": num_results
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [
                {
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", "")
                }
                for item in data.get("items", [])
            ]
        else:
            print("Google CSE error:", response.status_code, response.text)
            return []
    except Exception as e:
        print("Google CSE connection error:", e)
        return []
