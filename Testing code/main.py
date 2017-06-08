import pycom
import time
from machine import Pin
from dth import DTH
from network import LoRa, WLAN
import socket
import config
import binascii
import ubinascii
import struct
from gps import *

pycom.heartbeat(True)
wlanon = WLAN(mode=WLAN.AP, antenna=WLAN.EXT_ANT)
for i in range(15):
    time.sleep(1)
    print("Waiting " + str(i))

# connect to GPS device
gps = GPS_UART_start()
#Turning off automatic messages
GPS_disable_msg(gps)
GPS_on(gps)
gps.readall()




# data pin connected to P11
# 1 for AM2302

#lora properties
# LoRa details keys obtained from KPN
dev_addr = struct.unpack(">l", binascii.unhexlify(config.DEV_ADDR))[0]
# manually converted hex to decimal for better readability
#dev_addr = 337656918

nwks_key = binascii.unhexlify(config.NWKS_KEY)
apps_key = binascii.unhexlify(config.APPS_KEY)

# Setup LoRa
print("lora setup")
lora = LoRa(mode=LoRa.LORAWAN, adr=True)
# join a network using ABP
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwks_key, apps_key), timeout=0)
# create a LoRa socket
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
def lora_tx(payload):
    lora_sock.send(payload)

#filename = "result.txt"
#target = open(filename, 'w')
#target.truncate()
th = DTH(Pin('P10', mode=Pin.OPEN_DRAIN), 1)


counter = 0
while counter < 60:
    GPS_on(gps)
    for i in range(30):
        print("Waiting " + str(i))
        time.sleep(1)
    constant = 0
    while constant < 5:
        print("Try" + str(constant))
        #if (gps.any()):
        gps.readall()
        gps.write("$PUBX,00*33\r\n")
        time.sleep(1.2)
        data = gps.readline()
        print(str(data))
        if data != None:
            if data[0:5] == b'$PUBX':
                parsed_data = parse_data(data)
                latitude = parsed_data[0]
                longitude = parsed_data[1]
                constant +=1
                if latitude != 0 or longitude != 0:
                    print('fix')
                    constant = 5
                    const_lat = 51.9627
                    const_lon = 4.3161
                    lat = str(int(1000000*(latitude - const_lat)))
                    lon = str(int(1000000*(longitude - const_lon)))
                    print ("Latitude "+ str(latitude) + ', longitude ' + str(longitude))
                else:
                    print("No fix")
    GPS_off(gps)
    result = th.read()
    print(result.temperature)
    print(result.humidity)
    print("Lora sending")
    lora_tx(bytes([55,55,55]))



    """print("measuring \n")
    with open ("result.txt", "a") as f:
        result = th.read()
        print(result,type(result))
        f.write("Temperature: {:3.2f} \n".format(result.temperature / 1.0))
        f.write("Humidity: {:3.2f} \n").format(float(result.humidity) /1.0) #why :3.2f?"""
    #print(result, type(result))
    #print(result.is_valid())
    # if result.is_valid():
    #target.write('{:3.2f};'.format(result.temperature / 1.0))
    #target.write('{:3.2f}\n'.format(result.humidity / 1.0))
    #print('Temperature: {:3.2f}'.format(result.temperature / 1.0))
    #print('Humidity: {:3.2f}'.format(result.humidity / 1.0))
    counter = counter + 1
    time.sleep(2)

#target.close()
