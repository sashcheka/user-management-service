import json

import pika

from core.config import settings


def get_single_message(queue):
    url = settings.rabbitmq.url
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    dlq_name = "reset-password-queue-dlq"
    dlx_name = "reset-password-queue-dlx"
    arguments = {
        "x-dead-letter-exchange": dlx_name,
        "x-dead-letter-routing-key": dlq_name,
        "x-message-ttl": 60000,
        "x-max-length": 10000,
    }
    channel.queue_declare(queue=queue, arguments=arguments, durable=True)
    method_frame, header_frame, body = channel.basic_get(
        queue=queue,
        auto_ack=True,
    )

    connection.close()

    if method_frame:
        message = json.loads(body)
        return message
    else:
        return None
