import json
from confluent_kafka import Consumer, KafkaError


def get_consumer(group_id: str) -> Consumer:
    config = {
        "bootstrap.servers": "localhost:9093",
        "group.id": group_id,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    }
    return Consumer(config)


def run_user_events_consumer():
    consumer = get_consumer(group_id="backend-functions-dev")
    topic = "user-events"
    consumer.subscribe([topic])

    try:
        while True:
            msg = consumer.poll(1.0)  # Timeout of 1 second
            if msg is None:
                continue  # No message received
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
                else:
                    # Error
                    print(f"Error while consuming message: {msg.error()}")
                continue

            # Proper message received
            event = json.loads(msg.value().decode("utf-8"))
            print(f"Received event: {event}")

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    run_user_events_consumer()
