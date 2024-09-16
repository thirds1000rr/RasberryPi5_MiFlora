# import gpiod

# class GPIOCleanup:
#     @staticmethod
#     def cleanup():
       
#         gpio_pins = [16, 17, 27] 

#         try:
#             chip = gpiod.Chip('gpiochip0')
#             for gpio in gpio_pins:
#                 line = chip.get_line(gpio)
#                 line.request(consumer="GPIOCleanup", type=gpiod.LINE_REQ_DIR_OUT)
#                 line.set_value(1)  
#                 line.release()
#                 print(f"GPIO {gpio} cleaned up and set to HIGH.")
#         except Exception as e:
#             print(f"Error during GPIO cleanup: {e}")
#     def clean_specific ():
#         try : 
#             chip = gpiod.Chip('gpiochip0')
#         except Exception as e:
#             print(f"Err at clean up {e}")

# if __name__ == "__main__":
#     GPIOCleanup.cleanup()
