"""Core logic of the antiSMASH metrics service"""
from datetime import datetime
from prometheus_client import Gauge

BACT_QUEUE_LENGTH = Gauge('bacterial_queue_length', 'Length of the regular bacterial jobs queue')
BACT_FAST_QUEUE_LENGTH = Gauge('bacterial_fast_queue_length', 'Length of the bacterial fast jobs queue')
BACT_OLDEST_JOB = Gauge('bacterial_oldest_job_age', 'Age of oldest regular bacterial job, in seconds since epoch')

def gather_metrics(db):
    """Gather metrics from the redis connection

    :param db: Redis connection to use
    """
    BACT_QUEUE_LENGTH.set(db.llen('jobs:queued'))
    BACT_FAST_QUEUE_LENGTH.set(db.llen('jobs:minimal'))
    BACT_OLDEST_JOB.set(get_oldest_job_ts(db))

def get_oldest_job_ts(db):
    """Get the unix timestamp of the oldest job

    :param db: Redis connection to use
    :return: Seconds since epoch that the oldest job was started at
    """
    queue = db.lrange('jobs:queued', 0, 0)
    if not queue:
        return 0

    # TODO: decode just needed for the tests :(
    job_id = queue[0].decode('utf-8')
    job_key = 'job:{}'.format(job_id)

    added_str = db.hget(job_key, 'added')

    if not added_str:
        return 0

    # TODO: decode just needed for the tests :(
    dt = datetime.strptime(added_str.decode('utf-8'), "%Y-%m-%d %H:%M:%S.%f")
    return dt.timestamp()

