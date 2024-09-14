import gpiod
import time

LED_PIN = 17  # GPIO17 (Pin 11 on RPi)
chip = gpiod.Chip('gpiochip0')  # Using gpiochip4

led_line = chip.get_line(LED_PIN)
led_line.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)


try:
    while True:
        print("test begin")
        led_line.set_value(1)  # Turn LED on
        time.sleep(1)
        led_line.set_value(0)  # Turn LED off
        time.sleep(1)
finally:
    led_line.release()
