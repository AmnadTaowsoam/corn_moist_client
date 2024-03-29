from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import configparser
import joblib
import pandas as pd
import numpy as np
import json

app = FastAPI()

class MoistureData(BaseModel):
    value: List[int]

class ModelMoisture:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        model_config = self.config['Model_Path']
        self.loaded_model = joblib.load(r"D:\OneDrive - Betagro Public Company Limited\Project\Moisture Sensor Online\Python Code\Rev3\corn_moist_client\linear_moisture_model.pkl")

    def predict(self, data):
        # สร้าง DataFrame จากข้อมูลที่รับมา
        data_df = pd.DataFrame(data, columns=['sensorValueMoisture'])  # ให้ 'feature_name' เป็นชื่อคอลัมน์ที่โมเดลคาดหวัง
        # ทำนายผล
        prediction = self.loaded_model.predict(data_df)
        return prediction

# สร้างอินสแตนซ์ของ ModelMoisture
model_moisture = ModelMoisture()

@app.post("/moisture")
async def receive_moisture_data(request: Request):
    # อ่านข้อมูล JSON จาก request body
    data = await request.json()
    # สร้างอินสแตนซ์ของ MoistureData จากข้อมูล JSON
    moisture_data = MoistureData(**data)
    # ทำการประมวณผลหลักแรกของข้อมูล Mode F
    first_number = moisture_data.value[0]
    print(f"Received moisture sensor data Mode F: {first_number}")

    # ทำนายผลโดยใช้ model
    prediction = model_moisture.predict(moisture_data.value)

    # แปลงค่าที่ทำนายได้เป็น JSON
    prediction_json = json.dumps({"predicted_moisture": prediction[0].tolist()})

    # พิมพ์ผลลัพธ์การทำนายในรูปแบบ JSON
    print(f"Prediction JSON (Index 0): {prediction_json}")

    # ส่งคืนข้อมูลที่ได้รับและผลการทำนายในรูปแบบ JSON
    return {"status": "success", "received_first_value": first_number, "prediction_json": prediction_json}
