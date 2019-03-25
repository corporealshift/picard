# piCarD
(Pi Car Driver) Simple RC car controls with maybe some autonomous capabilities.

# Setup
Enable i2c and the pi camera modules using raspi-config command

Uses adafruit motor controller hat for motor controls https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi, and their python lib.

`sudo pip3 install adafruit-circuitpython-motorkit`

Install openCV by following these instructions: https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/

Maybe more required. I forget everything I did when setting everything up

## Run

```
workon cv
python3 detector/stream.py &
sudo python3 server.py &
cd control
sudo python3 -m http.server 80
```
