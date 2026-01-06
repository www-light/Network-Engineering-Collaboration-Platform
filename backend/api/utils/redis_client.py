import json
from django.conf import settings
import redis


# Shared Redis client for publish/subscribe
redis_client = redis.Redis.from_url(
    getattr(settings, "REDIS_URL", "redis://localhost:6379/0"),
    decode_responses=True,
)


def publish_message(conversation_id: int, payload: dict) -> None:
    """Publish a message payload to a conversation channel."""
    channel = f"conversation:{conversation_id}"
    redis_client.publish(channel, json.dumps(payload, ensure_ascii=False))


def get_pubsub():
    """Get a pubsub instance; caller is responsible for closing it."""
    return redis_client.pubsub(ignore_subscribe_messages=True)
