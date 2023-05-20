import time
from kipr import msleep, gyro_z
from typing import Optional, Callable

from utilities import wait_for_button

error_multiplier = 1.0
momentum_multiplier = 1.0
gyro_offset = 0.0
drive: Optional[Callable[[int, int], None]] = None
stop: Optional[Callable[[], None]] = None
is_init = False


def calibrate_gyro():
    total = 0
    for x in range(50):
        total = total + gyro_z()
        msleep(10)
    global gyro_offset
    gyro_offset = total / 50


def gyroscope():
    return gyro_z() - gyro_offset


def gyro_turn(left_speed, right_speed, angle):
    if not is_init:
        print("GYRO NOT INITIALIZED FOR TURN!")
        exit(0)
    old_time = time.time()
    drive(left_speed, right_speed)
    current_turned_angle = 0
    fixed_angle = abs(angle)-abs(right_speed-left_speed) * momentum_multiplier
    while abs(current_turned_angle) < fixed_angle:
        current_turned_angle += error_multiplier * gyroscope() * (time.time() - old_time) / 8
        old_time = time.time()
        msleep(10)
    stop()


def gyro_init(drive_function, stop_function, momentum_adjustment, gyro_error_adjustment):
    global error_multiplier
    global momentum_multiplier
    global drive
    global stop
    global is_init
    wait_for_button("Press button to calibrate gyro. DO NOT MOVE ROBOT!")
    msleep(500)
    calibrate_gyro()
    msleep(500)
    drive = drive_function
    stop = stop_function
    error_multiplier = gyro_error_adjustment
    momentum_multiplier = momentum_adjustment
    is_init = True


def gyro_turn_test(left_speed, right_speed, angle=90, iterations=4):
    for x in range(iterations):
        gyro_turn(left_speed, right_speed, angle)
        msleep(1000)
