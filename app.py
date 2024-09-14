from mqtt import MainApp
import threading
# from yolov5.cameraDetection import start

if __name__ =="__main__" : 
    # camera_thread = threading.Thread(target=start)
    # camera_thread.start()
    main_app = MainApp()
    main_app.start()