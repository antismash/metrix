"""Core logic of the antiSMASH metrics service"""
from datetime import datetime
from prometheus_client import Gauge

BACT_QUEUE_LENGTH = Gauge('bacterial_queue_length', 'Length of the regular bacterial jobs queue')
BACT_FAST_QUEUE_LENGTH = Gauge('bacterial_fast_queue_length', 'Length of the bacterial fast jobs queue')
BACT_OLDEST_JOB = Gauge('bacterial_oldest_job_age', 'Age of oldest regular bacterial job, in seconds since epoch')
BACT_NEWEST_JOB = Gauge('bacterial_newest_job_age', 'Age of newest regular bacterial job, in seconds since epoch')

def gather_metrics(db):
    """Gather metrics from the redis connection

    :param db: Redis connection to use
    """
    BACT_QUEUE_LENGTH.set(db.llen('jobs:queued'))
    BACT_FAST_QUEUE_LENGTH.set(db.llen('jobs:minimal'))
    BACT_OLDEST_JOB.set(get_job_ts(db, -1))
    BACT_NEWEST_JOB.set(get_job_ts(db, 0))

def get_job_ts(db, idx):
    """Get the unix timestamp of the oldest job

    :param db: Redis connection to use
    :param idx: index of job to grab
    :return: Seconds since epoch that the job was started at
    """
    queue = db.lrange('jobs:queued', idx, idx)
    if not queue:
        return 0

    # TODO: decode just needed for the tests :(
    job_id = queue[0].decode('utf-8')
    job_key = 'job:{}'.format(job_id)

    added_str = db.hget(job_key, 'added')

    if not added_str:
        return 0

    return get_ts_from_string(added_str.decode('utf-8'))


def get_ts_from_string(timestring):
    """Convert a time string to a unix epoch timestamp

    :param timestring: str to convert
    :return: unix timestamp since epoch
    """
    # TODO: decode just needed for the tests :(
    dt = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S.%f")
    return dt.timestamp()

