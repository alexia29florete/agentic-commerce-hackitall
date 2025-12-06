import os
import stripe
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

app = FastAPI()


@app.post("/create-checkout-session")
def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "ron",
                    "product_data": {"name": "Produs local"},
                    "unit_amount": 5000,  # 50 lei
                },
                "quantity": 1,
            }
        ],
        success_url="http://127.0.0.1:8000/success",
        cancel_url="http://127.0.0.1:8000/cancel",
    )

    return {"checkout_url": session.url}


@app.get("/success")
def success():
    return {"message": "Plata a fost efectuata cu succes!"}

@app.get("/cancel")
def cancel():
    return {"message": "Plata a fost anulata sau utilizatorul a inchis pagina."}
