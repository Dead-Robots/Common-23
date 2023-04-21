from kipr import push_button, msleep, analog

START_LIGHT_THRESHOLD = 0


def _calibrate(port):
    global START_LIGHT_THRESHOLD
    print("Press button with light on")
    while not push_button():
        pass
    while push_button():
        pass
    light_on = analog(port)
    print("On value =", light_on)
    if light_on > 200:
        print("Bad calibration")
        return False
    msleep(1000)
    print("Press button with light off")
    while not push_button():
        pass
    while push_button():
        pass
    light_off = analog(port)
    print("Off value =", light_off)
    if light_off < 3000:
        print("Bad calibration")
        return False

    if (light_off - light_on) < 2000:
        print("Bad calibration")
        return False
    START_LIGHT_THRESHOLD = (light_off - light_on) / 2
    print("Good calibration! ", START_LIGHT_THRESHOLD)
    return True


def _wait_4(port):
    print("waiting for light!! ")
    while analog(port) > START_LIGHT_THRESHOLD:
        pass


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
