import os
import pandas as pd
import requests
import time
from dotenv import load_dotenv
load_dotenv()

# ที่อยู่ของไฟล์ Excel
file_path = "D:\OneDrive - Betagro Public Company Limited\Project\Moisture Sensor Online\Python Code\Rev3\corn_moist_backend\Input.xlsx"

# ที่อยู่ของเซิร์ฟเวอร์ FastAPI
BACKEND_ENDPOINT = os.getenv("BACKEND_ENDPOINT")

# อ่านข้อมูลจากไฟล์ Excel
def read_excel_data(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print("Error reading Excel file:", e)
        return None

# ส่งข้อมูล JSON ไปยังเซิร์ฟเวอร์ FastAPI
def send_data_to_server(data):
    try:
        response = requests.post(BACKEND_ENDPOINT, json=data)
        response.raise_for_status()  # เช็คว่ามีข้อผิดพลาดหรือไม่
        print("Data sent successfully:", response.json())
    except requests.exceptions.RequestException as e:
        print("Error sending data:", e)

# ทำงานหลัก
if __name__ == "__main__":
    # อ่านข้อมูลจากไฟล์ Excel
    excel_data = read_excel_data(file_path)

    # ถ้าสามารถอ่านไฟล์ Excel ได้
    if excel_data is not None:
        # ส่งข้อมูลทีละบรรทัดไปยังเซิร์ฟเวอร์ FastAPI
        for index, row in excel_data.iterrows():
            # หารค่าในแต่ละแถวด้วย 100
            adjusted_data = row / 100
            json_data = {"data": adjusted_data.values.tolist()}  # แปลงข้อมูลเป็นลิสต์และใส่ใน JSON
            send_data_to_server(json_data)
            time.sleep(1)  # หน่วงเวลา 1 วินาที

