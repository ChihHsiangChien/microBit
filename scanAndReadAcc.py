from bleak import BleakScanner, BleakClient
import asyncio
import sys
import struct
import math


async def scan_for_devices():
    print("Scanning for devices...")
    scanner = BleakScanner()
    devices = await scanner.discover()
    return devices

def print_device_list(devices):
    print("\nAvailable devices:")
    for idx, device in enumerate(devices):
        print(f"{idx + 1}: {device.name} ({device.address})")


# 將不帶連字符的大寫 UUID 轉換為標準格式
def format_uuid(uuid_str):
    uuid_str = uuid_str.lower()  # 轉為小寫
    return f"{uuid_str[:8]}-{uuid_str[8:12]}-{uuid_str[12:16]}-{uuid_str[16:20]}-{uuid_str[20:]}"  # 插入連字符


async def connect_to_device(device_address):
    async with BleakClient(device_address) as client:
        if client.is_connected:
            print(f"Connected to {device_address}")

            try:
                # 使用 client.services 屬性來取得服務
                services = client.services if client.services is not None else await client.get_services()

                # 將大寫無連字符的 UUID 轉換為標準格式後讀取加速度計數據
                
                await read_accelerometer_data(client) 
                period = 1
                await write_accelerometer_period_data(client, period)
                await read_accelerometer_period_data(client)                 
            except Exception as e:
                print(f"Failed to retrieve services: {e}")

            while True:
                if client.is_connected:
                    try:
                        await read_accelerometer_data(client)
                        
                        pass
                    except Exception as e:
                        print(f"Connection error: {e}")
                    # await asyncio.sleep(1)
                else:
                    print("Device disconnected.")
                    break

async def read_accelerometer_data(client):
    characteristic_uuid = "E95DCA4B-251D-470A-A062-FA1922DFA9A8"

    try:
        # 讀取加速度計數據
        value = await client.read_gatt_char(characteristic_uuid)
        # 解析加速度計數據，為小端格式的 3 個有符號 16 位整數
        x, y, z = struct.unpack("<hhh", value)
        # 將數據除以 1000 得到實際的加速度值
        x = x / 1000.0
        y = y / 1000.0
        z = z / 1000.0
        
        magnitude = math.sqrt(x**2 + y**2 + z**2)

        print(magnitude)
    except Exception as e:
        print(f"    Failed to read {characteristic_uuid}: {e}")


async def read_accelerometer_period_data(client):
    '''
    讀取加速度週期的資料
    '''
    characteristic_uuid = format_uuid("E95DFB24251D470AA062FA1922DFA9A8")

    try:
        # 讀取加速度計period數據
        value = await client.read_gatt_char(characteristic_uuid)
        period = struct.unpack("<h", value)[0]
        print(f"period:{period}")
    except Exception as e:
        print(f"    Failed to read {characteristic_uuid}: {e}")


async def write_accelerometer_period_data(client, period):
    '''
    寫入加速度週期的資料
    '''    
    characteristic_uuid = format_uuid("E95DFB24251D470AA062FA1922DFA9A8")
    
    # 將 period 轉換為小端格式的字節串
    period_bytes = struct.pack("<H", period)
    print(f"period_bytes = {period_bytes}") 
    

    try:
        await client.write_gatt_char(characteristic_uuid, period_bytes)
        print(f"Successfully wrote period {period} to characteristic {characteristic_uuid}")
    except Exception as e:
        print(f"Failed to write to {characteristic_uuid}: {e}")

async def print_services(client, services):
    # 遍歷所有服務
    for service in services:
        print(f"\nService: {service.uuid}")

        # 遍歷服務的所有特徵值
        for characteristic in service.characteristics:
            print(f"  Characteristic: {characteristic.uuid}")
            print(f"    Properties: {characteristic.properties}")

            # 如果特徵值具有 'read' 屬性，則嘗試讀取值
            if "read" in characteristic.properties:
                try:
                    value = await client.read_gatt_char(characteristic.uuid)
                    print(f"    Read {characteristic.uuid}: {value}")
                except Exception as e:
                    print(f"    Failed to read {characteristic.uuid}: {e}")
def print_unique_services(services):
    unique_services = set()

    for service in services:
        # 只將唯一的 service UUID 添加到集合
        unique_services.add(service.uuid)
    
    print("\nUnique Services:")
    for service_uuid in unique_services:
        print(f"Service: {service_uuid}")

                    
async def print_values_for_uuid(client, services, target_uuid):
    # 遍歷所有服務並找出特定的 UUID
    for service in services:
        for characteristic in service.characteristics:
            if characteristic.uuid == target_uuid and "read" in characteristic.properties:
                try:
                    # 讀取特徵值
                    value = await client.read_gatt_char(characteristic.uuid)
                    print(f"Characteristic {characteristic.uuid}: {value}")
                except Exception as e:
                    print(f"Failed to read {characteristic.uuid}: {e}")

async def main():
    
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
    
    # 開啟一個任務來連接和接收數據
    #device_address = 'CA:59:0E:53:87:42'
    connect_task = asyncio.create_task(connect_to_device(device_address))
    
    # 等待用戶按鍵中斷
    print("Press Enter to exit.")
    await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)

    # 停止連接任務
    connect_task.cancel()
    try:
        await connect_task
    except asyncio.CancelledError:
        print("Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
