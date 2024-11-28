import asyncio
from datetime import datetime

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel, Field

from app.config import settings


class KafkaMessage(BaseModel):
    user_id: str | None = None
    action: str
    timestamp: datetime = Field(..., default_factory=datetime.now)


class AppBroker:
    def __init__(
        self,
        broker_url: str,
        base_topic: str,
        linger_ms: int = 0,
        max_batch_size: int = 16384,
    ) -> None:
        self.producer = None
        self.broker_url = broker_url
        self.linger_ms = linger_ms
        self.max_batch_size = max_batch_size

        self.base_topic = base_topic
        self.queue = asyncio.Queue()
        self.running = False

    async def connect(self):
        if self.producer is None:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.broker_url,
                linger_ms=self.linger_ms,
                max_batch_size=self.max_batch_size,
            )

        await self.producer.start()
        self.running = True
        asyncio.create_task(self._batch_worker())

    async def dispose(self):
        self.running = False
        if self.producer:
            await self.producer.stop()

    async def publish(self, message: KafkaMessage) -> None:
        await self.queue.put(message.model_dump_json())

    async def _batch_worker(self):
        while self.running:
            messages = await self._collect_messages(
                batch_size=100, timeout=0.1
            )

            if messages:
                await self._send_messages(messages)

    async def _collect_messages(
        self, batch_size: int, timeout: float
    ) -> list[str]:
        messages = []
        try:
            while len(messages) < batch_size:
                message = await asyncio.wait_for(
                    self.queue.get(), timeout=timeout
                )
                messages.append(message)
        except asyncio.TimeoutError:
            pass
        return messages

    async def _send_messages(self, messages: list[str]) -> None:
        tasks = [
            self.producer.send_and_wait(self.base_topic, msg.encode("utf-8"))
            for msg in messages
        ]
        await asyncio.gather(*tasks)


app_broker = AppBroker(
    broker_url=settings.kafka.url,
    base_topic=settings.kafka.topic,
    linger_ms=settings.kafka.linger_ms,
    max_batch_size=settings.kafka.max_batch_size,
)
