# piCar
Simple RC car controls with maybe some autonomous capabilities.

## Run

```
workon cv
python3 detector/stream.py &
sudo python3 server.py &
cd control
sudo python3 -m http.server 80
```
