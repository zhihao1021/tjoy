import os
import sys
import asyncio
import aio_pika
import json


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from embedding_service.routes.embedding import get_recommended_users_for_event

RESET = "\033[0m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"


print(f"{BLUE}[Initialization]{RESET}: Loading recommendation system model...")
try:
    from embedding_service.src import activity_recommender
    if not activity_recommender.model:
        activity_recommender.load_model()
    print(f"{GREEN}[Initialization]{RESET}: Model loaded successfully")
except Exception as e:
    print(f"{RED}[Initialization Error]{RESET}: Failed to load model: {e}")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
RABBITMQ_QUEUE_NAME = os.getenv("QUEUE_NAME", "matchmaking-queue")

async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            event_id = payload.get("event_id")
            print(f"{GREEN}[Log]{RESET}: Get event id: {event_id}")

            if not event_id:
                print(f"{RED}[Error]{RESET}: Not a event id")
                return

            print(f"{YELLOW}[Processing]{RESET}: Starting recommendation calculation...")
            result = await get_recommended_users_for_event(int(event_id))
            print(result)
            print(f"{GREEN}[Success]{RESET}: Recommendation calculation completed")
            print(f"{CYAN}[Result]{RESET}: Found {result.get('total_recommended_users', 0)} recommended users")
            print(f"{CYAN}[Result]{RESET}: Event: {result.get('event_title', 'N/A')}")

        except Exception as e:
            print(f"{RED}[Error]{RESET}: Processing error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=1)
    
    queue = await channel.declare_queue(
        RABBITMQ_QUEUE_NAME,
        durable=True
    )

    for i in range(3):
        await queue.consume(lambda msg, n=i: on_message_wrapper(msg, n))

    print(f"{BLUE}[Log]{RESET}: Listening with 3 consumers on queue '{RABBITMQ_QUEUE_NAME}' ...")
    return connection

async def on_message_wrapper(message: aio_pika.IncomingMessage, n):
    print(f"Worker {n} got message")
    await on_message(message)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.run_forever()