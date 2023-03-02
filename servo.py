from constants.servos import BackClaw
from kipr import msleep, set_servo_position, get_servo_position, disable_servo, \
    enable_servo


def move_servo(new_position, step_time=10):
    servo = new_position.port
    temp = get_servo_position(servo)

    if temp < new_position:
        while temp < new_position:
            set_servo_position(servo, temp)
            temp += 5
            msleep(step_time)
    else:
        while temp > new_position:
            set_servo_position(servo, temp)
            temp -= 5
            msleep(step_time)
