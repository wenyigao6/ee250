"""EE 250L Lab 07 Skeleton Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
import time

from grovepi import *
from grove_rgb_lcd import *

global led
global button
global ultrasonic_ranger
led = 4
button = 3
ultrasonic_ranger = 2

pinMode(led, "OUTPUT")
pinMode(button, "INPUT")


def led_callback(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    # print("custom_callback: " + message.topic + " " + "\"" + 
    #     str(message.payload, "utf-8") + "\"")
    # print("custom_callback: message.payload is of type " + 
    #       str(type(message.payload)))

    if str(message.payload, "utf-8") == "LED_ON":
        # do sth
        digitalWrite(led, 1)

    elif str(message.payload, "utf-8") == "LED_OFF":
        # do sth
        digitalWrite(led, 0)

def lcd_callback(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    # print("custom_callback: " + message.topic + " " + "\"" + 
    #     str(message.payload, "utf-8") + "\"")
    # print("custom_callback: message.payload is of type " + 
    #       str(type(message.payload)))
    setText(str(message.payload, "utf-8") )


def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    #subscribe to topics of interest here
    client.subscribe("anrg-pi8/led")
    client.message_callback_add("anrg-pi8/led", led_callback)

    client.subscribe("anrg-pi8/lcd")
    client.message_callback_add("anrg-pi8/lcd", lcd_callback)

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    setRGB(0,128,64)

    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    message = client.on_connect

    while True:
        # print("delete this line")
        time.sleep(1)

        client.publish("anrg-pi8/ultrasonicRanger", ultrasonicRead(ultrasonic_ranger))

        if digitalRead(button):
            client.publish("anrg-pi8/button", "Button pressed!")

        # if message == "LED_ON":
        #     # turn led on

        # elif message == "LED_OFF":
        #     # turn led off 
            
        # message = client.on_connect

        # # client.publish("anrg-pi8/ultrasonicRanger", dist)
