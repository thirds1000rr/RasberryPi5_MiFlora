from datetime import datetime
import time
from miflora.miflora_poller import MiFloraPoller
from btlewrap.bluepy import BluepyBackend

# formatted_time = now_gmt7.strftime("%Y-%m-%dT%H:%M:%S%z")

def read_mi_flora_data(mac_address , delay = 5):
        try:
            poller = MiFloraPoller(mac_address, BluepyBackend)

            temperature = poller.parameter_value("temperature")
            moisture = poller.parameter_value("moisture")
            light = poller.parameter_value("light")
            conductivity = poller.parameter_value("conductivity")
            battery = poller.parameter_value("battery")
            data = {
                "macAddress": mac_address,
                "temperature":  temperature if temperature else None,
                "moisture": moisture if moisture else None,
                "light": light if light else None,
                "conductivity": conductivity if conductivity else None,
                "battery": battery if battery else None,
                "timestamp": datetime.now().isoformat()
            }

            return data
        except BrokenPipeError as e:
            print(f"Broken pipe error: {e} , retrying")
        except Exception as e:
            print(f"Error reading Mi Flora data: {e}")
            data = {
                    "macAddress": mac_address,
                    "temperature":None,
                    "moisture": None,
                    "light": None,
                    "conductivity":None,
                    "battery":  None,
                    "timestamp": None
                }
            return data 
        finally:
            if 'poller' in locals():
                del poller
                print("Disconnect Flora")
            time.sleep(delay)
