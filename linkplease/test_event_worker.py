from app.services.event_worker import process_pending_events


if __name__ == "__main__":
    process_pending_events()