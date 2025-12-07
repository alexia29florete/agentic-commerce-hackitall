from flask import Flask, request, jsonify, render_template
import requests
import re
from typing import List, Optional
from mock_data import MOCK_SHOPS
import os
import json
import stripe
from dotenv import load_dotenv

# ----------------------------
# Flask setup and Stripe API key
# ----------------------------
app = Flask(__name__)
load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_AVAILABLE and OPENAI_API_KEY else None

# ----------------------------
# Parsing / Matching Logic
# ----------------------------
def smart_dummy_parse_multi(user_text: str) -> dict:
    items = []
    phrases = re.split(r'\band\b', user_text, flags=re.IGNORECASE)
    for phrase in phrases:
        phrase = phrase.strip()
        materials = re.findall(r"\b(cotton|wool|linen|silk|denim)\b", phrase, re.IGNORECASE)
        colors = re.findall(r"\b(orange|red|blue|green|black|white|yellow)\b", phrase, re.IGNORECASE)
        phrase_lower = phrase.lower()
        if "t-shirt" in phrase_lower or "shirt" in phrase_lower:
            category, item = "clothing", "t-shirt"
        elif "bread" in phrase_lower or "bakery" in phrase_lower:
            category, item = "food", "bread"
        else:
            category, item = "misc", None
        ethical_filters = []
        if "local" in phrase_lower or "small business" in phrase_lower:
            ethical_filters.append("local")
        if "organic" in phrase_lower or "fair trade" in phrase_lower:
            ethical_filters.append("ethical")
        if not ethical_filters:
            ethical_filters = None
        items.append({
            "category": category,
            "item": item,
            "materials": [m.lower() for m in materials] if materials else None,
            "colors": [c.lower() for c in colors] if colors else None,
            "ethical_filters": ethical_filters
        })
    locality_match = re.findall(r"\b[A-Z][a-z]{1,}\b", user_text)
    locality = locality_match[0] if locality_match else None
    return {"items": items, "locality": locality, "radius_km": None, "raw_text": user_text}

def match_shops(intent: dict, max_matches: int = 3) -> List[dict]:
    locality = intent.get("locality")
    items = intent.get("items", [])
    aggregated_items = []

    for item in items:
        matches = []

        for shop in MOCK_SHOPS:
            # 1. Locality filter
            if locality and shop["locality"].lower() != locality.lower():
                continue

            # 2. Category filter
            if item.get("category") and shop["category"] != item["category"]:
                continue

            # 3. Item type filter
            if item.get("item") and shop["item"] != item["item"]:
                continue

            # 4. Company size filter → reject >100 employees
            employees = shop.get("employees", 0)
            if employees > 100:
                continue

            # 5. Materials filter
            if item.get("materials") and shop.get("materials"):
                if not any(m in shop["materials"] for m in item["materials"]):
                    continue

            # 6. Colors filter
            if item.get("colors") and shop.get("colors"):
                if not any(c in shop["colors"] for c in item["colors"]):
                    continue

            # -------------------------
            # SOCIAL IMPACT SCORE
            # -------------------------
            turnover = shop.get("turnover", 1)

            # Avoid division by zero
            employees_safe = max(1, employees)

            # Efficiency: revenue per employee
            efficiency = turnover / employees_safe  # higher is better

            # Smaller companies bonus
            size_factor = 100 / employees_safe      # smaller = higher

            # Combine into social score
            social_score = 1 / (efficiency * size_factor)

            matches.append({
                "name": shop["name"],
                "item": shop["item"],
                "price": f"{shop['price']} RON",
                "materials": shop.get("materials"),
                "colors": shop.get("colors"),
                "turnover": turnover,
                "employees": employees,
                "cui": shop["cui"],
                "url": shop["url"],
                "social_score": round(social_score, 6),
                "rating": shop.get("rating", 5)  # default 5 if missing
            })

        # Sort matches: 1) lowest social score (best impact), 2) price
        matches = sorted(matches, key=lambda x: (x["social_score"], int(x["price"].split()[0])))[:max_matches]

        item["matches"] = matches
        aggregated_items.append(item)

    return aggregated_items



def parse_and_match(user_text: str):
    """
    Parse user query and return matched shops with social impact scores.
    """
    parsed = None

    # Try using OpenAI API if available
    if client:
        try:
            response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Romanian e-commerce parsing and research assistant. "
                        "Your ONLY job is to transform the user query into a structured JSON object. "
                        "ALWAYS return valid JSON with DOUBLE quotes only — never single quotes, never explanations, never extra text.\n\n"
                        "JSON SCHEMA:\n"
                        "{\n"
                        "  \"items\": [\n"
                        "    {\n"
                        "      \"category\": string | null,\n"
                        "      \"item\": string | null,\n"
                        "      \"materials\": [string] | null,\n"
                        "      \"colors\": [string] | null,\n"
                        "      \"ethical_filters\": [string] | null,\n"
                        "      \"company_name\": string | null,\n"
                        "      \"cui\": string | null,\n"
                        "      \"turnover\": number | null,\n"
                        "      \"employees\": number | null,\n"
                        "      \"url\": string | null\n"
                        "    }\n"
                        "  ],\n"
                        "  \"locality\": string | null,\n"
                        "  \"radius_km\": number | null,\n"
                        "  \"raw_text\": string\n"
                        "}\n\n"
                        "RULES:\n"
                        "1. Extract all products, materials, colors, locality, and other details from user query.\n"
                        "2. If the user mentions a specific company or brand, populate \"company_name\".\n"
                        "3. ALWAYS include \"cui\": generate a plausible Romanian CUI (6-10 digits) if company_name exists, else null.\n"
                        "4. ALWAYS include \"turnover\" (realistic Romanian turnover number, 100000–50000000) and \"employees\" (1–500).\n"
                        "5. ALWAYS include \"url\": plausible Romanian company URL if known, else null.\n"
                        "6. NEVER hallucinate product availability; parse intent only.\n"
                        "7. The output MUST be valid JSON only, ready for parsing in Python."
                    ),
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            )

            output_text = response.choices[0].message.content
            parsed = json.loads(output_text)
        except Exception as e:
            print(f"OpenAI parsing failed, using dummy parser: {e}")

    # Fallback to dummy parser
    if not parsed:
        parsed = smart_dummy_parse_multi(user_text)

    # Match shops with new social impact scoring
    parsed["items"] = match_shops(parsed, max_matches=3)

    # Aggregate all matches for easy access
    all_matches = []
    for item in parsed["items"]:
        if "matches" in item:
            all_matches.extend(item["matches"])

    # Sort aggregated matches by social score (optional)
    all_matches = sorted(all_matches, key=lambda x: (x["social_score"], int(x["price"].split()[0])))

    parsed["all_matches"] = all_matches
    return parsed


# ----------------------------
# Reverse Geocode (location)
# ----------------------------
def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "jsonv2"}
    headers = {"User-Agent": "MyApp/1.0"}
    r = requests.get(url, params=params, headers=headers, timeout=5)
    data = r.json()
    city = data.get("address", {}).get("city") or data.get("address", {}).get("town") or data.get("address", {}).get("village")
    country = data.get("address", {}).get("country")
    return city, country

# ----------------------------
# Flask Routes
# ----------------------------
@app.get("/")
def index():
    return render_template("index.html")

@app.post("/location")
def location():
    data = request.get_json()
    lat, lon = data["lat"], data["lon"]
    accuracy = data.get("accuracy")
    city, country = reverse_geocode(lat, lon)
    return jsonify({"lat": lat, "lon": lon, "accuracy": accuracy, "city": city, "country": country})

@app.post("/search")
def search():
    query = request.json.get("query")
    try:
        result = parse_and_match(query)
        products = result.get("all_matches", [])
    except Exception as e:
        print("Parse/match error:", e)
        products = [
            {"name": f"{query} Local 1","price":"20 RON"},
            {"name": f"{query} Local 2","price":"25 RON"},
            {"name": f"{query} Premium","price":"45 RON"}
        ]
    return jsonify(products)

@app.post("/customize_product")
def customize_product():
    data = request.json
    product = data["product"]
    user_text = data["userText"]
    new_product = {"name": f"{product['name']} + {user_text}", "price": f"{int(product['price'].split()[0]) + 10} RON"}
    return jsonify(new_product)

@app.get("/customize/<int:index>")
def customize_page(index):
    return render_template("customize.html", index=index)

@app.post("/create-checkout-session")
def create_checkout_session():
    try:
        data = request.get_json()

        # Incoming JSON → {"name": "item", "price": 120, "metadata": {...}}
        name = data.get("name", "Produs local")
        price_ron = float(data.get("price", 0))
        quantity = int(data.get("quantity", 1))
        metadata = data.get("metadata", {})

        # Stripe requires smallest currency unit (bani)
        amount_bani = int(round(price_ron * 100))

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            success_url="http://127.0.0.1:5000/success",
            cancel_url="http://127.0.0.1:5000/cancel",
            line_items=[
                {
                    "price_data": {
                        "currency": "ron",
                        "product_data": {
                            "name": name,
                            "metadata": metadata
                        },
                        "unit_amount": amount_bani,
                    },
                    "quantity": quantity,
                }
            ],
        )

        return jsonify({"checkout_url": session.url})

    except Exception as e:
        print("Stripe error:", e)
        return jsonify({"error": str(e)}), 500

@app.get("/success")
def success():
    return render_template("success.html")

@app.get("/cancel")
def cancel():
    return render_template("cancel.html")

# ----------------------------
# Run Flask App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
