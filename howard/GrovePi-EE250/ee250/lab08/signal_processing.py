import paho.mqtt.client as mqtt
import time
import requests
import json
from datetime import datetime

# MQTT variables
broker_hostname = "eclipse.usc.edu"
broker_port = 11000
ultrasonic_ranger1_topic = "ultrasonic_ranger1"
ultrasonic_ranger2_topic = "ultrasonic_ranger2"

# Lists holding the ultrasonic ranger sensor distance readings. Change the 
# value of MAX_LIST_LENGTH depending on how many distance samples you would 
# like to keep at any point in time.
MAX_LIST_LENGTH = 100
ranger1_dist = []
ranger2_dist = []

def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    ranger1_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]

def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    ranger2_dist.append(int(msg.payload))
    #truncate list to only have the last MAX_LIST_LENGTH values
    ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(ultrasonic_ranger1_topic)
    client.message_callback_add(ultrasonic_ranger1_topic, ranger1_callback)
    client.subscribe(ultrasonic_ranger2_topic)
    client.message_callback_add(ultrasonic_ranger2_topic, ranger2_callback)

# The callback for when a PUBLISH message is received from the server.
# This should not be called.
def on_message(client, userdata, msg): 
    print(msg.topic + " " + str(msg.payload))

if __name__ == '__main__':
    # Connect to broker and start loop    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)
    client.loop_start()

    hdr = {
        'Content-Type': 'application/json',
        'Authorization': None #not using HTTP secure
    }

    # The payload of our message starts as a simple dictionary. Before sending
    # the HTTP message, we will format this into a json object
    


    cnt = 0
    msg = ""

    # as the key is to determine  whether
    # the object has moved or not through a time window - instead of giving
    # feed back in real time (or every 0.2 second)
    # so i will set different counters for each outcome (e.g. move left, move right,
    # stand still - middle, stc.) And the state (or outcome) is ditermined by 
    # whether these counters has continuously incremented throughout certain
    # period of time, which is determined by the variavles "moved" and "still"

    m_r = 0
    m_l = 0

    s_m = 0
    s_r = 0
    s_l = 0 

    delta1 = 0
    delta2 = 0
    prev1 = int(sum(ranger1_dist)/(len(ranger1_dist)+1))
    prev2 = int(sum(ranger2_dist)/(len(ranger2_dist)+1))

    ind = 3
    moved = 3
    still = 5

    while True:
        """ You have two lists, ranger1_dist and ranger2_dist, which hold a window
        of the past MAX_LIST_LENGTH samples published by ultrasonic ranger 1
        and 2, respectively. The signals are published roughly at intervals of
        200ms, or 5 samples/second (5 Hz). The values published are the 
        distances in centimeters to the closest object. Expect values between 
        0 and 512. However, these rangers do not detect people well beyond 
        ~125cm. """
        
        # TODO: detect movement and/or position

        # set a cnt and do nothing until cnt > 10 which is 2 secs after 
        # the signal has been collected - to make sure the list is not empty
        cnt += 1
        if cnt > 10:

            avg1 = int(sum(ranger1_dist)/(len(ranger1_dist)+1))
            avg2 = int(sum(ranger2_dist)/(len(ranger2_dist)+1))
            # delta1 = avg1 - prev1
            # delta2 = avg2 - prev2
            delta1 = ranger1_dist[-1] - prev1
            delta2 = ranger2_dist[-1] - prev2

            # moved left
            # increment m_l and update all other counters to 0
            # moved right is similar
            if delta1 < -ind or delta2 > ind:
                m_l += 1
                m_r = 0
                s_m = 0
                s_r = 0
                s_l = 0
            # moved right 
            if delta1 > ind or delta2 < -ind :
                m_l = 0
                m_r += 1
                s_m = 0
                s_r = 0
                s_l = 0
            # stand still - middle
            if ranger1_dist[-1] < 85 and ranger2_dist[-1] < 85 :
                s_m += 1
                
                s_l = 0
                s_r = 0
            # stand still - right
            elif ranger1_dist[-1] < 50 and ranger2_dist[-1] > 100 and abs(delta1)<ind:
                s_m =0
                
                s_l = 0
                s_r += 1
            # stand still left
            elif ranger2_dist[-1] < 50 and ranger1_dist[-1] > 100 and abs(delta2)<ind:
                s_m =0
                
                s_l += 1
                s_r = 0

            # NOTE:
            # the program will ONLY output when one of the conditions has
            # been satisfied, otherwise nothing will get output.
            
            # to see if the movements has lasted long enough
            if m_l>=moved:
                print("moved RIGHT")
                msg = "moved RIGHT"
                m_l = 0
                payload = {
                'time': str(datetime.now()),
                'event': msg
                }

                response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                     data = json.dumps(payload))
            if m_r>=moved:
                print("moved LEFT")
                msg = "moved LEFT"
                m_r = 0
                payload = {
                'time': str(datetime.now()),
                'event': msg
                }

                response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                     data = json.dumps(payload))
            if s_m>=still:
                print("st MID")
                msg = "st MID"
                s_m = 0
                payload = {
                'time': str(datetime.now()),
                'event': msg
                }

                response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                     data = json.dumps(payload))
            if s_l>=still:
                print("st LEFT")
                msg = "st LEFT"
                s_l = 0
                payload = {
                'time': str(datetime.now()),
                'event': msg
                }

                response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                     data = json.dumps(payload))
            if s_r>=still:
                print("st RIGHT")
                msg = "st RIGHT"
                s_r = 0
                payload = {
                'time': str(datetime.now()),
                'event': msg
                }

                response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                     data = json.dumps(payload))

            

        # print("ranger1: " + str(ranger1_dist[-1:]) + ", ranger2: " + 
            # str(ranger2_dist[-1:]) + "average_1: " + str(delta1) + 
            # ", average_2: " + str(delta2) )

            # prev1 = int(sum(ranger1_dist)/(len(ranger1_dist)+1))
            # prev2 = int(sum(ranger2_dist)/(len(ranger2_dist)+1))
        
            prev1 = ranger1_dist[-1]
            prev2 = ranger2_dist[-1]
        
        time.sleep(0.2)