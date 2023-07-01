import time
from threading import Thread
from kipr import get_motor_position_counter, motor_power, freeze


class Multitasker:
    def __init__(self):
        self.threads = []
        # set up the storage for threads

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for thread in self.threads:
            thread.join()

    def do(self, function, args=None):
        # create a mew thread, store it, and start it
        thread = Thread(target=function, args=args or (), daemon=True)
        self.threads.append(thread)
        thread.start()
        return thread


class MultitaskedMotor:
    def __init__(self, port, position):
        self.port = port
        self.position = position
        self.running = True
        self.thread = Thread(target=self._move_motors, daemon=True)
        self.thread.start()

    def _move_motors(self):
        while self.running:
            current = get_motor_position_counter(self.port)

            motor_power(self.port, max(min(int(100 * (self.position - current) / 300), 100), -100))
            time.sleep(0.1)
        freeze(self.port)
