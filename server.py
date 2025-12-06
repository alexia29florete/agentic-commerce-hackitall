from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# ---------------------------
# LOCATIE (reverse geocode)
# ---------------------------
def reverse_geocode(lat, lon):
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "jsonv2"}
    headers = {"User-Agent": "MyApp/1.0"}
    
    r = requests.get(url, params=params, headers=headers, timeout=5)
    data = r.json()

    city = data.get("address", {}).get("city") or \
           data.get("address", {}).get("town") or \
           data.get("address", {}).get("village")
    country = data.get("address", {}).get("country")
    return city, country

# ---------------------------
# PAGINA PRINCIPALA
# ---------------------------
@app.get("/")
def index():
    return render_template("index.html")

# ---------------------------
# API: /location
# ---------------------------
@app.post("/location")
def location():
    data = request.get_json()
    lat = data["lat"]
    lon = data["lon"]
    accuracy = data.get("accuracy")

    city, country = reverse_geocode(lat, lon)
    return jsonify({"lat": lat, "lon": lon, "accuracy": accuracy, "city": city, "country": country})

# ---------------------------
# API: /search (produse mock)
# ---------------------------
@app.post("/search")
def search():
    query = request.json.get("query")
    products = [
        {"name": f"{query} Local 1", "price": "20 EUR"},
        {"name": f"{query} Local 2", "price": "25 EUR"},
        {"name": f"{query} Premium", "price": "45 EUR"}
    ]
    return jsonify(products)

# ---------------------------
# API: /customize_product (produse personalizate mock)
# ---------------------------
@app.post("/customize_product")
def customize_product():
    data = request.json
    product = data["product"]
    user_text = data["userText"]

    # MOCK: produs combinat
    new_product = {
        "name": f"{product['name']} + {user_text}",
        "price": f"{int(product['price'].split()[0]) + 10} EUR"
    }
    return jsonify(new_product)

# ---------------------------
# PAGINA PERSONALIZARE
# ---------------------------
@app.get("/customize/<int:index>")
def customize_page(index):
    return render_template("customize.html", index=index)

if __name__ == "__main__":
    app.run(debug=True)
