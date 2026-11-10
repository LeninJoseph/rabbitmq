"""FastAPI = PRODUCER. It puts messages on a RabbitMQ queue; worker.py consumes them."""
import json
from contextlib import asynccontextmanager

import aio_pika
from fastapi import FastAPI
from pydantic import BaseModel

RABBIT_URL = "amqp://guest:guest@localhost:5672/"
QUEUE = "tasks"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # One connection + channel for the whole app lifetime.
    app.state.conn = await aio_pika.connect_robust(RABBIT_URL)
    app.state.channel = await app.state.conn.channel()
    # durable=True: queue survives a broker restart.
    await app.state.channel.declare_queue(QUEUE, durable=True)
    yield
    await app.state.conn.close()


app = FastAPI(lifespan=lifespan)


class Task(BaseModel):
    message: str


@app.post("/publish")
async def publish(task: Task):
    body = json.dumps(task.model_dump()).encode()
    # Default exchange ("") routes straight to the queue named by routing_key.
    await app.state.channel.default_exchange.publish(
        aio_pika.Message(body=body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
        routing_key=QUEUE,
    )
    return {"status": "queued", "message": task.message}


@app.get("/queue-size")
async def queue_size():
    # passive=True: only inspect the existing queue, don't create/modify it.
    queue = await app.state.channel.declare_queue(QUEUE, durable=True, passive=True)
    return {
        "queue": QUEUE,
        "messages_waiting": queue.declaration_result.message_count,
        "consumers": queue.declaration_result.consumer_count,
    }
