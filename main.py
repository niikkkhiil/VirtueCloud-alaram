from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Union
from pydantic import BaseModel
import os

app = FastAPI()

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

class AlarmToggle(BaseModel):
    function_name: str
    enabled: bool

alarms_state = {
    "Raju": True,
    "Shyam": False,
    "Baburao": True
}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("ui.html", "r") as f:
        return f.read()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.get("/alarms")
async def get_alarms():
    alarms = [{"name": name, "enabled": enabled} for name, enabled in alarms_state.items()]
    return {"alarms": alarms}

@app.post("/alarms/toggle")
async def toggle_alarm(data: AlarmToggle):
    if data.function_name in alarms_state:
        alarms_state[data.function_name] = data.enabled
        return {"success": True, "enabled": data.enabled}
    return {"success": False, "error": "Function not found"}