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
    """
        Measures and saves the gyro offset value
    """
    total = 0
    for x in range(50):
        total = total + gyro_z()
        msleep(10)
    global gyro_offset
    gyro_offset = total / 50


def gyroscope():
    """
        Returns the adjusted gyro value
    """
    return gyro_z() - gyro_offset


def gyro_turn(left_speed, right_speed, angle, stop_when_finished=True):
    """
        Drives with the motor speed parameters until the robot has turned angle degrees


        :param left_speed: Speed of the left motor. Accepts integers in the range from -100 to 100,
        inclusive.

        :param right_speed: Speed of the right motor. Accepts integers in the range from -100 to 100,
        inclusive.

        :param angle: The amount of degrees to be turned. Accepts any integers or floats, but sign does not matter.

        :param stop_when_finished: Determines if the robot should stop when it finishes turning. Defaults to True.
    """
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
    """
        Prints "GYRO NOT INITIALIZED!" and exits the program if the gyro has not been initialized.
        gyro_init() must be run to avoid this error.
    """
    if not is_init:
        print("GYRO NOT INITIALIZED!")
        exit(0)


def gyro_init(drive_function, stop_function, get_motor_positions_function, push_sensor_function,
              gyro_turn_error_adjustment=1.0, gyro_turn_momentum_adjustment=0.0,
              straight_drive_error_adjustment=0.13, straight_drive_integral_adjustment=0.3,
              straight_drive_distance_momentum_adjustment=0.0):
    """
        Calibrates the gyroscope and sets the values of various constants that are used for gyro turns and straight
        drives.
        This function must have been called before any gyro turns or straight drives are performed.


        :param drive_function: A function that drives the robot. It takes the left motor speed and right motor speed as
            parameters.

        :param stop_function: A function that stops the robot. It takes no parameters.

        :param get_motor_positions_function: A function that returns a tuple of the left and right motor position. It
            takes no parameters.

        :param push_sensor_function: A function that returns true if the push sensor of the robot is being pressed. It
            takes no parameters.

        :param gyro_turn_error_adjustment: Used in gyro turns to inversely scale the angle that the robot is trying to
            turn to account for regular error in the gyroscope. To calibrate, have the robot execute slow gyro turns.
            If the robot turns too far, decrease the value, and if the robot does not turn enough, increase the value.

        :param gyro_turn_momentum_adjustment: Used in gyro turns to reduce the angle that the robot is trying to turn
            in order to account for momentum. The effect of this value scales with speed, so it has almost no effect on
            slower turns. To calibrate, make sure the gyro_turn_error_adjustment parameter is calibrated and then have
            the robot turn at high speeds. If the robot overturns at high speeds, increase the value, and if the robot
            doesn't turn enough at high speeds, decrease the value. If this value is significantly changed, check that
            the turns are still accurate at lower speeds. If they are not accurate at lower speeds, recalibrate the
            gyro_turn_error_adjustment.

        :param straight_drive_error_adjustment: Used in straight drives to adjust the amount that the robot corrects
            its motor speeds based on the current gyroscope value. To calibrate, set the
            straight_drive_integral_multiplier to zero and set it to the lowest point at which increasing it makes no
            noteworthy difference. Setting it too high will make the drives shaky. The robot will arc while calibrating
            this, but that will be fixed when the straight_drive_integral_multiplier is changed back from zero to its
            previous value.

        :param straight_drive_integral_adjustment: Used in straight drives to adjust how much the robot corrects its
            motor speeds based on the amount that it has turned so far throughout the drive so far. Increase this value
            if the robot is not driving adequately straight, but setting it too high will cause the drive to become
            shaky.

        :param straight_drive_distance_momentum_adjustment: Used for distance straight drives to reduce the distance
            that the robot tries to drive based on how fast it's moving. If the robot is driving the correct distances
            at low speeds and driving too far at high speeds, increase this value to fix the problem. Setting this value
            too high will cause the robot to undershoot its drive distances at high speeds.
    """
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
    error_proportion = straight_drive_error_adjustment
    error_integral_multiplier = straight_drive_integral_adjustment
    get_motor_positions = get_motor_positions_function
    push_sensor = push_sensor_function
    distance_adjustment = straight_drive_distance_momentum_adjustment


def gyro_turn_test(left_speed, right_speed, angle=90, iterations=1):
    """
        Executes a given number of gyro turns with set motor speeds and angles. There is a one-second pause between each
        turn.


        :param left_speed: Speed of the left motor. Accepts integers in the range 0-100, inclusive.

        :param right_speed: Speed of the right motor. Accepts integers in the range 0-100, inclusive.

        :param angle: The amount of degrees to be turned. Accepts any integers or floats, but sign does not matter.

        :param iterations: The number of gyro turns to be performed.
    """
    for x in range(iterations):
        gyro_turn(left_speed, right_speed, angle)
        msleep(1000)


def straight_drive(speed, condition, stop_when_finished=True):
    """
    Drives straight at a given speed while an input condition is True.


    :param speed: The speed at which the robot should be driving. Accepts integers in the range from -100 to 100,
        inclusive.

    :param condition: A function that returns a boolean value. The robot will continue driving until the function
        returns false.

    :param stop_when_finished: Determines if the robot should stop when it finishes driving. Defaults to True.
    """
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
    """
        Straight drives and records the number of motor ticks that have passed until the push sensor is pressed.


        :param robot_length_inches: The distance from the end of the push sensor (while it is being pressed) to the
            opposite end of the robot.

        :param direction: The direction for the robot to drive. Set to 1 to calibrate lego and -1 to calibrate create.
            Defaults to 1.

        :param speed: The speed at which the robot should drive during calibration.

        :param total_inches: The distance in inches being used to calibrate the drive distance. Defaults to the 94, the
            full length of the game board.
    """
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
    """
        Drives straight at a given speed for a given distance.


        :param speed: The speed at which the robot should be driving. Accepts integers in the range from -100 to 100,
            inclusive.

        :param inches: The number of inches for the robot to drive.

        :param stop_when_finished: Determines if the robot should stop when it finishes driving. Defaults to True.
    """
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
    # Reads the straight_drive_distance_proportion from straight.txt if straight.txt exists.
    with open(os.path.expanduser("~/straight.txt"), "r") as straight_file:
        straight_drive_distance_proportion = float(straight_file.read())
except FileNotFoundError:
    # Prints a warning if straight.txt is not found. If this happens, run calibrate_straight_drive_distance().
    print("Warning, straight drive distance not calibrated")
