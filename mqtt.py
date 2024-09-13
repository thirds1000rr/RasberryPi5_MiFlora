import threading
import json
import paho.mqtt.client as mqtt
import ssl
import time
import pytz
import asyncio
from ble_scanner import main
from read_sensor import read_mi_flora_data
from gpio import GPIOController
from utilities.notify import LineController
from datetime import datetime, timedelta



data_storage ={}
gmt7_timezone = pytz.timezone('Asia/Bangkok')

class TimeSeries : 
    def collectData(self , sensor_id, payload):
        try:
            if sensor_id not in data_storage:
                data_storage[sensor_id] = []
                data_storage[sensor_id].append({
                "temperature": payload["temperature"],
                "moisture": payload["moisture"],
                "timestamp": payload["timestamp"]
            })
            else:
                data_storage[sensor_id].append({
                    "temperature": payload["temperature"],
                    "moisture": payload["moisture"],
                    "timestamp": payload["timestamp"]
                })

            print(f"Structure of data collected: {data_storage}")
            return True
        except Exception as e:
            print(f"ERR collect payload: {e}")


class MQTTClient:
    def __init__(self, broker_url, broker_port, username, password):
        self.client = mqtt.Client(client_id="")
        self.client.username_pw_set(username, password)
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.read_publish_flag = True
        self.thread_list = []

    def connect(self):
        try:
            self.client.connect(self.broker_url, self.broker_port)
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
            client.subscribe("scan_sensor", qos=1)
            client.subscribe("userValid", qos=1)
            client.subscribe("state", qos=1)

        else:
            print(f"Connection failed with code {rc}")

    def on_publish(self, client, userdata, mid):
        print(f"Message {mid} published")

    def calculateAndPublishAverages(self , data_json = None):
        try:
            print(f"Data count  : {len(data_storage)}")
            now = datetime.now()
            ten_minutes_ago = now-timedelta(minutes=1)
            # ten_minutes_ago = ten_minutes_ago.isoformat()
            print(f"ten_minutes_ago {ten_minutes_ago} ")
        
            for sensor_id, data_list in data_storage.items():
                if data_list:
                # Filter data within the last 10 minutes
                    # print(f"ten_minutes_ago: {ten_minutes_ago}")
                    avg_data_time_check = [d for d in data_list if d['timestamp'] >= ten_minutes_ago]
                    print(f"Time calculate : {ten_minutes_ago}")
                    avg_temp = None
                    avg_humid = None
                    print(f"Data AVG TIME CHECK : {avg_data_time_check}")
                    if avg_data_time_check:
                    #for in arr to check is not none
                        valid_temps = [d['temperature'] for d in avg_data_time_check if d['temperature'] is  not None]
                        valid_humids = [d['moisture'] for d in avg_data_time_check if d['moisture'] is not None]
                    # Calculate averages
                        # print(f"Sensor : {sensor_id} \n,Temp : {valid_temps} length:{len(valid_temps)} \n, Humid : {valid_humids} length:{len(valid_humids)}\n")

                        avg_temp = sum(valid_temps) / len(valid_temps) if valid_temps else 0
                        
                        avg_humid = sum(valid_humids) / len(valid_humids) if valid_humids else 0
                        print(f"AVG_TEMP : {avg_temp} , AVG_HUMID : {avg_humid}")

                        print(f"{avg_temp} , {avg_humid}")
                        data_json = json.dumps({
                                "sensor_id": sensor_id,
                                "average_temperature": avg_temp,
                                "average_humidity": avg_humid,
                                "timestamp": datetime.now()
                            })
                    
                    # Publish to MQTT
                    try:
                        if data_json : 
                            print(f"Data before publish :  {data_json}")
                            # Prepare JSON payload for MQTT
                            
                            if self.publish("timeSeries",data_json):
                                print(f"Publish for Sensor {sensor_id}: {data_json}")
                                # Clear data list after published
                                data_storage[sensor_id] = []
                            
                    except Exception as e :
                        print(f"Err while publish Average {e} data will not save")
            print(f"Don't have data to calculate in time: {data_storage}")
        except Exception as e:
            print(f"Error calculate and publish: {e}")
            return True

    def on_message(self, client, userdata, msg):
        try : 
            topic = msg.topic
            payload = msg.payload.decode("utf-8")
            
            print(f"Received message on topic '{topic}': {payload}")
            
            if topic == "scan_sensor":
                print("Received scan_sensor")
                self.handle_scan_sensor(payload)
            elif topic == "userValid":
                read_publish_thread = threading.Thread(target=self.read_and_publish, args=(client, payload))
                self.thread_list.append(read_publish_thread)
            elif topic == "state":
                parseJson = json.loads(payload)
                instance_GpioController = GPIOController()
                user_id = parseJson["user_id"]
                return_topic="/state"
                topic = user_id+return_topic
                result_gpio = instance_GpioController.decision(parseJson)
                if result_gpio:
                    self.publish(topic,json.dumps(True))
                else:
                    self.publish(topic,json.dumps(False))
                # elif isinstance(result_gpio,int):
                #     print(f"This Gpio : {result_gpio} , Successfully operation.")
                #     self.publish(update_topic,result_gpio)
        except Exception  as  e :
            print(f"Err receive msg{e}")

    def publish(self, topic, message):
        try:
            if not self.client.is_connected():
                print("Client not connected, trying to reconnect...")
                self.client.reconnect()
            result = self.client.publish(topic, message, qos=1)
            print("Publish")
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to topic: {topic}, Message: {message}")
                return True
            else:
                print(f"Failed to publish message to topic '{topic}', result code: {result.rc}")
                return False
        except Exception as e:
            print(f"Error publishing message: {e}")
            return False
        
    def handle_scan_sensor(self, payload):
        if payload == "true":
            time.sleep(1)
            result = asyncio.run(main())
            print("Scan result:", result)
            payload_str = json.dumps(result)
            print("Payload to publish:", payload_str)

            try:
                publish_event = threading.Event() #Thread Event 

                def publish_and_signal(client, payload_str, publish_event):
                    topic = "sensors_lists"
                    success = client.publish(topic, payload_str)
                    
                    if success.rc == 0:  # Check the MQTT success code
                        print("Published successfully")
                        publish_event.set()  # Signal main thread when publish is done
                    else:
                        print(f"Failed to publish, result code: {success.rc}")

                publish_event = threading.Event() #Thread Event 
                publish_thread = threading.Thread(target=publish_and_signal, args=(self.client, payload_str, publish_event))
                publish_thread.start()

            except Exception as e:
                print(f"Error during publish: {e}")

    def read_and_publish(self, client, payload , temperature_threshold  = 31 , moisture_thershold = 28 ):
        try:
            data_detail = json.loads(payload)
            print(f"Received JSON payload: {data_detail}")
            
            for user in data_detail:
                username = user["username"]
                sensors = user["sensors"]
                data = []  # Reset data list every time when start with new user

                for sensor in sensors:
                    mac_sensor = sensor['macAddress']
                    id_sensor = sensor['id']
                    print(f"Processing sensor: {sensor}")
                    try:
                        result = read_mi_flora_data(mac_sensor)
                        print("before next ")
                        data.append(result)
                        
                       
                    except Exception as e:
                        print(f"Error reading sensor {sensor}: {e}")
                        time.sleep(2)  # Wait before retrying
                topic = f"{username}/flora"
                try:
                    
                    # TimeSeriesInstance = TimeSeries()
                    # TimeSeriesInstance.collectData(id_sensor, result)
                    if self.publish(topic, json.dumps(data)):
                        print(f"Published data")
                except Exception as e:
                    print(f"Failed to publish data to topic '{topic}': {data}")
                    print(e)
                time.sleep(2)  # Sleep 2 seconds before reading for the next user
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as err:
            print(f"Unexpected error: {err}")
    


class MainApp:
    def __init__(self):
        self.exit_flag = False
        self.mqtt_client = MQTTClient(
            broker_url="e076141ea6a943a5b775dae136735d83.s1.eu.hivemq.cloud",
            broker_port=8883,
            username="third",
            password="Third0804151646"
        )

    def update_gpio(self,gpio,topic ="state_update"):
        if self.mqtt_client.publish(gpio,topic) : 
            print(f"Update Gpio : {gpio} to database after exceed to time duration")
    def start(self):
        self.mqtt_client.connect()
        msg_start = LineController()
        msg_start.lineNotify("Raspberry Pi Start up ")
        while not self.exit_flag:
            self.mqtt_client.calculateAndPublishAverages()
            print("Main application is running...")
            print(f"Length of thread list: {len(self.mqtt_client.thread_list)}")
            for thread in self.mqtt_client.thread_list:
                thread.start()
                thread.join()
                self.mqtt_client.thread_list.remove(thread)
            time.sleep(3)


