from bleak import BleakScanner, BleakClient
import asyncio

# 這是你想連接的藍牙設備的地址（地址可以從掃描結果中獲得）
device_address = 'CA:59:0E:53:87:42'

async def scan_for_devices():
    # 掃描藍牙設備
    scanner = BleakScanner()
    devices = await scanner.discover()
    for device in devices:
        print(f"Found device: {device.name}, Address: {device.address}")
    return devices

async def print_characteristics(address):
    async with BleakClient(address) as client:
        # 確保設備已經連接
        print(f"Connected to {address}")

        # 獲取所有的 service 和 characteristics
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.uuid}")
            for characteristic in service.characteristics:
                properties = characteristic.properties
                print(f"  Characteristic: {characteristic.uuid}")
                if properties.write:
                    print("    Writable characteristic")
                if properties.read:
                    print("    Readable characteristic")
                if properties.notify:
                    print("    Notifiable characteristic")

async def main():
    # 扫描设备并连接
    await scan_for_devices()
    await print_characteristics(device_address)

# 运行异步主函数
loop = asyncio.get_event_loop()
loop.run_until_complete(main())