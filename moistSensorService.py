from pyModbusTCP.client import ModbusClient
import threading
import time
import configparser
import logging
import warnings
from paho.mqtt import client as mqtt_client

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
        self.sensorId = sensor_config.get('sensorId')

        self.client = ModbusClient(host=self.host, port=self.port, auto_open=True)

        # MQTT Configuration
        mqtt_config = self.config['MQTT']
        self.mqtt_broker = mqtt_config.get('broker')
        self.mqtt_port = mqtt_config.getint('port')
        self.mqtt_topic = mqtt_config.get('topic')
        self.mqtt_client_id = f'python-mqtt-{self.sensorId}'

    def mqtt_connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logging.info("Connected to MQTT Broker!")
            else:
                logging.error("Failed to connect, return code %d\n", rc)

        self.mqtt_client = mqtt_client.Client(self.mqtt_client_id)
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port)
        self.mqtt_client.loop_start()

    def read_data_and_publish(self):
        try:
            while True:
                data = self.client.read_holding_registers(self.address, self.num_registers)
                if data and data[6] == 1:
                    self.mqtt_client.publish(self.mqtt_topic, str(data[0]))
                elif data and data[6] == 0:
                    break  # หยุดการส่งข้อมูล
                time.sleep(1)  # รอ 1 วินาทีก่อนอ่านข้อมูลครั้งถัดไป
        except Exception as e:
            logging.error(f"Error reading data from moisture sensor: {e}")

    def start(self):
        self.mqtt_connect()
        read_thread = threading.Thread(target=self.read_data_and_publish)
        read_thread.daemon = True
        read_thread.start()

if __name__ == "__main__":
    sensor = MoistureSensor()
    sensor.start()
