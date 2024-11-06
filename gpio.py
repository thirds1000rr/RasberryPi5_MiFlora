import time
import threading
import gpiozero
import json
from datetime import datetime
# from mqtt import MQTTClient as mqtt
# from utilities.notify import LineController

active_gpio_auto = []
active_gpio_manual = []

class GPIOController:
    def __init__(self , mqtt_client):
        self.gpio_fan = 10
        self.duration = 15
        self.work_temp = 35
        self.min_humid = 50
        self.max_humid = 55
        self.extreme_humid = 70
        self.extreme_temp = 40
        self.lines = {}  # To store GPIO OutputDevice obj
        self.fan_setup = gpiozero.OutputDevice(self.gpio_fan, active_high=False, initial_value=True)
        self.fan_setup.on()
        self.mqtt_client = mqtt_client
        
    def setupJson(self ,gpio_id ,senesor_id, openedAt , closedAt ):
        try:
            data = {
                "sensor_id" : senesor_id,
                "gpio_id" : gpio_id,
                "openedAt" : openedAt,
                "closedAt" : closedAt
            }
            print(f"Json water Pump Log {data}")
            data = json.dumps(data)
            return self.publish_(data)
        except Exception as e :
            print(f"Json decode err in Decision fn {e}")

    def publish_(self , msg):
        try :
            self.mqtt_client.publish("waterPumpLog",msg)
        except Exception as e : 
            print(f"publish Notify Error : {e}")
        
    def setUpGpio(self, gpio):
        try:
            if gpio not in self.lines:
                self.lines[gpio] = gpiozero.OutputDevice(gpio, active_high=False, initial_value=True)
                print(f"GPIO {gpio} set up successfully.")
            return self.lines[gpio]
        except Exception as e:
            print(f"Error during setup GPIO {gpio}: {e}")
            return False
        
        
    def decision(self, sensor_id = None ,payload=None, gpio_receive=None , mode_receive=None , power_receive=None ,name=None):
        try:
            print(mode_receive , power_receive , name)
            # Check if payload is a dictionary
            # print(f"Type of payload: {type(payload)}")
            # print(f"Decision \n{payload}\n GPIO : {gpio_receive}")
            if payload :
                sensor_id = int(sensor_id)
                gpio = int(gpio_receive)
                mode = mode_receive
                power = power_receive
                temperature = payload.get("temperature", None)
                humid = payload.get("moisture", None)
                
            else : 
                mode = mode_receive
                power = power_receive
                gpio = int(gpio_receive)


        
            if gpio not in active_gpio_auto:
                if mode and temperature is not None and humid is not None:  # Auto mode
                    try:
                        if temperature >= self.work_temp and self.min_humid <= humid <= self.max_humid:
                            active_gpio_auto.append(gpio)
                            relay= self.setUpGpio(gpio)
                            waterPump_thread = threading.Thread(target=self.controllGpioAuto, args=(sensor_id , gpio, 5, power, 60 , name))
                            waterPump_thread.start() 
                            if waterPump_thread.is_alive():
                                print("Auto 1")
                                return True
                            else : 
                                print(f"Failed to set up GPIO {gpio}.")
                                return False
                        elif temperature < self.work_temp and humid < self.min_humid:
                            active_gpio_auto.append(gpio)
                            relay = self.setUpGpio(gpio)
                            waterPump_thread = threading.Thread(target=self.controllGpioAuto, args=(sensor_id,gpio, 10, power, 120 , name))
                            waterPump_thread.start()
                            if waterPump_thread.is_alive():
                                print("Auto 2")
                                return True
                            else:
                                print(f"Failed to set up GPIO {gpio}.")
                                return False
                    except Exception as err:
                        if gpio in active_gpio_auto:
                            active_gpio_auto.remove(gpio)
                        print(f"Err in Auto mode {err}")
                        return False
                    finally:
                        self.Autofan()
                elif not mode :  # Manual mode
                    try:
                        print(f"Received manual mode: {mode}, power: {power}")
                        if power and gpio not in active_gpio_manual:
                            relay = self.setUpGpio(gpio)
                            active_gpio_manual.append(gpio)
                            relay.on()
                            print(f"Active GPIOs after append Manual: {active_gpio_manual}")
                            return True
                        elif not power and gpio in active_gpio_manual:
                            relay = self.lines[gpio]
                            relay.off()
                            active_gpio_manual.remove(gpio)
                            print(f"Active GPIOs after remove Manual: {active_gpio_manual}")
                            return True
                        return False
                    except Exception as e:
                        print(f"Err at manual mode Gpio {gpio} : {e}\n")
                        return False
                    finally:
                        self.Autofan()
                else:
                    print(f"Received Temp: {temperature}, Humid: {humid}")
                    return False
            elif power is None and mode is None : 
                return False
            else:
                print(f"GPIO {gpio} is already in use.")
                return False
        except Exception as e:
            print(f"Error in decision GPIO controller: {e}")

    def controllGpioAuto(self, sensor_id , gpio , duration=None , power=None , sleepduration=None,name=None):
        try:
            relay = self.setUpGpio(gpio)
            if duration and not power:
                openedAt = datetime.now().isoformat()
                relay.on()
                time.sleep(duration)
                relay.off()
                closedAt = datetime.now().isoformat()
                self.setupJson(gpio,sensor_id , openedAt ,closedAt )
                time.sleep(sleepduration)
                active_gpio_auto.remove(gpio)
        except Exception as e:
            if gpio in active_gpio_auto:
                active_gpio_auto.remove(gpio)
            elif gpio in active_gpio_manual:
                active_gpio_manual.remove(gpio)
            print(f"Error in controllGpioAuto: {e}")
        finally:
            self.Autofan()
            # self.line_instance.lineNotify(f"Sensor Name : {name} \nGpio:{gpio}\nWaterPump(Auto) : Off")

            
    def Autofan(self):
        try:
            if len(active_gpio_manual) == 0 and len(active_gpio_auto) == 0:
                self.fan_setup.on()
                print(f"Autofan working. Auto list length: {len(active_gpio_auto)}, Manual list length: {len(active_gpio_manual)}")
            else:
                self.fan_setup.off()
                print(f"Found GPIOs in list. Autofan turned off. Auto list length: {len(active_gpio_auto)}, Manual list length: {len(active_gpio_manual)}")
        except Exception as e:
            print(f"Error in Autofan: {e}")
