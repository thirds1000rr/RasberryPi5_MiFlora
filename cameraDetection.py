import torch
import cv2
import numpy as np
import json
import os
import sys
import time
from datetime import datetime
import yaml
from picamera2 import Picamera2
import paho.mqtt.client as mqtt
import warnings
from base64 import b64encode , b64decode
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
# from utilities.notify import LineController
warnings.filterwarnings("ignore", category=FutureWarning, message=".*torch.cuda.amp.autocast.*")



class MQTTClient:
    def __init__(self, broker_url, broker_port, username, password):
        self.client = mqtt.Client(client_id="")
        self.client.username_pw_set(username, password)
        self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.connect()

    def connect(self):
        try:
            self.client.connect(self.broker_url, self.broker_port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            print(f"Error connecting to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_publish(self, client, userdata, mid):
        print(f"Message {mid} published")

    def publish(self, topic, message):
        try:
            if not self.client.is_connected():
                print("Client not connected, trying to reconnect...")
                self.client.connect()  # Connect using the instance method

            result = self.client.publish(topic, message, qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to topic: {topic}, Message: {message}")
                return True
            else:
                print(f"Failed to publish message to topic '{topic}', result code: {result.rc}")
                return False
        except Exception as e:
            print(f"Error publishing message: {e}")
        return False
    
class YOLODetector:
    def __init__(self, model_path, repo_path, device , mainapp, yaml_path):
        self.device = device
        self.model_path = model_path
        self.repo_path = repo_path
        self.class_names = self.load_class_names(yaml_path)
        self.model = self.load_model()
        self.camera_matrix = np.array([[630.0, 0, 320.0], [0, 630.0, 240.0], [0, 0, 1]])
        self.dist_coeffs = np.array([-0.2, 0.1, 0, 0, 0])
        self.prev_detections = []
        self.main_app_instance = mainapp
        self.base64_json

    def load_class_names(self, config_path):
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config['names']
    

    def load_model(self):
        try:
            model = torch.hub.load(self.repo_path, 'custom', path=self.model_path, source='local')
            return model.to(self.device).eval()
        except Exception as e:
            print(f"Error loading model: {e}")
            sys.exit(1)

    def detect_objects(self, frame):
        undistorted_frame = cv2.undistort(frame, self.camera_matrix, self.dist_coeffs, None, self.camera_matrix)
        img = cv2.cvtColor(undistorted_frame, cv2.COLOR_BGR2RGB)
        results = self.model(img)
        results = results.pandas().xyxy[0]

        current_detections = []
        for index, row in results.iterrows():
            x1, y1, x2, y2, confidence, class_id = (
                int(row['xmin']),
                int(row['ymin']),
                int(row['xmax']),
                int(row['ymax']),
                row['confidence'],
                int(row['class'])
            )

            if confidence > 0.5:
                current_detections.append((class_id, (x1, y1, x2, y2)))
                if not self.is_same_object((class_id, (x1, y1, x2, y2))):
                    cv2.rectangle(undistorted_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    #map yaml name with class id 
                    class_name = self.class_names[class_id]

                    cv2.putText(undistorted_frame, f"{class_name} ({confidence:.2f})", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    self.save_img(undistorted_frame, class_name)

        self.prev_detections = current_detections.copy()
        return undistorted_frame


    def is_same_object(self, current_detection, threshold=1000):
        current_class_id, (x1, y1, x2, y2) = current_detection
        for prev_class_id, (px1, py1, px2, py2) in self.prev_detections:
            if current_class_id == prev_class_id:
                if abs(x1 - px1) < threshold and abs(y1 - py1) < threshold and abs(x2 - px2) < threshold and abs(y2 - py2) < threshold:
                    return True
        return False

    def save_img(self, picture, class_name):
        try:
            print(class_name)
            time_now = datetime.now()
            date_str = time_now.strftime('%Y-%m-%d')
            time_str = time_now.strftime('%H-%M-%S')
            name_img = f"{date_str}:{time_str}_{class_name}.jpg"

            save_dir = '/home/third/Desktop/data_enemies'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            existing_files = [f for f in os.listdir(save_dir) if os.path.isfile(os.path.join(save_dir, f))]
            image_files_count = len([f for f in existing_files if f.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))])

            if image_files_count >= 50:
                existing_files.sort(key=lambda x: os.path.getmtime(os.path.join(save_dir, x)))
                for file_to_remove in existing_files[:image_files_count - 49]:
                    os.remove(os.path.join(save_dir, file_to_remove))

            full_path = os.path.join(save_dir, name_img)
            if cv2.imwrite(full_path, picture):
                # line_instance = LineController()
                # time_split = time_str.split("-")
                # line_instance.notifyPicture(full_path, f"Found {class_name}\n Date: {date_str} \n Time: \n Hours : {time_split[0]} \n Minutes:{time_split[1]} \n Seconds:{time_split[2]}")
                res_json_base64 = self.base64_json(full_path)
                data = {
                    "type": class_name, 
                    "image": f"data:image/jpeg;base64,{res_json_base64}",
                    "file_name": name_img if name_img else None
                }
                self.main_app_instance.handle_publish(data)
                
                return full_path
            else:
                print("Error: Could not save the image.")
                return None
        except Exception as e:
            print(f"Error at save img Yolo detection{e}")


    def base64_json (self , fullpath) : 
        try : 
            with open(fullpath, 'rb') as image_file:
             base64_encoded_image = b64encode(image_file.read()).decode('utf-8')
            return base64_encoded_image
        except Exception as e :
            print(f"Err at base 64 to json {e}\n")
            return None

class MainApp:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = '/home/third/Documents/GitHub/RasberryPi4_MiFlora/yolov5/best.pt'
        self.repo_path ='/home/third/Documents/GitHub/RasberryPi4_MiFlora/yolov5'
        self.yaml_path = '/home/third/Documents/GitHub/RasberryPi4_MiFlora/yolov5/data.yaml' 
        self.yolo_detector = YOLODetector(self.model_path, self.repo_path, self.device,self ,self.yaml_path)

        self.picamera2 = Picamera2()
        self.picamera2.configure(self.picamera2.create_preview_configuration(main={"size": (640, 480)}))


        self.mqtt_client = MQTTClient(
            broker_url="e076141ea6a943a5b775dae136735d83.s1.eu.hivemq.cloud",
            broker_port=8883,
            username="third",
            password="Third0804151646"
        )
        

    def start_detection(self):
        self.picamera2.start()
        fps = 30  # Target frame rate
        frame_time = 1.0 / fps

        frame_count = 0
        start_time = time.time()

        try:
            while True:
                frame_start_time = time.time()

                frame = self.picamera2.capture_array()
                frame = self.yolo_detector.detect_objects(frame)
                # show windows with frame
                cv2.imshow('YOLO Detection', frame)

                #frame count
                frame_count += 1

                if time.time() - start_time >= 1.0:
                    print(f"FPS: {frame_count}")
                    frame_count = 0
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord('q'): 
                    break
                elapsed_time = time.time() - frame_start_time
                time.sleep(max(frame_time - elapsed_time, 0))
        except Exception as e:
            print(f"Error during real-time detection: {e}")
        finally:
            self.picamera2.close()
            cv2.destroyAllWindows()




    def handle_publish(self, data):
        topic = "enemies"
        payload_json = json.dumps(data)
        self.mqtt_client.publish(topic,payload_json)

if __name__ == "__main__":
    app = MainApp()
    app.start_detection()
