# piCarD
(Pi Car Driver) Simple RC car controls with maybe some autonomous capabilities.

# Setup
Enable i2c and the pi camera modules using raspi-config command

Uses adafruit motor controller hat for motor controls https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi, and their python lib.

Install sqlite:
`apt-get install sqlite3`

Install gpsd (for gps)
`sudo apt-get -y install gpsd gpsd-clients python-gps`

`sudo pip3 install adafruit-circuitpython-motorkit`
`sudo pip3 install websocket-server`
`sudo pip3 install sqlite3`


Install openCV by following these instructions: https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/

Maybe more required. I forget everything I did when setting everything up

## GPS
Edit `/etc/default/gpsd`
Make sure it looks like this (You'll need to add the device and the SOCKET as well as change the GPSD_OPTIONS:
```
# Start the gpsd daemon automatically at boot time
START_DAEMON="true"

# Use USB hotplugging to add new USB devices automatically to the daemon
USBAUTO="true"

# Devices gpsd should collect to at boot time.
# They need to be read/writeable, either by user gpsd or the group dialout.
DEVICES="/dev/ttyACM0"

# Other options you want to pass to gpsd
GPSD_SOCKET="/var/run/gpsd.sock"
GPSD_OPTIONS="-n"
```
Edit `/etc/rc.local`
Add these lines:
```
/bin/systemctl stop gpsd.socket
/bin/sleep 1
/usr/sbin/gpsd /dev/ttyACM0 -n -F /var/run/gpsd.sock
/bin/sleep 1
/usr/sbin/service ntp restart
```

Edit `/etc/ntp.conf`
Add these lines:
```
# Use GPS Receiver
server 127.127.28.0 prefer
fudge 127.127.28.0 time1 0.0 refid GPS
# GPS PPS reference, if provided by GPS device
server 127.127.28.1 prefer
fudge 127.127.28.1 refid PPS
```
Enable the service:
`sudo systemctl enable gpsd.socket`
Start the service:
`sudo systemctl start gpsd.socket`

Last, install the `gpsd-py3` library
`sudo pip3 install gpsd-py3`

## Run

```
workon cv
python3 detector/stream.py &
sudo python3 server.py &
cd control
sudo python3 -m http.server 80
```
