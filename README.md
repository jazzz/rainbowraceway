Readme for rpi neopixel library
Build:

- Install Scons (on raspbian, apt-get install scons).
- Make sure to adjust the parameters in main.c to suit your hardware.
  - Signal rate (400kHz to 800kHz).  Default 800kHz.
  - ledstring.invert=1 if using a inverting level shifter.
  - Width and height of LED matrix (height=1 for LED string).
- Type 'scons' from inside the source directory.


Running:
- connect RFID reader on USB port (need to add support for UART serial)
- connect neopixel lights on GPIO 18, common ground with raspberry's ground
- sudo scons (only the first time, run from the root folder of the project to build the lirabries)
- cd python/rainbow
- sudo python RFIDtest.py
