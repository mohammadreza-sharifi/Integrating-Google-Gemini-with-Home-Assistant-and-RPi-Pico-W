import network
from time import sleep
from umqtt.simple import MQTTClient
import ujson
from machine import Pin, ADC
import dht
import _thread

dht_sensor = dht.DHT11(Pin(15))
analog_value = ADC(Pin(26))
light = Pin(14,Pin.OUT)

def air_params():
    #sleep(2)
    dht_sensor.measure()
    temp = dht_sensor.temperature()
    hum = dht_sensor.humidity()
    #CO_value = analog_value.read_u16()
    
    return temp, hum

# Network credentials
WIFI_SSID = 'Mrsh77'
WIFI_PASSWORD = '1m77n2299215r77#'

# MQTT credentials
MQTT_BROKER = '192.168.1.232'
MQTT_PORT = 1883
MQTT_TOPIC = 'pico'

msg_from_node_red = []

# Connect to WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())

# Callback function to handle messages
def on_message(topic, msg):
    #print('Received message:', msg)
    msg_from_node_red.append(msg)
# Setup MQTT client and connect to the broker
def setup_mqtt():
    
    client = MQTTClient(client_id='pico_w_client', server=MQTT_BROKER, port=MQTT_PORT, user="mqtt", password="sharifi77mm98")
    

    client.set_callback(on_message)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print('Connected to %s, subscribed to %s topic.' % (MQTT_BROKER, MQTT_TOPIC))
    return client


connect_wifi(WIFI_SSID, WIFI_PASSWORD)

client = setup_mqtt()

def send_params():
    while True:
        temperature, humidity = air_params()
        sensor_data = {
            "temperature": temperature,
            "humidity": humidity
            }

        json_data = ujson.dumps(sensor_data)
        client.publish("pico_in",json_data)
        sleep(1)

def core1_task():
    try:
        while True:
            client.check_msg()
            if msg_from_node_red:
                
                final_msg = msg_from_node_red.pop(0)
                print(final_msg)
                if final_msg == b'light on':
                    light.value(1)
                elif final_msg == b'light off':
                    light.value(0)
                sleep(1)
    except KeyboardInterrupt:
        print('Disconnected from MQTT Broker.')
    finally:
        client.disconnect()


_thread.start_new_thread(core1_task, ())

send_params()