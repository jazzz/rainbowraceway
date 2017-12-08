# RainbowRaceway
Internal command and control platform for the [RainbowRaceway project](https://www.facebook.com/Rainbow-Raceway-2134770673415594/)

## Environment Setup
* ARMv6Z (32-bit) device (such as RaspberryPi 1 or RaspberryPi Zero) - this is an untested limition from the light library
* OS:[Raspbian Stretch Lite(Recommended)](https://www.raspberrypi.org/downloads/raspbian/)
* Python 3.5+
* WIFI (for initial package installation)

## Build + Install
To install:
```
sudo ./build.sh
```
To clean:
```
sudo ./build.sh clean
```

## Usage + Operation
This project uses Systemctl to manage the process. It autoruns on boot and will auto restart on a failure. If for some reason you need to interact with the process, below are the most common terminal commands.

To check status
```
systemctl status rainbowraceway
```

To stop
```
sudo systemctl stop rainbowraceway
```

To start
```
sudo systemctl start rainbowraceway
```

## Developers
More technical information can found [#####here####]