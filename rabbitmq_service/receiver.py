# This is a Demo for Colten to reference how to receive messages from RabbitMQ

import os
import asyncio
import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
RABBITMQ_QUEUE_NAME = os.getenv("QUEUE_NAME", "matchmaking-queue")

async def on_message(message: aio_pika.IncomingMessage) -> None:
    """
    on_message doesn't necessarily have to be defined as async.
    Here it is to show that it's possible.
    """
    print(" [x] Received message %r" % message)
    print("Message body is: %r" % message.body)

    print("Before sleep!")
    await asyncio.sleep(5)  # Represents async I/O operations
    print("After sleep!")
    
async def main() -> None:
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(RABBITMQ_QUEUE_NAME, durable=True)

        await queue.consume(on_message, no_ack=True)
        await asyncio.sleep(1)
        print(" [*] Waiting for messages. To exit press CTRL+C")
        await asyncio.Future()
    
        
# if __name__ == "__main__":
#     asyncio.run(main())