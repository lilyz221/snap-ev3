#!/usr/bin/env python
import os
import sys

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import ev3dev.ev3 as ev3

from mock_devices import *
from snap_server import *


ev3.Device.DEVICE_ROOT_PATH = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'fake_sys_class')

print "DEVICE_ROOT_PATH =", ev3.Device.DEVICE_ROOT_PATH

motor1 = MockMediumMotor(ev3.Device.DEVICE_ROOT_PATH, "outA")
motor2 = MockLargeMotor(ev3.Device.DEVICE_ROOT_PATH, "outB")
sensor1 = MockColorSensor(ev3.Device.DEVICE_ROOT_PATH, "in1")

port = 9000
if len(sys.argv) > 1:
    port = int(sys.argv[1])

start_server(port)

    

