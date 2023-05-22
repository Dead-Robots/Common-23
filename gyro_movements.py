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
error_proportion = 1.0
error_integral_multiplier = 1.0


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


def gyro_init(drive_function, stop_function, momentum_adjustment=0, gyro_error_adjustment=0.95,
              drive_straight_error_proportion=0.1, drive_straight_integral_multiplier=0):
    global error_multiplier
    global momentum_multiplier
    global drive
    global stop
    global is_init
    global error_proportion
    global error_integral_multiplier
    wait_for_button("Press button to calibrate gyro. DO NOT MOVE ROBOT!")
    msleep(500)
    calibrate_gyro()
    msleep(500)
    drive = drive_function
    stop = stop_function
    error_multiplier = gyro_error_adjustment
    momentum_multiplier = momentum_adjustment
    is_init = True
    error_proportion = drive_straight_error_proportion
    error_integral_multiplier = drive_straight_integral_multiplier


def gyro_turn_test(left_speed, right_speed, angle=90, iterations=1):
    for x in range(iterations):
        gyro_turn(left_speed, right_speed, angle)
        msleep(1000)


def straight_drive(speed, condition):
    speed = int(round(speed*0.95, 0))
    drive(speed, speed)
    start_time = time.time()
    previous_time = start_time
    integral_error_adjustment = 0.0
    while condition():
        current_gyro = gyroscope()
        current_time = time.time()
        marginal_time = current_time - previous_time
        gyro_error_adjustment = error_proportion * current_gyro
        integral_error_adjustment += error_integral_multiplier * current_gyro * marginal_time
        drive(speed, speed + gyro_error_adjustment + integral_error_adjustment)
        msleep(10)
    stop()
