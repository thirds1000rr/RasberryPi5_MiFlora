import os
import sys
import time
import cv2
import torch
import numpy as np
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from yolov5.models.experimental import attempt_load
from yolov5.utils.general import non_max_suppression, scale_coords, xyxy2xywh
from yolov5.utils.torch_utils import select_device
from picamera2 import Picamera2
from datetime import datetime
import base64

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-time Object Detection with Camera Preview")
        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.picam2 = Picamera2()
        #Size and color format 
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))

        self.picam2.start()
        
        self.weight = "best.pt"
        self.conf = 0.8
        self.device = select_device('')
        self.model = attempt_load(self.weight, map_location=self.device)
        self.stride = int(self.model.stride.max())
        
        self.capture_path = 'detected'  

        self.image_count = 0  # Initialize image_count attribute

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 ms 

        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture_image)
        self.capture_timer.start(3000)  # Capture image every 30 seconds
    
    def capture_image(self, frame=None, save_path=None, label_box = None):
        if self.image_count >= 100:
            # If the number of images exceeds 100, remove the oldest image
            oldest_image_path = f"{self.capture_path}/detected_{time.time() - 100}.jpg"
            try:
                os.remove(oldest_image_path)
            except FileNotFoundError:
                pass

        if frame is not None and save_path is not None:
            frame_copy = frame.copy()

        if label_box is not None:
            x1, y1, x2, y2 = label_box
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            width = abs(x2 - x1)
            height = abs(y2 - y1)
            cv2.rectangle(frame_copy, (center_x - width // 2, center_y - height // 2), 
                        (center_x + width // 2, center_y + height // 2), (0, 255, 0), 2)  # Draw the centered box
            frame_copy_bgr = cv2.cvtColor(frame_copy, cv2.COLOR_RGB2BGR)
            cv2.imwrite(save_path, frame_copy_bgr)

            self.image_count += 1

    def update_frame(self):
        frame = self.picam2.capture_array()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        if frame is not None:
            frame_copy = frame.copy()
            frame_copy = cv2.cvtColor(frame_copy, cv2.COLOR_BGR2RGB)
            im = cv2.resize(frame_copy, (640, 480))
            im = im.transpose((2, 0, 1))
            im = torch.from_numpy(im).to(self.device)
            im = im.half() if self.device.type != 'cpu' else im.float()
            im /= 255.0
            if im.ndimension() == 3:
                im = im.unsqueeze(0)

            pred = self.model(im, augment=False)[0]
            pred = non_max_suppression(pred, self.conf, 0.45, classes=None, agnostic=False)
                
            if len(pred):
                for det in pred[0]:
                    *xyxy, conf, cls = det
                    box = xyxy2xywh(torch.tensor(xyxy).view(1, 4))[0].tolist()
                    
                    object_name = self.model.names[int(cls)]
                    label = f'{object_name} {conf:.2f}'
                    
                    text = f'{object_name}: {conf:.2f}'
                    #create retangle
                    cv2.rectangle(frame_copy, (int(box[0]), int(box[1])), (int(box[0] + box[2]), int(box[1] + box[3])), (255, 0, 0), 2)
                    cv2.putText(frame_copy, text, (int(box[0]), int(box[1]) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    cv2.putText(frame_copy, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)  # Add label to the frame
                    
                    # Retrieve GPS data
                    #try:
                        #x=L76X.L76X()
                        #x.L76X_Set_Baudrate(9600)
                        #x.L76X_Send_Command(x.SET_NMEA_BAUDRATE_115200)
                        #time.sleep(2)
                        #x.L76X_Set_Baudrate(115200)

                        #x.L76X_Send_Command(x.SET_POS_FIX_400MS)

                        ## Set output message
                        #x.L76X_Send_Command(x.SET_NMEA_OUTPUT)

                        #x.L76X_Exit_BackupMode()

                        #x.L76X_Gat_GNRMC()
                        #if x.Status == 1:
                        #    print('Get location success')
                        #else:
                        #    print('Get location fail')

                        # Store latitude and longitude values
                        #self.latitude = x.Lat
                        #self.longitude = x.Lon

                    # Capture image and send Line notification
                    image_file_name = f"detected_{time.time()}.jpg"  # New file name
                    image_path = f"{self.capture_path}/{image_file_name}"
                    cv2.putText(frame_copy, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)  # Add label to the captured image
                    
                    # Call capture_image with the required arguments
                    self.capture_image(frame_copy, image_path, (int(box[0]), int(box[1]), int(box[0] + box[2]), int(box[1] + box[3])))

                    if 'Fire' in label:
                        message = 'Fire detected!\nAt Location:\n Latitude: "null"\n Longitude: "null" \n'
                    elif 'Smoke' in label:
                        message = 'Smoke detected!\nAt Location:\n Latitude: "null"\n Longitude: "null" \n'
                    else:
                        message = 'Object detected\nAt Location:\n Latitude: "null"\n Longitude: "null" \n!'

                    message += label

                    # msgWithPic(message, image_path)
                    
                # Send data to Firebase Realtime Database
                    # Read image file as binary data
                    with open(image_path, "rb") as img_file:
                        image_data = img_file.read()
                
                    # Encode image data into base64 string
                    encoded_image = base64.b64encode(image_data).decode("utf-8")

                    date = time.strftime("%d.%m.%Y", time.localtime(time.time()))
                    
            img = QImage(frame_copy.data.tobytes(), 640, 480, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            self.label.setPixmap(pixmap)
        
        QApplication.processEvents()

class MainCameraApp ():           
    def _inint_ (self):
        self.cameraDetection = None

    def cameraDetection():
        app = QApplication(sys.argv)
        window = QMainWindow()
        camera_app = CameraApp()
        window.setCentralWidget(camera_app)
        window.show()

        exit_key = ord('q')
        while True:
            try:
                app.processEvents()
                if cv2.waitKey(1) & 0xFF == exit_key:
                    break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        camera_app.picam2.stop()
        sys.exit(app.exec_())

    def startCamera (self):
        try:
            thread_cameraDetection =threading.Thread(target=self.cameraDetection()) 
            thread_cameraDetection.start()
        except Exception as e :
            print(f"ERR at Thread camera : {e}")

if __name__ =="__main__" :
    main = MainCameraApp()
    main.cameraDetection()