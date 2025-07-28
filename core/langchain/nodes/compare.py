from openai import OpenAI
from django.conf import settings
import json

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_URL)

def compare_products(state: dict) -> dict:
    products = state["enriched"]
    params = state["input"].get("params", [])

    system_prompt = "شما یک دستیار تحلیل‌گر محصولات هستید که ویژگی‌های چند محصول را بر اساس معیارهای مشخص شده با هم مقایسه می‌کنید."

    user_prompt = f"""
        لیست زیر شامل مشخصات چند محصول به همراه ویژگی‌ها، نکات مثبت و منفی اولیه است. لطفاً بر اساس معیارهای مقایسه زیر:
        {', '.join(params)}
        
        برای هر محصول موارد زیر را تولید کنید:
        - توضیح کوتاه از وضعیت محصول بر اساس مقایسه
        - تکمیل و بهبود pros و cons اگر لازم است
        
        محصولات:
        {json.dumps(products, ensure_ascii=False, indent=2)}
        
        خروجی فقط در قالب JSON فارسی زیر:
        
        [
          {{
            "id": "شناسه محصول",
            "description": "توضیح تحلیلی محصول",
            "features": [...],
            "pros": [...],
            "cons": [...]
          }},
          ...
        ]
        """

    try:
        response = openai_client.chat.completions.create(
            model=settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )

        content = response.choices[0].message.content

        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()

        parsed = json.loads(content)
        state["compared"] = parsed

    except Exception as e:
        # fallback: use previous data as-is
        state["compared"] = [
            {
                "id": p["id"],
                "description": "تحلیل در دسترس نیست.",
                "features": p.get("features", []),
                "pros": p.get("pros", []),
                "cons": p.get("cons", [])
            } for p in products
        ]

    return state
