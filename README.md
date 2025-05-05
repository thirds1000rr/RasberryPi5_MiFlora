
<h1>THE EARTHWORM SMART FARM</h1>
<span>This project aims to develop an IoT-based smart farming system for monitoring soil conditions and protecting worm farms. It uses Raspberry Pi 5 to connect with Xiaomi Flora BLE sensors to monitor temperature and moisture, and integrates a camera with YOLO object detection to detect threats like rats or toads. The system sends data to a server every 15 seconds and responds with commands, while also allowing autonomous operation if the server is down. Alerts and controls are sent to users via a mobile application, enabling real-time farm monitoring and automation.
</span>


<h2>Project Contributors</h2>
<ul>
  <li>Bovornpol Jiturai</li>
  
   <span>Role: <a href=https://github.com/thirds1000rr/SmatFarm_nodejs_sql>Backend Development</a> & IoT Integration</span>
  <li>Ammar Chuapoodee</li>
    <span>Role: Flutter Mobile Application Development</span>
</ul>
<br>
<h2>IoT Side (Explanation):</h2>
<span>
The IoT system uses a Raspberry Pi 5 to collect environmental data and monitor threats in a worm farm. It connects to Xiaomi Flora sensors via Bluetooth Low Energy (BLE) to read soil temperature and moisture, and uses a connected camera running YOLO object detection to identify unwanted animals such as rats or toads. The Raspberry Pi sends sensor data and detection results to the server every 15 seconds and receives control commands in response. To reduce server dependency, the board can locally store MAC addresses and operate independently when the server is unreachable. GPIO is used to control devices like water pumps and buzzers.
</span>
<br>
<h2>Devices</h2>
<ul>
<li>Raspberry Pi 5 </li>
<li>OV5647 IR-CUT Camera</li>
<li>Xiaomi Flora</li>
<li>ESP32</li>
<li>Passive Buzzer</li>
</ul>
<br>
<h2>Dependencies</h2>
  <ul>
    <li>threading</li>
    <li>asynceio</li>
    <li>miflora</li>
    <li>pahomqtt</li>
    <li>BleakScanner</li>
    <li>datetime</li>
    <li>gpiozero</li>
    <li>json</li>
  </ul>
  <br>
<h2>Dependencies for object detection</h2>
<ul>
<li><a href=https://github.com/ultralytics/yolov5>YoloV5 (Pytorch)</a></li>
<li>base64</li>
<li>Picamera2</li>
</ul>
<br>
<h2>Python Threads:</h2>
<span>
In this project, threads are used to run MQTT communication and sensor reading in parallel. One thread is responsible for continuously listening to MQTT messages from the server, while another handles periodic Bluetooth readings from the Xiaomi Flora sensor. This approach ensures that the device can react to incoming commands in real time without being delayed by sensor scanning. Threading improves the system’s responsiveness and prevents blocking operations, which is essential in IoT environments with time-sensitive interactions.
</span>



