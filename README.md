# DynamIoT

The Geomatics Synthesis Project (GSP) is a culminating group project at the end of the first year 
of the Master of Geomatics, TU Delft. The project allows students to combine the knowledge
from the core programme and apply it to a real-world project while gaining hands-on experience 
in project management. The goal of the IoT dynamic project team was to develop a network of 
eight sensor platforms moving throughout the city of Delft, which would provide governmental 
bodies and also citizens with near-real-time environmental geo-data.

The platform is based on Pycom Lopy micro processor (MC) and a collection of sensor modules:
* GPS breakout board based on u-blox NEO-8M chip
* Temperature and humidity sensor AM2302
* Microphone with atomatic gain control MAX9814
* (still to be impemented) Particle sensor PMS5003

The communication is done by LoRa, while localization at the data collection stage is done by GPS, later on, by Wifi fingerprinting.
