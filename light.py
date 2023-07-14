from kipr import push_button, msleep, console_clear, analog
from time import time

START_LIGHT_THRESHOLD = 0
USE_BUTTON_INSTEAD = False


def _calibrate(port):
    global START_LIGHT_THRESHOLD
    light_on = 0
    while not push_button():
        light_on = analog(port)
        console_clear()
        print("Press button with light on")
        print("On value =", light_on)
        msleep(100)
    while push_button():
        pass

    if light_on > 400:
        print("Bad calibration")
        return False
    msleep(1000)
    light_off = 3000
    while not push_button():
        console_clear()
        print("Press button with light off")
        print("On value =", light_on)
        light_off = analog(port)
        print("Off value =", light_off)
        msleep(100)
    while push_button():
        pass

    if light_off < 1400:
        print("Bad calibration")
        return False

    if (light_off - light_on) < 900:
        print("Bad calibration")
        return False
    START_LIGHT_THRESHOLD = (light_off - light_on) / 2
    print("Good calibration! ", START_LIGHT_THRESHOLD)
    return True


def _wait_4(port, function=None, function_every=None):
    i = 10
    end_time = 0
    print("waiting for light!!", i)
    while i > 0:
        if analog(port) < START_LIGHT_THRESHOLD or (push_button() and USE_BUTTON_INSTEAD):
            i = i - 1
            print("Countdown:", i)
        else:
            i = 10
        if function and function_every and time() - end_time > function_every and i == 10:
            function()
            end_time = time()
        else:
            msleep(10)


def wait_4_light(port, ignore=False, function=None, function_every=None):
    if ignore:
        wait_for_button()
        return
    if not USE_BUTTON_INSTEAD:
        while not _calibrate(port):
            pass
    _wait_4(port, function=function, function_every=function_every)


def wait_for_button():
    print('waiting for button')
    while not push_button():
        pass
    while push_button():
        pass
