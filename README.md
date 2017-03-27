Running:
- connect RFID reader on USB port (need to add support for UART serial)
- connect neopixel lights on GPIO 18, common ground with raspberry's ground
- git clone https://github.com/Margravegit/rainbowraceway.git
- apt-get install scons
- sudo scons (only the first time, run from the root folder of the project to build the lirabries)
- cd python/rainbow
- sudo python RFIDtest.py
