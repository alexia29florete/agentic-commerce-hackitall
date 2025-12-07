from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import stripe
from dotenv import load_dotenv
import os

# Încarcă .env care cont cheia stripe
load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()

# Montăm folderul frontend ca static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Permite cereri din orice frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return FileResponse("frontend/index.html")

@app.post("/create-checkout-session")
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            success_url="http://127.0.0.1:8000/success",
            cancel_url="http://127.0.0.1:8000/cancel",
            line_items=[
                {
                    "price_data": {
                        "currency": "ron",
                        "product_data": {"name": "Produs local"},
                        "unit_amount": 5000,
                    },
                    "quantity": 1,
                }
            ],
        )
        # url pg stripe unde clientul introduce cardul
        return {"checkout_url": session.url}

    except Exception as e:
        return {"error": str(e)}


@app.get("/success")
def success():
    return FileResponse("templates/success.html")


@app.get("/cancel")
def cancel():
    return FileResponse("templates/cancel.html")
