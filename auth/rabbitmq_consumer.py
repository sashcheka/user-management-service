import json

import pika

from core.config import settings


def get_single_message(queue):
    url = settings.rabbitmq.CLOUDAMQP_URL
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue=queue)
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
