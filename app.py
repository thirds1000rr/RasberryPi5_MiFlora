from mqtt import MainApp
# import threading
# from cleanup_gpio import GPIOCleanup

if __name__ =="__main__" : 
    # camera_thread = threading.Thread(target=start)
    # camera_thread.start() 
    # Clean up all GPIO lines
    # GPIOCleanup.cleanup()
    main_app = MainApp()
    main_app.start()