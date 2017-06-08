import pycom
import time
from machine import Pin
from machine import Timer
from dth import DTH

import machine
from gps import *
from machine import RTC

from network import LoRa
from network import WLAN
import socket
import binascii
import ubinascii
import struct
import config
from math import log


pycom.heartbeat(False)
th = DTH(Pin('P10', mode=Pin.OPEN_DRAIN), 1)
adc = machine.ADC(bits=10)
apin = adc.channel(pin='P18')
SAMPLE_WINDOW = 50  # Sample window width in ms (50 ms = 20Hz)
sample = 0

#setting up the GPS
# connect to GPS device
gps = GPS_UART_start()
#Turning off automatic messages
GPS_disable_msg(gps)
gps.readall()
GPS_on(gps)

# LoRa details keys obtained from KPN
dev_addr = struct.unpack(">l", binascii.unhexlify(config.DEV_ADDR))[0]
# manually converted hex to decimal for better readability
#dev_addr = 337656918

nwks_key = binascii.unhexlify(config.NWKS_KEY)
apps_key = binascii.unhexlify(config.APPS_KEY)

# Setup LoRa
lora = LoRa(mode=LoRa.LORAWAN, adr=True)

# join a network using ABP
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwks_key, apps_key), timeout=0)

# create a LoRa socket
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
lora_sock.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)


def lora_tx(payload):
    lora_sock.send(payload)

#
byms = []
def send_blob():

    #WiFi RSSI
    wlanon = WLAN(mode=WLAN.STA, antenna=WLAN.EXT_ANT)
    scan = wlanon.scan()
    i = 0
    messages = []
    if len(scan) >=3:
        while i<3:
            messages.append(ubinascii.hexlify(scan[i].bssid, "/").decode())
            messages.append(scan[i].rssi)
            i += 1
    elif len(scan) == 2:
        while i<2:
            messages.append(ubinascii.hexlify(scan[i].bssid, "/").decode())
            messages.append(scan[i].rssi)
        for num in range(7):
            message.append(00)
    else:
        for num in range(21):
            message.append(00)

    for j, part in enumerate(messages):
        if j%2 == 0:
            for byt in part.split('/'):
                byms.append(int(byt, 16))
        elif j%2 == 1:
            byms.append(abs(part))

    #temperature and humidity
    result = th.read()
    byms.append(int(result.temperature))
    byms.append(int(result.humidity))
    print('temp appended')

    #sound
    chrono = Timer.Chrono()
    chrono.start()
    start_time = chrono.read_ms()

    peak_to_peak = 0  # peak-to-peak level
    signal_max = 0  # max signal
    signal_min = 1024  # min signal

    while (chrono.read_ms() - start_time) < SAMPLE_WINDOW:  # 50 ms
        sample = apin()  # read an analog value
        if sample > signal_max:
            signal_max = sample
        elif sample < signal_min:
            signal_min = sample

    peak_to_peak = signal_max - signal_min
    print(peak_to_peak)
    db = 0
    if peak_to_peak > 154:
        db = 20 * log((peak_to_peak)-(153.1) , 10)
    byms.append(int(db))

    #GPS message addition
    byms.append(int(lat[0:2]))
    byms.append(int(lat[2:4]))
    byms.append(int(lat[4:]))
    byms.append(int(lon[0:2]))
    byms.append(int(lon[2:4]))
    byms.append(int(lon[4:]))

    #sending with lora
    lora_tx(bytes(byms))
    print(byms)
    print('sent')

#gps information retrieval
time.sleep(30)
constant = 0
while constant < 5:
    #if (gps.any()):
    #gps.readall()
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
                print ("Latitude "+ str(lat) + ', longtitude ' + str(lon))
            else:
                print("No fix")


send_blob()
GPS_off(gps)
machine.deepsleep(240000)
