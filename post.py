import os
from time import sleep
from kipr import a_button, b_button, c_button, push_button


def msleep(milliseconds):
    sleep(milliseconds/1000)


def post_core(
        test_servos,
        test_motors,
        test_sensors,
        initial_setup=None,
        calibration_function=None
):
    """
    This function contains the core logic for the power on self test
    :param test_servos: A function to test the servos
    :param test_motors: A function to test the motors
    :param test_sensors: A function to test the sensors
    :param initial_setup: An optional function to run one-time initial setup
    :param calibration_function: An optional function to calibrate the robot
    """
    if initial_setup:
        print("Running initial setup.")
        initial_setup()
        print("Initial setup complete.")
    msleep(1500)

    while not push_button():

        print("Press 'A' to run the robot.\nPress 'B' to re-run the POST\nPress 'C' to calibrate drive distances.")
        a, b, c = a_button(), b_button(), c_button()
        while not (a or b or c or push_button()):
            a, b, c = a_button(), b_button(), c_button()
        while a_button() or b_button() or c_button():
            pass
        if a:
            break
        elif b:
            try:
                # Reads the straight_drive_distance_proportion from straight.txt if straight.txt exists.
                with open(os.path.expanduser("~/straight.txt"), "r") as straight_file:
                    print("Testing servos.")
                    test_servos()
                    print("Testing motors.")
                    test_motors()
                    print("Testing sensors.")
                    test_sensors()
                    print("POST complete.")
            except FileNotFoundError:
                print("Aborting POST, straight.txt was not found.")
        elif c:
            if calibration_function:
                calibration_function()
            else:
                raise Exception("No calibration function provided.")
    msleep(500)
