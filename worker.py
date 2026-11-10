"""WORKER = CONSUMER. Run separately: python worker.py"""
import asyncio
import json

import aio_pika

RABBIT_URL = "amqp://guest:guest@localhost:5672/"
QUEUE = "tasks"


async def main():
    conn = await aio_pika.connect_robust(RABBIT_URL)
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=1)  # one unacked message at a time
    queue = await channel.declare_queue(QUEUE, durable=True)

    print("Waiting for messages. Ctrl+C to stop.")
    async with queue.iterator() as it:
        async for msg in it:
            # process() acks on success; on exception the message is rejected/requeued.
            async with msg.process():
                data = json.loads(msg.body)
                print("Got:", data)
                await asyncio.sleep(2)  # pretend to do slow work
                print("Done:", data["message"])


if __name__ == "__main__":
    asyncio.run(main())
