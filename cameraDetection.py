from picamera2 import Picamera2
import cv2
import numpy as np


# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()

# Capture and display images
while True:
    frame = picam2.capture_array()
    image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    cv2.imshow('Pi Camera', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.close()
cv2.destroyAllWindows()
