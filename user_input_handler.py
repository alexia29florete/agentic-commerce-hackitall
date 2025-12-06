import threading
import time
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI()

class UserInput(BaseModel):
    user_text: str

class Intent(BaseModel):
    category: Optional[str]
    item: Optional[str]
    materials: Optional[List[str]]
    colors: Optional[List[str]]
    locality: Optional[str]
    radius_km: Optional[int]
    budget: Optional[float]
    ethical_filters: Optional[List[str]]
    raw_text: str

# Dummy parser
def smart_dummy_parse(user_text: str) -> dict:
    # Simple keyword-based parsing
    colors = ["orange"] if "orange" in user_text.lower() else None
    materials = ["cotton"] if "cotton" in user_text.lower() else None
    budget = 120 if "120" in user_text else None
    locality = "Cluj" if "Cluj" in user_text else None
    category = "clothing"
    item = "t-shirt"
    ethical_filters = ["local", "small_business"]
    return {
        "category": category,
        "item": item,
        "materials": materials,
        "colors": colors,
        "locality": locality,
        "radius_km": None,
        "budget": budget,
        "ethical_filters": ethical_filters,
        "raw_text": user_text
    }

@app.post("/parse_intent", response_model=Intent)
async def parse_intent(data: UserInput):
    return Intent.model_validate(smart_dummy_parse(data.user_text))

# Run server in a thread
def run_server():
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

threading.Thread(target=run_server, daemon=True).start()
time.sleep(1)  # give server a moment to start

# Test request
test_input = {"user_text": "I need a 100% cotton orange t-shirt from Cluj under 120 lei"}
response = requests.post("http://127.0.0.1:8000/parse_intent", json=test_input)
print("Response from /parse_intent endpoint:")
print(response.json())
