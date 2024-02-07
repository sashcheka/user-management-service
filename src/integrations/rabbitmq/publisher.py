import json

import pika

from core.config import settings


def publish_message(
    queue: str,
    exchange: str,
    routing_key: str,
    message: dict,
):
    url = settings.rabbitmq.url
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=queue)
    channel.exchange_declare(exchange=exchange)
    channel.queue_bind(
        queue=queue,
        exchange=exchange,
        routing_key=routing_key,
    )

    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(message).encode(),
    )
    print("Message sent to queue:", queue)

    channel.close()
    connection.close()
