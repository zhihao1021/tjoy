import os
import aio_pika
import json

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
RABBITMQ_QUEUE_NAME = os.getenv("QUEUE_NAME", "matchmaking-queue")


async def send_message(message: dict):
    try:
        connection = await aio_pika.connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()

            await channel.declare_queue(RABBITMQ_QUEUE_NAME, durable=True)

            body = json.dumps(message).encode("utf-8")
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=RABBITMQ_QUEUE_NAME,
            )

            print(f"[Sender] Sent message to queue '{RABBITMQ_QUEUE_NAME}': {body}")

    except Exception as e:
        print(f"[Sender][Error]: Failed to send message: {e}")