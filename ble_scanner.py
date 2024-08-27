import json
import time
from bluepy.btle import Scanner, DefaultDelegate, BTLEDisconnectError

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print(f"Discovered device {dev.addr}")
        elif isNewData:
            print(f"Received new data from {dev.addr}")

def get_device_name(dev):
    for (adtype, desc, value) in dev.getScanData():
        print(desc, value)
        if desc == "Complete Local Name" or desc == "Shortened Local Name":
            return value
    return None

def main():
    max_retries = 3
    retries = 0
    devices = None

    while retries < max_retries:
        try:
            scanner = Scanner().withDelegate(ScanDelegate())
            devices = scanner.scan(5)
            break
        except BTLEDisconnectError as e:
            print(f"BLE device disconnect during scanning: {e}")
            retries += 1
            time.sleep(1)
        except Exception as e:
            print(f"Unexpected error during scanning: {e}")
            retries += 1
            time.sleep(1)
        finally:
            if 'scanner' in locals():
                del scanner
                print('Free resource after scan BLE list')

    if devices is None:
        print("Cannot find any flora devices after maximum retries.")
        return None

    devices_info = []
    sensors = []

    try:
        for dev in devices:
            device_name = get_device_name(dev)
            device_info = {
                'address': dev.addr,
                'name': device_name,
            }
            print(f"deviceInfo{device_info}")
            devices_info.append(device_info)
            if device_name == 'Flower care' or device_name == 'flower care':
                sensors.append(device_info)
    except Exception as e:
        print(f"Error during scan processing: {e}")
        return None
    finally:
        print("test before returns")
        return json.dumps(sensors, indent=2) if sensors else None
