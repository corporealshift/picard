# import the necessary packages
import argparse
import imutils
import numpy as np
import os
import cv2
import io
import random
import picamera
import logging
import socketserver
from time import sleep
from threading import Condition
from http import server
from picamera.array import PiRGBArray
from picamera import PiCamera

PAGE="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

def focusing(val):
    value = (val << 4) & 0x3ff0
    data1 = (value >> 8) & 0x3f
    data2 = value & 0xf0
    os.system("i2cset -y 1 0x0c %d %d" % (data1,data2))

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                # initialize the camera and grab a reference to the raw camera capture
                sleep(0.1)
                while(True):
                    # Capture frame-by-frame
                    ret, frame = cap.read()
                    image = cv2.resize(frame, (640, 480))
                    # encoded, image = cv2.imencode('.jpg', frame)
                    
                    # Our operations on the frame come here
                    # Make brighter, more contrasty
                    image_bright = cv2.convertScaleAbs(image, alpha=3, beta=1.5)
                    gray = cv2.cvtColor(image_bright, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

                    # Maybe better?
                    # blurred = cv2.medianBlur(gray, 5)
                    # thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 2)
                    
                    # ret3, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                    # find contours in the thresholded image
                    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)

                    # Can do edge detection this way, but it seems not as good?
                    # edges = cv2.Canny(gray, 100, 200)

                    # loop over the contours
                    for c in cnts:
                        # compute the center of the contour
                        M = cv2.moments(c)
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                            # draw the contour and center of the shape on the image
                            cv2.drawContours(image, [c], -1, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)), 2)
                            cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
                            cv2.putText(image, "ctr", (cX - 20, cY - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Display the resulting frame
                    encoded, output = cv2.imencode('.jpg', image)

                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(output))
                    self.end_headers()
                    self.wfile.write(output)
                    self.wfile.write(b'\r\n')
                    
                
                # allow the camera to warmup
                # sleep(1)
                
                # capture frames from the camera
                # for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                    # Create an actual image from the byte frame
                    # nparr = np.fromstring(frame, np.uint8)
                    # image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    # image = frame.array

                    # # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    # blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    # thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

                    # # find contours in the thresholded image
                    # cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                    #     cv2.CHAIN_APPROX_SIMPLE)
                    # cnts = imutils.grab_contours(cnts)

                    # # loop over the contours
                    # for c in cnts:
                    #     # compute the center of the contour
                    #     M = cv2.moments(c)
                    #     if M["m00"] != 0:
                    #         cX = int(M["m10"] / M["m00"])
                    #         cY = int(M["m01"] / M["m00"])
                    #         # draw the contour and center of the shape on the image
                    #         cv2.drawContours(image, [c], -1, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)), 2)
                    #         cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
                    #         cv2.putText(image, "center", (cX - 20, cY - 20),
                    #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    # # print("Writing buffer %d" % len(image))

                    # self.wfile.write(b'--FRAME\r\n')
                    # self.send_header('Content-Type', 'image/jpeg')
                    # self.send_header('Content-Length', len(image))
                    # self.end_headers()
                    # self.wfile.write(image)
                    # self.wfile.write(b'\r\n')

                    # # Clear capture buffer
                    # rawCapture.truncate(0)

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

# with picamera.PiCamera(resolution='640x480', framerate=32) as camera:
    
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    # camera.start_recording(output, format='mjpeg')
    # camera = PiCamera()
    # camera.resolution = (640, 480)
    # camera.framerate = 32
    # rawCapture = PiRGBArray(camera, size=(640, 480))
    # sleep(2)
try:
    # output = StreamingOutput()
    focusing(100)
    cap = cv2.VideoCapture(0)
    address = ('', 8000)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
finally:
    cap.release()
    # camera.stop_recording()

# # load the image, convert it to grayscale, blur it slightly,
# # and threshold it
# image = cv2.imread(args["image"])
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# blurred = cv2.GaussianBlur(gray, (5, 5), 0)
# thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

# # find contours in the thresholded image
# cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
# 	cv2.CHAIN_APPROX_SIMPLE)
# cnts = imutils.grab_contours(cnts)

# # loop over the contours
# for c in cnts:
# 	# compute the center of the contour
# 	M = cv2.moments(c)
# 	cX = int(M["m10"] / M["m00"])
# 	cY = int(M["m01"] / M["m00"])

# 	# draw the contour and center of the shape on the image
# 	cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
# 	cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)
# 	cv2.putText(image, "center", (cX - 20, cY - 20),
# 		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

# 	# show the image
# 	cv2.imshow("Image", image)
# 	cv2.waitKey(0)
