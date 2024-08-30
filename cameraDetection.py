import cv2
import torch
import numpy as np
from picamera2 import Picamera2

# Import the DetectionModel class from your YOLO model implementation
from yolov5.models.yolo import DetectionModel  # Adjust the import path as needed
from yolov5.models.experimental import attempt_load
# Allowlist the DetectionModel class
torch.serialization.add_safe_globals([DetectionModel])

# Step 1: Initialize the YOLO model architecture
model_config_path = 'yolov5/models/yolov5s.yaml'
model = DetectionModel(cfg=model_config_path)

# Step 2: Load the state_dict (weights) from the .pt file

# Replace with the path to your YOLO model
model = attempt_load('best.pt', 'cpu')
model.eval()

# Initialize Pi Camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

# Define target size (change as needed)
target_size = (640, 480)  # Width, Height

def process_frame(frame):
    # Resize the frame to the target size
    resized_frame = cv2.resize(frame, target_size)

    # Convert the resized frame to RGB
    img = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

    # Prepare the image for the model
    img_tensor = torch.from_numpy(img).float() / 255.0
    img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)

    # Perform detection
    with torch.no_grad():
        results = model(img_tensor)

    # Extract results (assuming YOLO output format)
    pred = results[0]  # Check the format according to your model's output

    # Process detections !!!! Problem is here !!!!
    # for det in pred:
    #     if len(det) > 0:
    #         # Extract coordinates and labels
    #         for *xyxy, conf, cls in det:
    #             xyxy = torch.tensor(xyxy).numpy()
    #             conf = conf.item()
    #             cls = int(cls.item())

    #             # Extract the first four elements for bounding box (x_min, y_min, x_max, y_max)
    #             x1, y1, x2, y2 = xyxy[:4]

    #             # Convert bounding box coordinates back to original size
    #             x1 = int(x1 * (frame.shape[1] / target_size[0]))
    #             y1 = int(y1 * (frame.shape[0] / target_size[1]))
    #             x2 = int(x2 * (frame.shape[1] / target_size[0]))
    #             y2 = int(y2 * (frame.shape[0] / target_size[1]))

    #             # Draw bounding box
    #             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #             cv2.putText(frame, f'Class {cls} Conf {conf:.2f}', (x1, y1 - 10),
    #                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

# Real-time detection loop
while True:
    # Capture frame
    frame = picam2.capture_array()

    # Process frame
    result_frame = process_frame(frame)

    # Display result
    cv2.imshow('Detection', result_frame)

    # Break loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
picam2.close()
cv2.destroyAllWindows()