import time

from app.services.event_worker import process_pending_events
from app.services.delivery_worker import process_queued_deliveries
from app.services.reconciliation import reconcile_deliveries


POLL_INTERVAL = 1


def run_worker():

    print("LinkPlease worker started")

    while True:

        try:
            process_pending_events()

            process_queued_deliveries()

            reconcile_deliveries()

        except Exception as exc:
            print(
                f"Worker error: {exc}"
            )

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    run_worker()