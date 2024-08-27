import RPi.GPIO as GPIO
import time
import threading

active_gpio_auto = []
active_gpio_manual=[]
class GPIOController:
    def __init__(self):
        self.gpio_fan = 10
        self.duration = 15
        self.work_temp = 35
        self.min_humid = 40
        self.max_humid = 55
        self.POWER_ON = GPIO.HIGH
        self.POWER_OFF = GPIO.LOW
        GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(self.gpio_fan, GPIO.OUT)

    def decision(self, payload):
        gpio = int(payload["gpio_id"])
        mode = payload["mode"]
        power = payload["power"]
        temperature = payload.get("temperature", None)
        humid = payload.get("humid", None)

        try:
            
            if gpio not in active_gpio_auto:
                GPIO.setup(gpio, GPIO.OUT)
                # GPIO.output(gpio, GPIO.LOW)
                if mode and temperature is not None and humid is not None:  # Auto mode
                    try:
                        active_gpio_auto.append(gpio)
                        if temperature >= self.work_temp and self.min_humid <= humid <= self.max_humid:
                            waterPump_thread = threading.Thread(target=self.controllGpioAuto, args=(gpio, 5, power))
                            waterPump_thread.start()
                            print("Auto 1 ")
                            return True
                        elif temperature < self.work_temp and humid < self.min_humid:
                            waterPump_thread = threading.Thread(target=self.controllGpioAuto, args=(gpio, 5, power))
                            waterPump_thread.start()
                            print("Auto 2 ")
                            return True
                    except Exception as e:
                        print(f"Error at Decision Auto mode: {e}")
                        if gpio in active_gpio_auto:
                            active_gpio_auto.remove(gpio)
                        return False
                elif not mode :  # Manual mode
                    try: 
                        print(f"receive manual {mode} , {power}")
                        if power and gpio not in active_gpio_manual:
                            active_gpio_manual.append(gpio)
                            print(f"Arr after append {active_gpio_manual}")
                            GPIO.output(gpio ,self.POWER_ON)
                            return True
                        elif not power and gpio in active_gpio_manual :
                            GPIO.output(gpio , self.POWER_OFF)
                            active_gpio_manual.remove(gpio)
                            print(f"Arr after delete {active_gpio_manual}")
                            return True
                    except Exception as e :
                        print(e)
                else:
                    print(f"Received Temp: {temperature}, Humid: {humid}")
                    return False
            else:
                print(f"Gpio: {gpio} is already in use.")
                return False
        except Exception as e:
            print(f"Error at decision GPIO controller: {e}")

    def controllGpioAuto(self, gpio, duration=None, power=None):
        try:
            if duration and not power:
                GPIO.output(gpio, self.POWER_ON)
                time.sleep(duration)
                GPIO.output(gpio, self.POWER_OFF)
                active_gpio_auto.remove(gpio)
        except Exception as e:
            if gpio in active_gpio_auto:
                active_gpio_auto.remove(gpio)
            elif gpio in active_gpio_manual:
                active_gpio_manual.remove(gpio)
            print(f"Error at controllGpioAuto: {e}")

    # def controllGpioManual(self, gpio, power):
    #     try:
    #         if power and gpio not in active_gpio_manual:
    #             GPIO.output(gpio, self.POWER_ON)
    #             active_gpio_manual.append(gpio)
    #             print(f"Manual Mode On : {power}\n , {active_gpio_manual}")
    #             return True
    #         elif not power and gpio in active_gpio_manual:
    #             active_gpio_manual.remove(gpio)
    #             # GPIO.output(gpio, self.POWER_OFF)
    #             GPIO.cleanup(gpio)
    #             print(f"Manual Mode OFF : {power}\n , {active_gpio_manual}")
    #             return True
    #         else:
    #             return False
    #     except Exception as e:
    #         if gpio in active_gpio_manual:
    #             active_gpio_manual.remove(gpio)
    #         print(f"Error at controllGpioManual: {e}")
    #         return False

