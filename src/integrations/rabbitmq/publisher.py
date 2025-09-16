import json
from datetime import datetime

import pika

from auth.schemas import ResetPasswordMessageSchema
from core.config import settings


def publish_message(
    queue: str,
    exchange: str,
    routing_key: str,
    message: ResetPasswordMessageSchema,
):
    url = settings.rabbitmq.url
    params = pika.URLParameters(url)
    dlq_name = "reset-password-queue-dlq"
    dlx_name = "reset-password-queue-dlx"

    try:
        with pika.BlockingConnection(params) as connection:
            with connection.channel() as channel:
                arguments = {
                    "x-dead-letter-exchange": dlx_name,
                    "x-dead-letter-routing-key": dlq_name,
                    "x-message-ttl": 60000,
                    "x-max-length": 10000,
                }
                channel.queue_declare(queue=queue, arguments=arguments, durable=True)

                channel.exchange_declare(
                    exchange=exchange,
                    exchange_type="direct",
                )
                channel.queue_bind(
                    queue=queue,
                    exchange=exchange,
                    routing_key=routing_key,
                )

                message.sent_at = datetime.utcnow()
                message_json = message.model_dump_json()

                properties = pika.BasicProperties(headers={"x-retry-count": 0})

                channel.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=message_json,
                    properties=properties,
                )
                print(f"Message sent to queue: {queue}")

    except pika.exceptions.AMQPConnectionError:
        print(f"Failed to connect to RabbitMQ.")
    except pika.exceptions.AMQPChannelError:
        print(f"Channel error in RabbitMQ.")
