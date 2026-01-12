import json
from typing import Optional

from confluent_kafka import Producer

from app.settings import settings


_producer: Optional[Producer] = None


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
        _producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})
    return _producer


def emit_user_created(user_id: str, email: str):
    """Send a 'user_created' event to the Kafka topic. Best-effort when enabled."""
    if not settings.kafka_enabled:
        return

    event = {"event_type": "UserCreated", "user_id": user_id, "email": email}

    try:
        p = get_producer()
        p.produce(
            topic=settings.kafka_topic_user_events,
            key=str(user_id),
            value=json.dumps(event),
            callback=delivery_report,
        )
        # Flush to ensure delivery when called from request handlers
        p.poll(0)
        p.flush(5)
    except Exception as e:  # noqa: BLE001 - guard external dependency errors
        # Degrade gracefully when Kafka is unavailable
        print(f"Kafka emit skipped or failed: {e}")
