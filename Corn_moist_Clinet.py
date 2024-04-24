from pyModbusTCP.client import ModbusClient
import configparser
import time
import requests
import json
import logging

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
        self.sensorId = sensor_config.get('sensorid')  # Read sensorId from config
        
        self.client = ModbusClient(host=self.host, port=self.port, auto_open=True)
        
    def read_data(self):
        return self.client.read_holding_registers(self.address, self.num_registers)

    def close_connection(self):
        self.client.close()

if __name__ == "__main__":
    sensor = MoistureSensor()
    try:
        while True:
            data = sensor.read_data()
            if data:
                first_value_scaled = [float(data[0]) / 100.0]
                print("Scaled first moisture sensor data: ", first_value_scaled)

                # Include sensorId with the data payload
                json_data = {"data": first_value_scaled, "sensorId": sensor.sensorId}
                response = requests.post("http://127.0.0.1:8001/upload/json", json=json_data)
                print("Data posted to server:", response.status_code, response.text)
            else:
                print("Failed to read data from the moisture sensor")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped reading data from the moisture sensor")
    finally:
        sensor.close_connection()
        sensor.save_data_to_json()  # ส่งออกข้อมูลทั้งหมดเมื่อโปรแกรมจบการทำงาน