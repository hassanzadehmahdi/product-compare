from openai import OpenAI
from django.conf import settings
import json

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_API_URL)

def recommend_best(state: dict) -> dict:
    products = state["scored"]

    system_prompt = "شما باید از میان محصولات زیر، بهترین گزینه را برای خرید انتخاب کنید و دلیل آن را به فارسی بنویسید."

    user_prompt = f"""
        در ادامه لیستی از محصولات به همراه امتیاز، ویژگی‌ها و نکات مثبت/منفی آمده است. لطفاً یکی از آن‌ها را به عنوان بهترین انتخاب مشخص کنید و دلیل واضح و منطقی برای انتخاب خود بیان کنید.
        
        محصولات:
        {json.dumps(products, ensure_ascii=False, indent=2)}
        
        خروجی فقط در قالب JSON فارسی:
        
        {{
          "id": "شناسه محصول انتخاب‌شده",
          "reason": "دلیل انتخاب"
        }}
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
            content = content.strip("`")  # remove all backticks
            # optionally remove language tag
            if content.startswith("json"):
                content = content[4:].strip()

        parsed = json.loads(content)

        state["output"] = {
            "comparison_details": [
                {
                    "id": p["id"],
                    "description": p.get("description", ""),
                    "features": p.get("features", []),
                    "pros": p.get("pros", []),
                    "cons": p.get("cons", []),
                    "rate": p.get("rate", 0)
                } for p in products
            ],
            "overall_description": "تمامی محصولات بررسی شدند و یکی به عنوان انتخاب برتر توصیه می‌شود.",
            "recommendation": parsed
        }

    except Exception as e:
        # fallback to max rate
        best = max(products, key=lambda x: x["rate"])
        state["output"] = {
            "comparison_details": [
                {
                    "id": p["id"],
                    "description": p.get("description", ""),
                    "features": p.get("features", []),
                    "pros": p.get("pros", []),
                    "cons": p.get("cons", []),
                    "rate": p.get("rate", 0)
                } for p in products
            ],
            "overall_description": "بر اساس امتیازدهی، یک محصول به عنوان برترین انتخاب مشخص شده است.",
            "recommendation": {
                "id": best["id"],
                "reason": f"این محصول بیشترین امتیاز ({best['rate']}) را داشته است."
            }
        }

    return state
