import gpiod
import time
import threading

active_gpio_auto = []
active_gpio_manual = []

class GPIOController:
    def __init__(self):
        self.gpio_fan = 10
        self.duration = 15
        self.work_temp = 35
        self.min_humid = 40
        self.max_humid = 55
        self.POWER_ON = 0  # Active low
        self.POWER_OFF = 1  # Active low
        self.chip = gpiod.Chip('gpiochip0')  # Use the appropriate gpiochip
        self.pi = self.chip.get_line(self.gpio_fan)
        self.pi.request(consumer="GPIOController", type=gpiod.LINE_REQ_DIR_OUT)

    def decision(self, payload):
        gpio = int(payload["gpio_id"])
        mode = payload["mode"]
        power = payload["power"]
        temperature = payload.get("temperature", None)
        humid = payload.get("humid", None)

        try:
            if gpio not in active_gpio_auto:
                line = self.chip.get_line(gpio)
                line.request(consumer="GPIOController", type=gpiod.LINE_REQ_DIR_OUT)
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
                elif not mode:  # Manual mode
                    try:
                        print(f"Receive manual {mode} , {power}")
                        if power and gpio not in active_gpio_manual:
                            active_gpio_manual.append(gpio)
                            print(f"Arr after append {active_gpio_manual}")
                            line.set_value(self.POWER_ON)
                            return True
                        elif not power and gpio in active_gpio_manual:
                            line.set_value(self.POWER_OFF)
                            active_gpio_manual.remove(gpio)
                            print(f"Arr after delete {active_gpio_manual}")
                            return True
                    except Exception as e:
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
            line = self.chip.get_line(gpio)
            line.request(consumer="GPIOController", type=gpiod.LINE_REQ_DIR_OUT)
            if duration and not power:
                line.set_value(self.POWER_ON)
                time.sleep(duration)
                line.set_value(self.POWER_OFF)
                active_gpio_auto.remove(gpio)
        except Exception as e:
            if gpio in active_gpio_auto:
                active_gpio_auto.remove(gpio)
            elif gpio in active_gpio_manual:
                active_gpio_manual.remove(gpio)
            print(f"Error at controllGpioAuto: {e}")

    def cleanup(self):
        self.chip.close()  # Close the chip to release resources


