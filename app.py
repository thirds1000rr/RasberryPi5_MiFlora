from mqtt import MainApp
from cameraDetection import MainCameraApp

if __name__ =="__main__" : 
    # camera = MainCameraApp()
    # camera.startCamera()
    main = MainApp()
    main.start()