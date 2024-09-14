import time
import threading
import gpiozero

active_gpio_auto = []
active_gpio_manual = []

class GPIOController:
    def __init__(self):
        self.gpio_fan = 10
        self.duration = 15
        self.work_temp = 35
        self.min_humid = 40
        self.max_humid = 55
        self.lines = {}  # To store GPIO OutputDevice objects
        self.fan_setup = gpiozero.OutputDevice(self.gpio_fan, active_high=False, initial_value=True)
        self.fan_setup.on()

    def setUpGpio(self, gpio):
        try:
            if gpio not in self.lines:
                self.lines[gpio] = gpiozero.OutputDevice(gpio, active_high=False, initial_value=True)
                print(f"GPIO {gpio} set up successfully.")
            return self.lines[gpio]
        except Exception as e:
            print(f"Error during setup GPIO {gpio}: {e}")

    def decision(self, payload):
        gpio = int(payload["gpio_id"])
        mode = payload["mode"]
        power = payload["power"]
        temperature = payload.get("temperature", None)
        humid = payload.get("humid", None)

        try:
            if gpio not in active_gpio_auto:
                if mode and temperature is not None and humid is not None:  # Auto mode
                    try:
                        active_gpio_auto.append(gpio)
                        relay = self.setUpGpio(gpio)
                        if temperature >= self.work_temp and self.min_humid <= humid <= self.max_humid:
                            waterPump_thread = threading.Thread(target=self.controllGpioAuto, args=(gpio, 5, power, 60))
                            waterPump_thread.start()
                            print("Auto 1")
                            return True
                        elif temperature < self.work_temp and humid < self.min_humid:
                            waterPump_thread = threading.Thread(target=self.controllGpioAuto, args=(gpio, 10, power, 120))
                            waterPump_thread.start()
                            print("Auto 2")
                            return True
                    except Exception as e:
                        print(f"Error in Decision Auto mode: {e}")
                        if gpio in active_gpio_auto:
                            active_gpio_auto.remove(gpio)
                        return False
                elif not mode :  # Manual mode
                    try:
                        print(f"Received manual mode: {mode}, power: {power}")
                        if power and gpio not in active_gpio_manual:
                            relay = self.setUpGpio(gpio)
                            active_gpio_manual.append(gpio)
                            relay.on()
                            print(f"Active GPIOs after append: {active_gpio_manual}")
                            return True
                        elif not power and gpio in active_gpio_manual:
                            relay = self.setUpGpio(gpio)
                            relay.off()
                            active_gpio_manual.remove(gpio)
                            print(f"Active GPIOs after removal: {active_gpio_manual}")
                            return True
                    except Exception as e:
                        print(e)
                    finally:
                        self.Autofan()
                else:
                    print(f"Received Temp: {temperature}, Humid: {humid}")
                    return False
            else:
                print(f"GPIO {gpio} is already in use.")
                return False
        except Exception as e:
            print(f"Error in decision GPIO controller: {e}")

    def controllGpioAuto(self, gpio, duration=None, power=None, sleepduration=None):
        try:
            relay = self.setUpGpio(gpio)
            if duration and not power:
                relay.on()
                time.sleep(duration)
                relay.off()
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
