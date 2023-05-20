from threading import Thread


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
        thread = Thread(target=function, args=args, daemon=True)
        self.threads.append(thread)
        thread.start()
        return thread
