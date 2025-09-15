import os
import asyncio
from aio_pika import connect_robust, Message, DeliveryMode

# remember to change localhost to right RabbitMQ host
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
RABBITMQ_QUEUE_NAME = os.getenv("QUEUE_NAME", "matchmaking-queue")

async def send_message_to_rabbitmq(activity_id: str):
    try:
        connection = await connect_robust(RABBITMQ_URL)
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(
                RABBITMQ_QUEUE_NAME,
                durable=True
            )
            await channel.default_exchange.publish(
                Message(
                    body=activity_id.encode(),
                    delivery_mode=DeliveryMode.PERSISTENT
                ),
                routing_key=queue.name
            )
    except Exception as e:
        print(f"Error sending message to RabbitMQ: {e}")
        raise

# if __name__ == "__main__":
#     asyncio.run(send_message_to_rabbitmq("test-activity-id"))
# To run a RabbitMQ server locally for testing, use:
# docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management