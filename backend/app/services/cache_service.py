import json
import logging

from pydantic import TypeAdapter, ValidationError
from redis.exceptions import RedisError

from app.redis_client import redis_client
from app.schemas.game import GameResponse

from typing import List

logger = logging.getLogger("rally")

CACHE_TTL_SECONDS = 60
VERSION_KEY = "rally:games:version"

games_adapter = TypeAdapter(List[GameResponse])

def read_games_cache(filters):
    try:
        version = redis_client.get(VERSION_KEY) or "0"

        filter_text = json.dumps(
            filters,
            sort_keys=True,
            separators=(",", ":"),
        )

        key = f"rally:games:v{version}:{filter_text}"

        cached = redis_client.get(key)

    except RedisError:
        logger.warning("games_cache_read_failed")
        return None, None

    if cached is None:
        return key, None

    try:
        games = games_adapter.validate_json(cached)

    except ValidationError:
        logger.warning("games_cache_invalid_data")
        return key, None

    return key, games


def write_games_cache(key, games):
    if key is None:
        return

    payload = games_adapter.dump_json(games)

    try:
        redis_client.set(
            key,
            payload,
            ex=CACHE_TTL_SECONDS,
        )

    except RedisError:
        logger.warning("games_cache_write_failed")


def invalidate_games_cache():
    try:
        redis_client.incr(VERSION_KEY)

    except RedisError:
        logger.warning("games_cache_invalidation_failed")