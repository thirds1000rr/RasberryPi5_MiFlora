import json
from bleak import BleakScanner

async def scan_devices():
    print("Starting BLE scan...")
    scanner = BleakScanner()
    devices = await scanner.discover()  # Await to get res
    print("Scan complete.")

    devices_info = []
    for dev in devices:
        device_name = dev.name if dev.name else 'Unknown'
        device_info = {
            'address': dev.address,
            'name': device_name,
        }
        
        if device_name.lower() == 'flower care' and dev.address not in device_info :
            devices_info.append(device_info)
    
    return devices_info

async def main():
    devices_info = await scan_devices()
    #Process devices info
    print(json.dumps(devices_info, indent=2))
    return devices_info
