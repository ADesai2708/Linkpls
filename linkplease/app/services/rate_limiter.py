import time
from collections import deque


class RateLimiter:

    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 60
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_times = deque()

    def wait_if_needed(self):
        while True:

            now = time.monotonic()

            # Remove requests that are outside
            # the rolling 60-second window.
            while (
                self.request_times
                and now - self.request_times[0]
                >= self.window_seconds
            ):
                self.request_times.popleft()

            # We still have capacity.
            if len(self.request_times) < self.max_requests:
                self.request_times.append(now)
                return

            # We are at the rate limit.
            sleep_time = (
                self.window_seconds
                - (now - self.request_times[0])
            )

            time.sleep(max(sleep_time, 0))