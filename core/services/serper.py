import requests
from django.conf import settings



def search_product_specs(query: str) -> str:
    try:
        headers = {
            "X-API-KEY": settings.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"{query}",
            "gl": "ir",
            "hl": "fa"
        }

        response = requests.post(settings.SERPER_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        snippets = []

        for result in data.get("organic", []):
            text = result.get("snippet") or result.get("title", "")
            if text:
                snippets.append(text)

        return "\n".join(snippets[:5])  # top 5 results
    except Exception as e:
        return ""
