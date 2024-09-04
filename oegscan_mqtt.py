#!/usr/bin/python3

# Dictionary to store OEG data
oeg_dict = {
    38: "",  # T1
    39: "",  # T2
    40: "",  # T3
    58: "",  # Pump modulation 0-100%
}

import minimalmodbus
import serial
import time
import paho.mqtt.client as mqtt

# Setup minimalmodbus instrument
try:
    instrument = minimalmodbus.Instrument('/dev/ttyACM0', 128, minimalmodbus.MODE_ASCII)  # Adjust the port name
    instrument.serial.baudrate = 9600   # Baud rate
    instrument.serial.parity = serial.PARITY_EVEN
    instrument.serial.bytesize = 7
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 0.05  # seconds
except Exception as e:
    print(f"Error setting up the instrument: {e}")
    exit(1)

# MQTT broker information
broker = '192.168.3.98'  # Replace with your MQTT broker IP-address
mqtt_username = 'mosquito'
mqtt_password = 'mosquito0987654321'
delay = 5

try:
    # Initialize the MQTT client
    client = mqtt.Client("ha-client")
    client.username_pw_set(mqtt_username, mqtt_password)
    client.connect(broker)
    client.loop_start()

    # Main loop to publish data
    while True:
        try:
            state_topic = "home-assistant/oeg/OegT1"
            value = instrument.read_register(38, 1, 3, signed=True)
            client.publish(state_topic, value)
            print(f"Published {value} to {state_topic}")

            state_topic = "home-assistant/oeg/OegT2"
            value = instrument.read_register(39, 1, 3, signed=True)
            client.publish(state_topic, value)
            print(f"Published {value} to {state_topic}")

            state_topic = "home-assistant/oeg/OegT3"
            value = instrument.read_register(40, 1, 3, signed=True)
            client.publish(state_topic, value)
            print(f"Published {value} to {state_topic}")

            state_topic = "home-assistant/oeg/Oegpomp"
            value = instrument.read_register(58, 0, 3, signed=True)
            client.publish(state_topic, value)
            print(f"Published {value} to {state_topic}")

            time.sleep(delay)

        except minimalmodbus.NoResponseError as e:
            print(f"No response from the instrument: {e}")
        except Exception as e:
            print(f"An error occurred during the loop: {e}")

except Exception as e:
    print(f"An error occurred setting up MQTT client or in main loop: {e}")

finally:
    # Ensure the client is properly disconnected and the loop stopped
    try:
        client.loop_stop()  # Stop the MQTT loop
        client.disconnect()  # Disconnect from the MQTT broker
        print("MQTT client disconnected.")
    except Exception as cleanup_error:
        print(f"Error during cleanup: {cleanup_error}")
