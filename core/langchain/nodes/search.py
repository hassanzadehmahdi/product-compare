from core.services.serper import search_product_specs
from openai import OpenAI
from django.conf import settings
import json

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_URL)

def enrich_via_web(state: dict) -> dict:
    enriched = []

    for item in state["extracted"]:
        context_prompt = f"""
            با استفاده از اطلاعات زیر، یک عبارت مناسب برای جستجوی اینترنتی جهت یافتن مشخصات محصول بساز.
            لطفاً فقط یک جمله‌ی کوتاه و دقیق برای جستجو ارائه بده.

            عنوان: {item.get("title", "")}
            توضیحات: {item.get("description", "")}
            ویژگی‌ها: {', '.join(item.get("features", []))}
        """

        try:
            query_response = openai_client.chat.completions.create(
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "تو یک مولد حرفه‌ای عبارت جستجوی فارسی برای گوگل هستی."},
                    {"role": "user", "content": context_prompt}
                ],
                temperature=0.3
            )

            search_query = query_response.choices[0].message.content.strip()
        except Exception as e:
            search_query = item.get("title", "")

        # Now call serper.dev with this GPT-generated query
        search_summary = search_product_specs(search_query)

        if not search_summary:
            enriched.append(item)
            continue

        # Use GPT to extract features from snippets
        extraction_prompt = f"""
            شما باید از متن زیر مشخصات مفید محصول را به صورت ویژگی‌های مجزا استخراج کنید.

            متن:
            {search_summary}

            خروجی فقط در قالب JSON فارسی:

            {{
              "features": ["ویژگی۱", "ویژگی۲", ...]
            }}
        """

        try:
            response = openai_client.chat.completions.create(
                model=settings.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "شما یک استخراج‌کننده ویژگی هستید."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:].strip()

            parsed = json.loads(content)
            extra_features = parsed.get("features", [])
            item["features"].extend(extra_features)

        except Exception as e:
            item["features"].append("خطا در جستجوی وب")

        enriched.append(item)

    state["enriched"] = enriched
    return state
