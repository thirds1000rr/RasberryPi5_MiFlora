
<h2>THE EARTHWORM SMART FARM</h1>
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
<h2>Dependencies</h2>
  <ul>
    <li> @line/bot-sdk</li>
    <li> bcryptjs</li>
    <li>cors</li>
    <li>dayjs</li>
    <li>dotenv</li>
    <li>express</li>
    <li>jsonwebtoken</li>
    <li>mqtt</li>
    <li>nodemon</li>
    <li>sequelize</li>
  </ul>


