import google.generativeai as genai
import paho.mqtt.publish as publish
import random
import paho.mqtt.client as mqtt
from time import sleep
# MQTT parameters
MQTT_SERVER = "192.168.1.232" #mqtt broker ip
MQTT_PATH = "test" #topic
port = 1883
'''
broker = '192.168.1.232'
port = 1883
topic = "test"
'''
final_msg = []

client_id = f'python-mqtt-{random.randint(0, 1000)}'

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc, properties=None):
    client.username_pw_set('mqtt', 'sharifi77mm98')

    print("Connected with result code "+str(rc))
    
    client.subscribe("question")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print(msg.payload.decode())
    message = msg.payload.decode()
    final_msg.append(message)
    print(message)
# Create an MQTT client and attach our routines to it.
# Specify the new callback API version
client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_SERVER, port, 60)

# Process network traffic and dispatch callbacks.
client.loop_start()


genai.configure(api_key="AIzaSyDSFt21TMaIhJOahjg6YxRA2DStFrG7sAY")

model = genai.GenerativeModel('gemini-1.0-pro-latest')


while True:
    if final_msg:
        nodered_message = final_msg.pop(0)
        #print(nodered_message)
        response = model.generate_content(str(nodered_message))
        print(response.text)
        publish.single("response", response.text, hostname=MQTT_SERVER, auth={'username':"mqtt", 'password':"sharifi77mm98"})
        sleep(1)
    else:
        continue
        
    
