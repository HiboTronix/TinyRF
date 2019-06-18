# Copyright (c) 2019 Hibotronix
# Author: Hibotronix
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from radio import Radio
from registers import RF69_868MHZ as FREQ_868MHZ
import smbus
import RPi.GPIO as GPIO
import datetime
import time
import TinyRF_OLED
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# Input pins:
A_pin = 29 
B_pin = 31
C_pin = 32 

GPIO.setmode(GPIO.BOARD) 

GPIO.setup(A_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(B_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(C_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

# 128x32 display with hardware I2C:
disp = TinyRF_OLED.TinyRF_OLED_128x32()

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
width = disp.width
height = disp.height
#image = Image.new('1', (width, height))
imageBG = Image.open('node_data.bmp').convert('1')

# Get drawing object to draw on image.
draw = ImageDraw.Draw(imageBG)
#font = ImageFont.load_default()
fontS = ImageFont.truetype('TinyRF_Font_14px.ttf', 8)
fontL = ImageFont.truetype('TinyRF_Font_14px.ttf', 14)

pi_gateway_id = 1
pi_network_id = 100
pi_auto_acknowledge = False #Automatically send acknowledgements
pi_isHighPower = True #Is this a high power radio model
pi_power = 100 #Power level - a percentage in range 10 to 100.
pi_promiscuousMode = False #Listen to all messages not just those addressed to this node ID.
pi_encryptionKey = "TinyRFSensorNode" #16 character encryption key.
pi_verbose = False #Verbose mode - Activates logging to console.

with Radio(FREQ_868MHZ, pi_gateway_id, pi_network_id, isHighPower=pi_isHighPower, verbose=pi_verbose, auto_acknowledge=pi_auto_acknowledge, promiscuousMode=pi_promiscuousMode, power=pi_power) as radio:
#with Radio(FREQ_868MHZ, pi_gateway_id, pi_network_id, isHighPower=pi_isHighPower, verbose=pi_verbose, auto_acknowledge=pi_auto_acknowledge, promiscuousMode=pi_promiscuousMode, power=pi_power, encryptionKey=pi_$
    print("Radio Initialized\nStarting loop...")
    print("Listening at 868MHz...\n")

    try:
        while 1:
            if radio.has_received_packet():
                data_out = ""
                db_data = ""
                ts = time.gmtime()
                print("[Packet Received]")
                for packet in radio.get_packets():
                    if packet.receiver == pi_gateway_id or packet.receiver == 255:
                        data_out = "#[ "+time.strftime("%c", ts)+" ][Sender NodeID: "+str(packet.sender)+"][Data Packet: "
                        for list_item in range(len(packet.data)): 
                            data_out += chr(packet.data[list_item])
                            db_data += chr(packet.data[list_item])
                        data_out += "][RX_RSSI: "+str(packet.RSSI)+"]"
                        print(data_out)
                        radio.send_ack(packet.sender, "ACK")
                        print("[ACK Sent To NodeID: "+str(packet.sender)+" ]")
                        db_data_list = db_data.split()
                        draw.rectangle([(32,0),(64,15)], outline=0, fill=0)#RSSI
                        draw.rectangle([(80,0),(127,15)], outline=0, fill=0)#temp
                        draw.rectangle([(19,15),(64,15)], outline=0, fill=0)#pressure
                        draw.rectangle([(80,15),(127,15)], outline=0, fill=0)#humidity
                        draw.text((4, 2), str(packet.sender), font=fontS, fill=0)
                        tempvar = db_data_list[0].lstrip("T:")
                        draw.text((80, 0), tempvar.split('.', 1)[0]+" C", font=fontL, fill=255)
                        tempvar = db_data_list[1].lstrip("H:")
                        draw.text((80, 15), tempvar.split('.', 1)[0]+" %", font=fontL, fill=255)
                        tempvar = db_data_list[2].lstrip("P:")
                        draw.text((19, 15), tempvar.split('.', 1)[0], font=fontL, fill=255)
                        draw.text((32, 0), str(packet.RSSI), font=fontL, fill=255)

            # if not GPIO.input(A_pin):
            #     draw.text((0, 0), 'Button A!', font=font, fill=255)
            # elif not GPIO.input(B_pin):
            #     draw.text((0, 0), 'Button B!', font=font, fill=255)
            # elif not GPIO.input(C_pin):
            #     draw.text((0, 0), 'Button C!', font=font, fill=255)
            # else:
            #     draw.rectangle((0,0,width,height), outline=0, fill=0)
            disp.image(imageBG)
            disp.display()   
            time.sleep(.01) 

    except KeyboardInterrupt: 
        GPIO.cleanup()