import RPi.GPIO as GPIO
import time 

class buzzerController : 
    def __init__ (self):
        self.duration = 15
        self.stop_duration = 20
        self.gpio_buzzer = 4
        self.state = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_buzzer , GPIO.OUT)

    
    def OpenBuzzer(self): 
        if self.state :
            GPIO.output(self.gpio_buzzer,GPIO.HIGH)
            time.sleep(self.duration)
            GPIO.output(self.gpio_buzzer,GPIO.LOW)
            self.state = False
        time.sleep(self.stop_duration)

        
    