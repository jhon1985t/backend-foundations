import json

from confluent_kafka import Producer


_producer: Producer | None = None


def delivery_report(err, msg):
    """Called once for each message produced to indicate delivery result.
    Triggered by poll() or flush()."""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(
            f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}"
        )


def get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer({"bootstrap.servers": "localhost:9093"})
    return _producer


def emit_user_created(user_id: str, email: str):
    """Send a 'user_created' event to the Kafka topic."""
    event = {"event_type": "UserCreated", "user_id": user_id, "email": email}

    p = get_producer()
    p.produce(
        topic="user-events",
        key=str(user_id),
        value=json.dumps(event),
        callback=delivery_report,
    )
    # Flush to ensure delivery when called from request handlers
    p.poll(0)
    p.flush(5)
