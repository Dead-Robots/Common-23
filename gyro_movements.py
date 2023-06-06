import time
import os
from math import copysign

from common import ROBOT
from kipr import msleep, gyro_z
from typing import Optional, Callable, Tuple
from utilities import wait_for_button

error_multiplier = 1.0
momentum_multiplier = 1.0
gyro_offset = 0.0
drive: Optional[Callable[[int, int], None]] = None
stop: Optional[Callable[[], None]] = None
is_init = False
error_proportion = 1.0
error_integral_multiplier = 1.0
get_motor_positions: Optional[Callable[[], Tuple[int, int]]] = None
push_sensor: Optional[Callable[[], bool]] = None
distance_adjustment = 0.0


def calibrate_gyro():
    total = 0
    for x in range(50):
        total = total + gyro_z()
        msleep(10)
    global gyro_offset
    gyro_offset = total / 50


def gyroscope():
    return gyro_z() - gyro_offset


def gyro_turn(left_speed, right_speed, angle, stop_when_finished=True):
    check_init()
    old_time = time.time()
    drive(left_speed, right_speed)
    current_turned_angle = 0
    fixed_angle = abs(angle)-abs(right_speed-left_speed) * momentum_multiplier
    while abs(current_turned_angle) < fixed_angle:
        current_turned_angle += error_multiplier * gyroscope() * (time.time() - old_time) / 8
        old_time = time.time()
        msleep(10)
    if stop_when_finished:
        stop()
        msleep(500)


def check_init():
    if not is_init:
        print("GYRO NOT INITIALIZED!")
        exit(0)


def gyro_init(drive_function, stop_function, get_motor_positions_function, push_sensor_function,
              gyro_turn_momentum_adjustment=0.0, gyro_turn_error_adjustment=1.0,
              straight_drive_error_proportion=0.13, straight_drive_integral_multiplier=0.005,
              straight_drive_distance_momentum_adjustment=0.0):
    global error_multiplier
    global momentum_multiplier
    global drive
    global stop
    global is_init
    global error_proportion
    global error_integral_multiplier
    global get_motor_positions
    global push_sensor
    global distance_adjustment
    wait_for_button("Press button to calibrate gyro. DO NOT MOVE ROBOT!")
    msleep(500)
    calibrate_gyro()
    msleep(500)
    drive = drive_function
    stop = stop_function
    error_multiplier = gyro_turn_error_adjustment
    momentum_multiplier = gyro_turn_momentum_adjustment
    is_init = True
    error_proportion = straight_drive_error_proportion
    error_integral_multiplier = straight_drive_integral_multiplier
    get_motor_positions = get_motor_positions_function
    push_sensor = push_sensor_function
    distance_adjustment = straight_drive_distance_momentum_adjustment


def gyro_turn_test(left_speed, right_speed, angle=90, iterations=1):
    for x in range(iterations):
        gyro_turn(left_speed, right_speed, angle)
        msleep(1000)


def straight_drive(speed, condition, stop_when_finished=True):
    check_init()
    if abs(speed) < 20:
        speed = 20 if speed > 0 else -20
        print("Warning, speed is too slow, defaulting to 20.")
    previous_time = time.time()
    integral_error_adjustment = 0.0
    while condition():

        # Calculate adjustment values
        current_gyro = gyroscope()
        current_time = time.time()
        marginal_time = current_time - previous_time
        previous_time = current_time
        gyro_error_adjustment = error_proportion * current_gyro
        integral_error_adjustment += error_integral_multiplier * current_gyro * marginal_time

        # Calculate new speeds
        left_speed = right_speed = speed
        if abs(speed + gyro_error_adjustment + integral_error_adjustment) <= 100:
            right_speed = speed + gyro_error_adjustment + integral_error_adjustment
        else:
            left_speed = speed - gyro_error_adjustment - integral_error_adjustment

        # Make sure speeds are not too small
        if abs(right_speed) < 5:
            right_speed = speed
        if abs(left_speed) < 5:
            left_speed = speed

        # Drive
        drive(left_speed, right_speed)
        msleep(10)
    if stop_when_finished:
        stop()
        msleep(500)


def calibrate_straight_drive_distance(robot_length_inches, direction=1, speed=80, total_inches=94):
    start_position = sum(get_motor_positions())

    def condition():
        return not push_sensor()

    straight_drive(int(copysign(speed, direction)), condition)
    with open(os.path.expanduser("~/straight.txt"), "w+") as file:
        file.write(
            str(abs((sum(get_motor_positions()) - start_position)
                / (total_inches - robot_length_inches))))
    msleep(500)
    with open(os.path.expanduser("~/straight.txt")) as file:
        proportion = file.read()
    print(f"Straight drive distance calibrated. {proportion} ticks per inch.")
    wait_for_button("Press button to drive halfway back")
    straight_drive_distance(-1*copysign(speed, direction), (total_inches-robot_length_inches)/2)
    exit(0)


def straight_drive_distance(speed, inches, stop_when_finished=True):
    start_position = sum(get_motor_positions())
    global distance_adjustment

    def condition():
        left, right = get_motor_positions()
        return abs(left + right - start_position) \
            < (abs(inches) - abs(distance_adjustment * (speed / 100.0))) * straight_drive_distance_proportion

    straight_drive(speed, condition, stop_when_finished)


def gyro_demo():
    # pivot
    # gyro_turn_test(0, 100, 90, 1)
    # wait_for_button('waiting for button')
    # # both wheels
    # gyro_turn_test(-100, 100, 90, 1)
    # wait_for_button('waiting for button')
    # 180 turns
    # pivot
    gyro_turn_test(25, -25, 90, 4)
    wait_for_button("waiting for button")
    gyro_turn_test(-25, 25, 90, 4)


try:
    with open(os.path.expanduser("~/straight.txt"), "r") as straight_file:
        straight_drive_distance_proportion = float(straight_file.read())
except FileNotFoundError:
    print("Warning, straight drive distance not calibrated")
