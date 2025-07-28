from openai import OpenAI
from django.conf import settings
import json

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_URL)

def score_products(state: dict) -> dict:
    products = state["compared"]

    system_prompt = "شما یک تحلیل‌گر هستید که باید محصولات را بر اساس ویژگی‌ها، نکات مثبت و منفی و تحلیل کلی آن‌ها امتیازدهی کنید."

    user_prompt = f"""
        در ادامه لیست محصولات با ویژگی‌ها، توضیحات، نکات مثبت و منفی آمده است. 
        لطفاً به هر محصول یک امتیاز بین 0 تا 10 بدهید که نشان‌دهنده کیفیت کلی و ارزش خرید آن در مقایسه با سایر محصولات باشد.
        
        محصولات:
        {json.dumps(products, ensure_ascii=False, indent=2)}
        
        خروجی فقط در قالب JSON فارسی زیر:
        
        [
          {{
            "id": "شناسه محصول",
            "rate": عدد بین 0 تا 10 (ممکن است اعشاری باشد)
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
            temperature=0.3
        )

        content = response.choices[0].message.content

        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()

        scores = json.loads(content)

        # Merge scores into product dicts
        scored = []
        for p in products:
            score_entry = next((s for s in scores if s["id"] == p["id"]), None)
            rate = float(score_entry["rate"]) if score_entry else 5.0
            p["rate"] = round(rate, 1)
            scored.append(p)

        state["scored"] = scored

    except Exception as e:
        # fallback: assign descending mock scores
        state["scored"] = [
            {**p, "rate": round(10.0 - i * 2, 1)} for i, p in enumerate(products)
        ]

    return state
