from kipr import push_button, msleep, analog, console_clear

START_LIGHT_THRESHOLD = 0


def _calibrate(port):
    global START_LIGHT_THRESHOLD
    print("Press button with light on")
    while not push_button():
        light_on = analog(port)
        console_clear()
        print("On value =", light_on)
        msleep(100)
    while push_button():
        pass

    if light_on > 200:
        print("Bad calibration")
        return False
    msleep(1000)
    print("Press button with light off")
    while not push_button():
        console_clear()
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


def _wait_4(port):
    i = 10
    print("waiting for light!!", i)
    while i > 0:
        if analog(port) < START_LIGHT_THRESHOLD:
            i = i - 1
            print("Countdown:", i)
        else:
            i = 10
        msleep(10)


def wait_4_light(port, ignore=False):
    if ignore:
        wait_for_button()
        return
    while not _calibrate(port):
        pass
    _wait_4(port)


def wait_for_button():
    print('waiting for button')
    while not push_button():
        pass
    while push_button():
        pass
