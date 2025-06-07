import pika
import json
from api.config import get_settings

settings = get_settings()

def publish_event(payload: dict, routing_key: str = None):
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.rabbitmq_host)
        )
        channel = connection.channel()

        channel.exchange_declare(
            exchange=settings.rabbitmq_exchange,
            exchange_type=settings.rabbitmq_exchange_type,
            durable=True,
            auto_delete=False
        )

        channel.basic_publish(
            exchange=settings.rabbitmq_exchange,
            routing_key=routing_key or settings.rabbitmq_routing_key,
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

    except Exception as e:
        print(f"[RabbitMQ] Failed to publish event: {e}")
