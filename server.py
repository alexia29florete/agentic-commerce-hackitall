from flask import Flask, request, jsonify, render_template
import requests
import re
from typing import List, Optional
from mock_data import MOCK_SHOPS
import os
import json

# ----------------------------
# Flask setup
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Parsing / Matching Logic
# ----------------------------
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_AVAILABLE and OPENAI_API_KEY else None

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
            if locality and shop["locality"].lower() != locality.lower(): continue
            if item.get("category") and shop["category"] != item["category"]: continue
            if item.get("item") and shop["item"] != item["item"]: continue
            if "small_business" not in shop.get("ethical", []): continue
            if item.get("materials") and shop.get("materials"):
                if not any(m in shop["materials"] for m in item["materials"]): continue
            if item.get("colors") and shop.get("colors"):
                if not any(c in shop["colors"] for c in item["colors"]): continue
            matches.append({
                "name": shop["name"],
                "item": shop["item"],
                "price": shop["price"],
                "url": shop["url"]
            })
        matches = sorted(matches, key=lambda x: x["price"])[:max_matches]
        item["matches"] = matches
        aggregated_items.append(item)
    return aggregated_items

def parse_and_match(user_text: str):
    parsed = None
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an intent-parsing AI for Romanian shopping. Return JSON with category, items, materials, colors, locality, ethical filters, radius_km, raw_text."},
                    {"role": "user", "content": user_text}
                ],
            )
            output_text = response.choices[0].message.content
            parsed = json.loads(output_text)
        except Exception as e:
            print(f"OpenAI failed, using dummy: {e}")
    if not parsed:
        parsed = smart_dummy_parse_multi(user_text)
    parsed["items"] = match_shops(parsed, max_matches=3)
    all_matches = []
    for item in parsed["items"]:
        if "matches" in item: all_matches.extend(item["matches"])
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
        for p in products:
            p["price"] = f"{p.get('price',0)} RON"
    except Exception as e:
        print("Parse/match error:", e)
        products = [{"name": f"{query} Local 1","price":"20 EUR"},
                    {"name": f"{query} Local 2","price":"25 EUR"},
                    {"name": f"{query} Premium","price":"45 EUR"}]
    return jsonify(products)

@app.post("/customize_product")
def customize_product():
    data = request.json
    product = data["product"]
    user_text = data["userText"]
    new_product = {"name": f"{product['name']} + {user_text}", "price": f"{int(product['price'].split()[0]) + 10} EUR"}
    return jsonify(new_product)

@app.get("/customize/<int:index>")
def customize_page(index):
    return render_template("customize.html", index=index)

# ----------------------------
# Run Flask App
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
