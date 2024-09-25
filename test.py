import asyncio
from bleak import BleakClient, BleakScanner

# 定義常見的 Bluetooth 服務 UUID 名稱對應
UUID_DEFINITIONS = {
    # Sample Services
    "0000180d-0000-1000-8000-00805f9b34fb": "Heart Rate Service",
    "0000180a-0000-1000-8000-00805f9b34fb": "Device Information Service",
    
    # Sample Characteristics
    "00002a37-0000-1000-8000-00805f9b34fb": "Heart Rate Measurement",
    "00002a29-0000-1000-8000-00805f9b34fb": "Manufacturer Name String",
    
    # GATT Services
    "00001800-0000-1000-8000-00805f9b34fb": "Generic Access",
    "00001801-0000-1000-8000-00805f9b34fb": "Generic Attribute",
    
    # GATT Declarations
    "00002800-0000-1000-8000-00805f9b34fb": "Primary Service",
    "00002801-0000-1000-8000-00805f9b34fb": "Secondary Service",
    "00002802-0000-1000-8000-00805f9b34fb": "Include",
    "00002803-0000-1000-8000-00805f9b34fb": "Characteristic",
    
    # GATT Descriptors
    "00002900-0000-1000-8000-00805f9b34fb": "Characteristic Extended Properties",
    "00002901-0000-1000-8000-00805f9b34fb": "Characteristic User Description",
    "00002902-0000-1000-8000-00805f9b34fb": "Client Characteristic Configuration",
    "00002903-0000-1000-8000-00805f9b34fb": "Server Characteristic Configuration",
    "00002904-0000-1000-8000-00805f9b34fb": "Characteristic Presentation Format",
    "00002905-0000-1000-8000-00805f9b34fb": "Characteristic Aggregate Format",
    "00002906-0000-1000-8000-00805f9b34fb": "Valid Range",
    "00002907-0000-1000-8000-00805f9b34fb": "External Report Reference Descriptor",
    "00002908-0000-1000-8000-00805f9b34fb": "Report Reference Descriptor",
    
    # GATT Characteristics
    "00002a00-0000-1000-8000-00805f9b34fb": "Device Name",
    "00002a01-0000-1000-8000-00805f9b34fb": "Appearance",
    "00002a02-0000-1000-8000-00805f9b34fb": "Peripheral Privacy Flag",
    "00002a03-0000-1000-8000-00805f9b34fb": "Reconnection Address",
    "00002a04-0000-1000-8000-00805f9b34fb": "PPCP",
    "00002a05-0000-1000-8000-00805f9b34fb": "Service Changed",
    
    # GATT Service UUIDs
    "00001802-0000-1000-8000-00805f9b34fb": "Immediate Alert",
    "00001803-0000-1000-8000-00805f9b34fb": "Link Loss",
    "00001804-0000-1000-8000-00805f9b34fb": "Tx Power",
    "00001805-0000-1000-8000-00805f9b34fb": "Current Time Service",
    "00001806-0000-1000-8000-00805f9b34fb": "Reference Time Update Service",
    "00001807-0000-1000-8000-00805f9b34fb": "Next DST Change Service",
    "00001808-0000-1000-8000-00805f9b34fb": "Glucose",
    "00001809-0000-1000-8000-00805f9b34fb": "Health Thermometer",
    "0000180a-0000-1000-8000-00805f9b34fb": "Device Information",
    "0000180b-0000-1000-8000-00805f9b34fb": "Network Availability",
    "0000180d-0000-1000-8000-00805f9b34fb": "Heart Rate",
    "0000180e-0000-1000-8000-00805f9b34fb": "Phone Alert Status Service",
    "0000180f-0000-1000-8000-00805f9b34fb": "Battery Service",
    "00001810-0000-1000-8000-00805f9b34fb": "Blood Pressure",
    "00001811-0000-1000-8000-00805f9b34fb": "Alert Notification Service",
    "00001812-0000-1000-8000-00805f9b34fb": "Human Interface Device",
    "00001813-0000-1000-8000-00805f9b34fb": "Scan Parameters",
    "00001814-0000-1000-8000-00805f9b34fb": "Running Speed and Cadence",
    "00001816-0000-1000-8000-00805f9b34fb": "Cycling Speed and Cadence",
    "00001818-0000-1000-8000-00805f9b34fb": "Cycling Power",
    "00001819-0000-1000-8000-00805f9b34fb": "Location and Navigation",
    
    # GATT Characteristic UUIDs
    "00002a06-0000-1000-8000-00805f9b34fb": "Alert Level",
    "00002a07-0000-1000-8000-00805f9b34fb": "Tx Power Level",
    "00002a08-0000-1000-8000-00805f9b34fb": "Date Time",
    "00002a09-0000-1000-8000-00805f9b34fb": "Day of Week",
    "00002a0a-0000-1000-8000-00805f9b34fb": "Day Date Time",
    "00002a0c-0000-1000-8000-00805f9b34fb": "Exact Time 256",
    "00002a0d-0000-1000-8000-00805f9b34fb": "DST Offset",
    "00002a0e-0000-1000-8000-00805f9b34fb": "Time Zone",
    "00002a0f-0000-1000-8000-00805f9b34fb": "Local Time Information",
    "00002a11-0000-1000-8000-00805f9b34fb": "Time with DST",
    "00002a12-0000-1000-8000-00805f9b34fb": "Time Accuracy",
    "00002a13-0000-1000-8000-00805f9b34fb": "Time Source",
    "00002a14-0000-1000-8000-00805f9b34fb": "Reference Time Information",
    "00002a16-0000-1000-8000-00805f9b34fb": "Time Update Control Point",
    "00002a17-0000-1000-8000-00805f9b34fb": "Time Update State",
    "00002a18-0000-1000-8000-00805f9b34fb": "Glucose Measurement",
    "00002a19-0000-1000-8000-00805f9b34fb": "Battery Level",
    "00002a1c-0000-1000-8000-00805f9b34fb": "Temperature Measurement",
    "00002a1d-0000-1000-8000-00805f9b34fb": "Temperature Type",
    "00002a1e-0000-1000-8000-00805f9b34fb": "Intermediate Temperature",
    "00002a21-0000-1000-8000-00805f9b34fb": "Measurement Interval",
    "00002a22-0000-1000-8000-00805f9b34fb": "Boot Keyboard Input Report",
    "00002a23-0000-1000-8000-00805f9b34fb": "System ID",
    "00002a24-0000-1000-8000-00805f9b34fb": "Model Number String",
    "00002a25-0000-1000-8000-00805f9b34fb": "Serial Number String",
    "00002a26-0000-1000-8000-00805f9b34fb": "Firmware Revision String",
    "00002a27-0000-1000-8000-00805f9b34fb": "Hardware Revision String",
    "00002a28-0000-1000-8000-00805f9b34fb": "Software Revision String",
    "00002a29-0000-1000-8000-00805f9b34fb": "Manufacturer Name String",
    "00002a2a-0000-1000-8000-00805f9b34fb": "IEEE 11073-20601 Regulatory Certification Data List",
    "00002a2b-0000-1000-8000-00805f9b34fb": "Current Time",
    "00002a31-0000-1000-8000-00805f9b34fb": "Scan Interval Window",
    "00002a32-0000-1000-8000-00805f9b34fb": "PnP ID",
    "00002a33-0000-1000-8000-00805f9b34fb": "Glucose Feature",
    "00002a34-0000-1000-8000-00805f9b34fb": "Record Access Control Point",
    "00002a35-0000-1000-8000-00805f9b34fb": "Blood Pressure Measurement",
    "00002a36-0000-1000-8000-00805f9b34fb": "Intermediate Cuff Pressure",
    "00002a37-0000-1000-8000-00805f9b34fb": "Heart Rate Measurement",
    "00002a38-0000-1000-8000-00805f9b34fb": "Body Sensor Location",
    "00002a39-0000-1000-8000-00805f9b34fb": "Heart Rate Control Point",
    "00002a3f-0000-1000-8000-00805f9b34fb": "Alert Status",
    "00002a40-0000-1000-8000-00805f9b34fb": "Ringer Control Point",
    "00002a41-0000-1000-8000-00805f9b34fb": "Ringer Setting",
    "00002a42-0000-1000-8000-00805f9b34fb": "Alert Category ID Bit Mask",
    "00002a43-0000-1000-8000-00805f9b34fb": "Alert Category ID",
    "00002a44-0000-1000-8000-00805f9b34fb": "Alert Notification Control Point",
    "00002a45-0000-1000-8000-00805f9b34fb": "Unread Alert Status",
    "00002a46-0000-1000-8000-00805f9b34fb": "New Alert",
    "00002a47-0000-1000-8000-00805f9b34fb": "Supported New Alert Category",
    "00002a48-0000-1000-8000-00805f9b34fb": "Supported Unread Alert Category",
    "00002a49-0000-1000-8000-00805f9b34fb": "Blood Pressure Feature",
    "00002a4a-0000-1000-8000-00805f9b34fb": "HID Information",
    "00002a4b-0000-1000-8000-00805f9b34fb": "Report Map",
    "00002a4c-0000-1000-8000-00805f9b34fb": "HID Control Point",
    "00002a4d-0000-1000-8000-00805f9b34fb": "Report",
    "00002a4e-0000-1000-8000-00805f9b34fb": "Protocol Mode",
    "00002a4f-0000-1000-8000-00805f9b34fb": "Scan Interval Window",
    "00002a50-0000-1000-8000-00805f9b34fb": "PnP ID"
}


def get_service_name(uuid):
    return UUID_DEFINITIONS.get(uuid, "Unknown Service")


async def scan_for_devices():
    print("Scanning for devices...")
    scanner = BleakScanner()
    devices = await scanner.discover()
    return devices


def print_device_list(devices):
    print("\nAvailable devices:")
    for idx, device in enumerate(devices):
        print(f"{idx + 1}: {device.name} ({device.address})")


async def run():
    devices = await scan_for_devices()

    if not devices:
        print("No devices found.")
        return

    print_device_list(devices)

    # 提示用戶選擇設備
    try:
        choice = int(input("\nEnter the number of the device to connect to: ")) - 1
        if choice < 0 or choice >= len(devices):
            raise ValueError("Invalid choice")
        device_address = devices[choice].address
    except (ValueError, IndexError):
        print("Invalid selection. Exiting.")
        return

    async with BleakClient(device_address) as client:
        print(f"Connected: {client.is_connected}")

        services = client.services

        for service in services:
            service_name = get_service_name(service.uuid)
            print(f"Service: {service.uuid} ({service_name})")
            for characteristic in service.characteristics:
                print(f"  Characteristic: {characteristic.uuid}")
                if characteristic.properties:
                    # 檢查是否支持寫入
                    if "write" in characteristic.properties:
                        print("    Writable characteristic")
                    # 檢查是否支持讀取
                    if "read" in characteristic.properties:
                        print("    Readable characteristic")
                    # 檢查是否支持通知
                    if "notify" in characteristic.properties:
                        print("    Notifiable characteristic")        



loop = asyncio.get_event_loop()
loop.run_until_complete(run())
