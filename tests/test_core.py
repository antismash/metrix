"""Unit tests for the core functions"""

from datetime import datetime
import mockredis
import pytest

from metrix import core

@pytest.fixture
def db():
    return mockredis.mock_redis_client()


def test_get_oldest_job_ts(db):
    expected = datetime.utcnow()
    strtime = expected.strftime('%Y-%m-%d %H:%M:%S.%f')

    db.lpush('jobs:queued', 'fakejob')
    db.hset('job:fakejob', 'added', strtime)

    timestamp = core.get_oldest_job_ts(db)

    assert timestamp == expected.timestamp()
