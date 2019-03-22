from adafruit_motorkit import MotorKit

kit = MotorKit()
trav_fwd = False
def left():
    print("left")
    kit.motor2.throttle = 1

def right():
    print("right")
    kit.motor2.throttle = -1

def straight():
    print("straight")
    kit.motor2.throttle = 0

def forward():
    print("forward")
    global trav_fwd
    trav_fwd = True
    kit.motor1.throttle = 0.75

def reverse():
    print("reverse")
    global trav_fwd
    trav_fwd = False
    kit.motor1.throttle = -0.75

def stop():
    print("stop")
    global trav_fwd
    trav_fwd = False
    kit.motor1.throttle = 0
