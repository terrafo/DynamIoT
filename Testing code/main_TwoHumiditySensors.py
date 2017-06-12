import time
from machine import Pin
from dth import DTH

# data pin connected to P11
# 1 for AM2302
inside = DTH(Pin('P10', mode=Pin.OPEN_DRAIN), 1)
outside = DTH(Pin('P9', mode=Pin.OPEN_DRAIN), 1)
time.sleep(2)

while True:
    resultIn = inside.read()
    print(resultIn, type(resultIn))
    print(resultIn.is_valid())
    print('TemperatureIn: {:3.2f}'.format(resultIn.temperature / 1.0))
    print('HumidityIn: {:3.2f}'.format(resultIn.humidity / 1.0))
    resultOut = outside.read()
    print(resultOut, type(resultOut))
    print(resultOut.is_valid())
    print('TemperatureOut: {:3.2f}'.format(resultOut.temperature / 1.0))
    print('HumidityOut: {:3.2f}'.format(resultOut.humidity / 1.0))
    # if result.is_valid():
    with open("results.txt", 'a') as output:
        output.write("{:3.2f};{:3.2f};{:3.2f};{:3.2f}   ".format(
        resultIn.temperature / 1.0, resultIn.humidity / 1.0,
        resultOut.temperature / 1.0, resultOut.humidity / 1.0
        ))
        output.write('\n')
    time.sleep(20)
