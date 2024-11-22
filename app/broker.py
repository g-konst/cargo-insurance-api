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
        self.producer = AIOKafkaProducer(
            bootstrap_servers=broker_url,
            linger_ms=linger_ms,
            max_batch_size=max_batch_size,
        )
        self.base_topic = base_topic
        self.queue = asyncio.Queue()
        self.running = False

    async def connect(self):
        await self.producer.start()
        self.running = True
        asyncio.create_task(self._batch_worker())

    async def dispose(self):
        self.running = False
        await self.producer.stop()

    async def publish(self, message: KafkaMessage) -> None:
        await self.queue.put(message.model_dump_json())

    async def _batch_worker(self):
        while self.running:
            messages = []
            try:
                while len(messages) < 100:
                    message = await asyncio.wait_for(
                        self.queue.get(), timeout=0.1
                    )
                    messages.append(message)
            except asyncio.TimeoutError:
                pass

            if messages:
                await asyncio.gather(
                    *[
                        self.producer.send_and_wait(
                            self.base_topic, msg.encode("utf-8")
                        )
                        for msg in messages
                    ]
                )


app_broker = AppBroker(
    broker_url=settings.kafka.url,
    base_topic=settings.kafka.topic,
    linger_ms=settings.kafka.linger_ms,
    max_batch_size=settings.kafka.max_batch_size,
)
