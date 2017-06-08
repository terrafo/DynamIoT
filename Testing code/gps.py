import os
import time
import machine
from machine import UART

#Sleep mode
def GPS_off(gps):
    #data = [0xB5, 0x62, 0x06, 0x11, 0x02, 0x00, 0x08, 0x01, 0x22, 0x92]
    data = [0xB5, 0x62, 0x06, 0x04, 0x04, 0x00, 0x00, 0x00,0x08, 0x00, 0x16, 0x74]
    #sending byte array of the UBX protocol to the GPS
    for i in data:
        gps.write(chr(i))
    print("GPS off")

#High power mode
def GPS_on(gps):
    data = [0xB5, 0x62, 0x06, 0x04, 0x04, 0x00, 0x00, 0x00,0x09, 0x00, 0x17, 0x76]
    #sending byte array of the UBX protocol to the GPS
    for i in data:
        gps.write(chr(i))
    print("GPS on")

#Power save mode
def power_save_mode(gps):
    data = [0xB5, 0x62, 0x06, 0x11, 0x02, 0x00, 0x08, 0x01, 0x22, 0x92]
    #sending byte array of the UBX protocol to the GPS
    for i in data:
        gps.write(chr(i))
    print("Power save mode")

def GPS_disable_msg(gps):
    gps.write('$PUBX,40,GLL,0,0,0,0,0,0*5C\r\n')
    gps.write('$PUBX,40,GGA,0,0,0,0,0,0*5A\r\n')
    gps.write('$PUBX,40,GSA,0,0,0,0,0,0*4E\r\n')
    gps.write('$PUBX,40,RMC,0,0,0,0,0,0*47\r\n')
    gps.write('$PUBX,40,GSV,0,0,0,0,0,0*59\r\n')
    gps.write('$PUBX,40,VTG,0,0,0,0,0,0*5E\r\n')
    gps.readall()

def GPS_UART_start():
    #print ('Start GPS UART1')
    com = UART(1,  pins=("P3",  "P4"),  baudrate=9600)
    # pins=("G23",  "G24")
    time.sleep(1)
    return(com)


def GPS_go(com):
    while (True):
        if (com.any()):
            data =com.readline()
            #print (data)
            if (data[0:6] == b'$GPGGA'):
                place = NmeaParser()
                place.update(data)
                print (place.longitude,  ":",  place.latitude)
                info1 = struct.pack('hii',  machine.rng()&0xffff,  int(place.longitude*100000),  int(place.latitude*100000))


def parse_data(data_in):
    data = str(data_in).split(',')
    #print('Length: ' + str(len(data)))
    if len(data) == 21:
        l_string = data[3]
        lat_degs = float(l_string[0:2])
        lat_mins = float(l_string[2:])
        lat_hemi = data[4]

        l_string = data[5]
        lon_degs = float(l_string[0:3])
        lon_mins = float(l_string[3:])
        lon_hemi = data[6]

        latitude = lat_degs + (lat_mins/60)
        if lat_hemi == 'S':
            latitude = -latitude
        longitude = lon_degs + (lon_mins/60)
        if lon_hemi == 'W':
            longitude = -longitude
        return [latitude, longitude]
    else:
        return [0,0]

com=GPS_UART_start()
