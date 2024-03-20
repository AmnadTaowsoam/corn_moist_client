from fastapi import FastAPI, HTTPException
from moistSensorService import MoistureSensor
import uvicorn
import httpx
import configparser
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.token = None
        self.token_expiry = datetime.now()

    def set_token(self, token, expires_in=3600):
        self.token = token
        self.token_expiry = datetime.now() + timedelta(seconds=expires_in)

    def is_token_expired(self):
        return datetime.now() >= self.token_expiry

app = FastAPI()
token_manager = TokenManager()
# อ่านค่าจาก config.ini
config = configparser.ConfigParser()
config.read('config.ini')
sensor_config = config['MoistureSensor']
server_config = config['ServerCredentials']
sensorId = sensor_config.get('sensorId')

# สร้างอินสแตนซ์ของ MoistureSensor
sensor = MoistureSensor()

async def get_token():
    if token_manager.token is None or token_manager.is_token_expired():
        url = server_config['ENDPOINT'] + "/login"
        data = {
            "username": server_config['username'],
            "password": server_config['password']
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            new_token = response.json()["token"]
            # สมมติว่าเวลาหมดอายุของ token อยู่ใน response, หรือใช้ค่า default
            token_manager.set_token(new_token, expires_in=3600)  # Adjust expires_in accordingly
    return token_manager.token

async def refresh_token(token: str):
    url = server_config['ENDPOINT'] + "/refresh_token"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]

@app.get("/moisture")
async def read_moisture():
    data = sensor.read_data()
    if data is not None:
        try:
            token = await get_token()
            # ใช้ token ที่ได้จาก TokenManager
            url = server_config['url']
            headers = {"Authorization": f"Bearer {token}"}
            payload = {"sensor_id": sensorId, "moisture": data}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
    else:
        return {"error": "Failed to read data from the moisture sensor"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8007)



