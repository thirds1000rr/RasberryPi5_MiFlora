
<h2>THE EARTHWORM SMART FARM</h1>
<span>This project aims to develop an IoT-based smart farming system for monitoring soil conditions and protecting worm farms. It uses Raspberry Pi 5 to connect with Xiaomi Flora BLE sensors to monitor temperature and moisture, and integrates a camera with YOLO object detection to detect threats like rats or toads. The system sends data to a server every 15 seconds and responds with commands, while also allowing autonomous operation if the server is down. Alerts and controls are sent to users via a mobile application, enabling real-time farm monitoring and automation.
</span>


<h2>Project Contributors</h2>
<ul>
  <li>Bovornpol Jiturai</li>
  
   <span>Role: Backend Development & <a href=https://github.com/thirds1000rr/RasberryPi5_MiFlora>IoT Integration</a></span>
  <li>Ammar Chuapoodee</li>
    <span>Role: Flutter Mobile Application Development</span>
</ul>
<br>
<h2>Server Side (Explanation):</h2>
<span>
The server acts as the central controller that communicates with the Raspberry Pi every 15 seconds. It sends scanning commands and receives environmental data (e.g., temperature, humidity) and threat alerts (e.g., detected animals). The server processes this data, stores it in a database, and forwards notifications to users via a mobile app. Additionally, the server allows remote control of farm equipment (e.g., water pumps) through commands sent to the board. While the board can operate independently when needed, the server enables synchronization, logging, and centralized management of the entire system.
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


