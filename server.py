from websocket_server import WebsocketServer

from ultrasonic import distance

# Car controls
import driver

# For sending time based messages
from threading import Thread
from time import sleep

wall = False

def call_at_interval(period, callback, args):
    while True:
        callback(*args)
        sleep(period)

def setInterval(period, callback, *args):
    Thread(target=call_at_interval, args=(period, callback, args)).start()

def send_distance():
    d = distance()
    # ignore random big readings
    if d < 2000:
        wall = d < 50
        print("w: %s forward?: %s" % (wall, driver.trav_fwd))
        server.send_message_to_all("distance:%f" % d)
        if wall and driver.trav_fwd == True:
            print("Should stop!")
            driver.reverse()
            sleep(0.5)
            driver.stop()

def new_client(client, server):
    print("New client connected, id: %d" % client['id'])
    server.send_message_to_all("Hey all, a new client has joined")
    server.send_message_to_all("distance:%f" % distance())

def client_left(client, server):
    print("Client %d disconnected" % client['id'])

def message_received(client, server, message):
    print("Client %d said %s" % (client['id'], message))
	
    if message == "throttle.forward" and wall != True:
        driver.forward()
    elif message == "throttle.reverse":
        driver.reverse()
    elif message == "throttle.off":
        driver.stop()
    elif message == "steering.left":
        driver.left()
    elif message == "steering.right":
        driver.right()
    elif message == "steering.straight":
        driver.straight()

# Websocket server
PORT=9001
server = WebsocketServer(PORT, '0.0.0.0')
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)

setInterval(0.05, send_distance)

server.run_forever()

