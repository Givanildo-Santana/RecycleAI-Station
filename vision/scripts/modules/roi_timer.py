import time

class RoiTimer:
    def __init__(self):
        self.current = None
        self.start_time = None
        self.confirmed = None

    def update(self, label):
        if label != self.current:
            self.current = label
            self.start_time = time.time()
            self.confirmed = None

        elif time.time() - self.start_time >= 3 and self.confirmed is None:
            self.confirmed = self.current
            return self.confirmed

        return None
