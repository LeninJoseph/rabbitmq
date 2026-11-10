# Tiny RabbitMQ + FastAPI

```
curl -> FastAPI (producer) -> [ "tasks" queue in RabbitMQ ] -> worker.py (consumer)
```

## Run

```bash
docker compose up -d                       # start RabbitMQ
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload                  # terminal 1: API
python worker.py                           # terminal 2: worker
```

## Try it

```bash
curl -X POST localhost:8000/publish -H 'Content-Type: application/json' -d '{"message":"hello"}'
```

The API returns instantly; the worker prints the message and "works" for 2s.
Send several quickly and watch them get processed one by one.

## Experiments to learn

- Stop the worker, publish 5 messages, open http://localhost:15672 (guest/guest) -> Queues -> `tasks` shows 5 ready. Start the worker; they drain.
- Run two workers: messages are split between them (round-robin).
- Raise an exception inside the worker's `process()` block and see the message requeue.

## Concepts

- **Producer** publishes, **consumer** receives; the **queue** buffers between them.
- **Exchange** routes messages to queues. Here we use the default exchange, which routes by queue name.
- **Ack**: the consumer confirms a message is done; unacked messages are redelivered.
- **durable + persistent**: queue and messages survive a broker restart.
