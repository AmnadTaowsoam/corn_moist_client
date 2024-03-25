from pyModbusTCP.client import ModbusClient
import threading
import time
import configparser
import logging
#from paho.mqtt import client as mqtt_client
import warnings
import requests
import json

warnings.filterwarnings('ignore')
# Logging and Configuration
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class MoistureSensor:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        sensor_config = self.config['MoistureSensor']
        
        self.host = sensor_config.get('host')
        self.port = sensor_config.getint('port')
        self.address = sensor_config.getint('address')
        self.num_registers = sensor_config.getint('num_registers')
        self.sensorid = sensor_config.get('sensorid')
        
        self.client = ModbusClient(host=self.host, port=self.port, auto_open=True)
        
    def read_data(self):
        return self.client.read_holding_registers(self.address, self.num_registers)

    def close_connection(self):
        self.client.close()

if __name__ == "__main__":
    sensor = MoistureSensor()
    moisture_percentages = []
    try:
        while True:
            data = sensor.read_data()
            if data:
                print("Raw moisture sensor data:", data)            
                moisture_percentages.extend(data)

                #แปลงข้อมูลเป็น JSON string
                json_data = json.dumps({"value":data})
                #บันทึก JSON string ลงในไฟล์
                with open("sensor_data.json", "w") as file:
                    file.write(json_data)

                response = requests.post("http://localhost:8007/moisture",data=json_data, headers={"Content-Type": "application/json"})
            else:
                print("Failed to read data from the moisture sensor")
            time.sleep(1)
    except KeyboardInterrupt:
         print("Stopped reading data from the moisture sensor")
    finally:
        sensor.close_connection()