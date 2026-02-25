from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import Union
from pydantic import BaseModel
import os
import boto3
from botocore.exceptions import ClientError

app = FastAPI()
lambda_client = boto3.client('lambda')

class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

class AlarmToggle(BaseModel):
    function_name: str
    enabled: bool

MONITORED_FUNCTIONS = [
    "Raju",
    "Shyam",
    "Baburao"
]

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
    alarms = []
    for func_name in MONITORED_FUNCTIONS:
        try:
            response = lambda_client.get_function_configuration(FunctionName=func_name)
            env_vars = response.get('Environment', {}).get('Variables', {})
            enabled = env_vars.get('ALARMS_ENABLED', 'true') == 'true'
            alarms.append({"name": func_name, "enabled": enabled})
        except ClientError:
            alarms.append({"name": func_name, "enabled": False})
    return {"alarms": alarms}

@app.post("/alarms/toggle")
async def toggle_alarm(data: AlarmToggle):
    try:
        response = lambda_client.get_function_configuration(FunctionName=data.function_name)
        env_vars = response.get('Environment', {}).get('Variables', {})
        env_vars['ALARMS_ENABLED'] = 'true' if data.enabled else 'false'
        
        lambda_client.update_function_configuration(
            FunctionName=data.function_name,
            Environment={'Variables': env_vars}
        )
        return {"success": True, "enabled": data.enabled}
    except ClientError as e:
        return {"success": False, "error": str(e)}