import os
import openai
from django.conf import settings
from openai import OpenAI
from typing import Dict

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_URL)

def extract_features(state: Dict) -> Dict:
    posts = state["input"]["posts"]
    extracted = []

    for post in posts:
        product_data = post["data"]
        messages = product_data.get("messages", [])

        system_prompt = "تو یک دستیار تحلیل‌گر هستی و باید از اطلاعات ساختار یافته و پیام‌ها، ویژگی‌های محصول را استخراج کنی."

        full_prompt = f"""
            شما یک دستیار هوش مصنوعی هستید که وظیفه دارد اطلاعات مربوط به یک محصول را از توضیحات و پیام‌های گفتگو استخراج و دسته‌بندی کند.
            
            اطلاعات خام محصول:
            {product_data}
            
            پیام‌ها:
            {messages}
            
            لطفاً خروجی زیر را فقط به صورت JSON فارسی ارائه بده:
            
            {{
              "description": "خلاصه‌ای از محصول",
              "features": ["ویژگی ۱", "ویژگی ۲", ...],
              "pros": ["نکات مثبت"],
              "cons": ["نکات منفی"]
            }}
        """

        response = openai_client.chat.completions.create(
            model=settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.4
        )

        try:
            content = response.choices[0].message.content

            # Remove triple backticks and optional 'json' tag
            content = content.strip()
            if content.startswith("```"):
                content = content.strip("`")
                if content.startswith("json"):
                    content = content[4:].strip()

            # Parse raw JSON string if necessary
            import json
            parsed = json.loads(content)

            extracted.append({
                "id": post["id"],
                "description": parsed.get("description", ""),
                "features": parsed.get("features", []),
                "pros": parsed.get("pros", []),
                "cons": parsed.get("cons", []),
            })

        except Exception as e:
            # Fallback in case of parsing error
            extracted.append({
                "id": post["id"],
                "description": product_data.get("description", ""),
                "features": ["خطا در استخراج ویژگی"],
                "pros": [],
                "cons": []
            })

    state["extracted"] = extracted
    return state
