from bleak import BleakClient
import asyncio
import struct
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import queue
from bleak import BleakScanner
import threading
import time

# Queue for storing data
data_queue = queue.Queue()

# Lists for storing data
timestamps = []
magnitudes = []

# Set up the plot
fig, ax = plt.subplots()

# Flag to control the Bluetooth loop
running = True

def update_plot(frame):
    global timestamps, magnitudes
    # Get the latest data from the queue
    while not data_queue.empty():
        timestamp, magnitude = data_queue.get()
        timestamps.append(timestamp)
        magnitudes.append(magnitude)

        # Keep data within 100 points
        if len(timestamps) > 100:
            timestamps = timestamps[-100:]
            magnitudes = magnitudes[-100:]

    # Clear current plot and redraw
    ax.clear()
    ax.plot(timestamps, magnitudes, label='Magnitude')
    # ax.set_xlabel('Time (s)')
    # ax.set_ylabel('Magnitude')
    # ax.set_title('Real-time Accelerometer Magnitude')
    # ax.legend()

    # Return the plot object to ensure animation continues
    return ax

async def read_accelerometer_data(client):
    characteristic_uuid = "E95DCA4B-251D-470A-A062-FA1922DFA9A8"

    try:
        value = await client.read_gatt_char(characteristic_uuid)
        x, y, z = struct.unpack("<hhh", value)
        x, y, z = x / 1000.0, y / 1000.0, z / 1000.0
        magnitude = math.sqrt(x**2 + y**2 + z**2)
        current_time = time.time() - start_time

        data_queue.put((current_time, magnitude))

        #print(f"Accelerometer Data -> X: {x:.3f}, Y: {y:.3f}, Z: {z:.3f}, Magnitude: {magnitude:.3f}")
    except Exception as e:
        print(f"Failed to read {characteristic_uuid}: {e}")
        

async def connect_to_device(device_address):
    global running
    device = await BleakScanner.find_device_by_address(device_address)
    if not device:
        print(f"Could not find device with address {device_address}")
        running = False
        return

    async with BleakClient(device) as client:
        if await client.is_connected():
            print(f"Connected to {device_address}")
            while running and await client.is_connected():
                await read_accelerometer_data(client)
                await asyncio.sleep(0.001)  # Reduced sleep time for more frequent updates
            print("Device disconnected.")

def run_bluetooth_loop(device_address):
    asyncio.run(connect_to_device(device_address))

def on_close(event):
    global running
    running = False
    plt.close('all')

def main():
    global start_time, running
    device_address = 'CA:59:0E:53:87:42'
    start_time = time.time()

    # Start the Bluetooth loop in a separate thread
    bluetooth_thread = threading.Thread(target=run_bluetooth_loop, args=(device_address,))
    bluetooth_thread.start()

    # Set up the animation
    ani = animation.FuncAnimation(fig, update_plot, interval=10, cache_frame_data=False)

    # Set up the close event
    fig.canvas.mpl_connect('close_event', on_close)

    # Run the Matplotlib GUI in the main thread
    plt.show()

    # After the plot window is closed, stop the Bluetooth thread
    running = False
    bluetooth_thread.join()

if __name__ == "__main__":
    main()