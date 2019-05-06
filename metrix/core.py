"""Core logic of the antiSMASH metrics service"""
from datetime import datetime
from prometheus_client import Gauge
from typing import List

QUEUES = [
    'jobs:queued',
    'jobs:development',
    'jobs:legacy',
    'jobs:queued-fungi',
    'jobs:development-fungi',
    'jobs:legacy-fungi',
]


class GaugeWrapper:
    def __init__(self, full_name: str) -> None:
        queue_name = full_name.rsplit(':', 1)[-1].replace('-', '_')
        self.full_name = full_name
        self.queue_name = queue_name
        self.length_gauge = Gauge("queue_{}_length".format(queue_name),
                                  "Length of the {} queue".format(queue_name))
        self.newest_job_gauge = Gauge("{}_newest_job_age".format(queue_name),
                                      "Age of the newest job in queue {}, in seconds since epoch".format(queue_name))
        self.oldest_job_gauge = Gauge("{}_oldest_job_age".format(queue_name),
                                      "Age of the oldest job in queue {}, in seconds since epoch".format(queue_name))

    def update(self, db) -> None:
        self.length_gauge.set(db.llen(self.full_name))
        self.oldest_job_gauge.set(get_job_ts(db, self.full_name, -1))
        self.newest_job_gauge.set(get_job_ts(db, self.full_name, 0))


def build_gauges():
    gauges = []
    for queue_name in QUEUES:
        gauges.append(GaugeWrapper(queue_name))

    return gauges


def gather_metrics(db, gauges: List[GaugeWrapper]):
    """Gather metrics from the redis connection

    :param db: Redis connection to use
    """
    for gauge in gauges:
        gauge.update(db)


def get_job_ts(db, queue_name, idx):
    """Get the unix timestamp of the oldest job

    :param db: Redis connection to use
    :param idx: index of job to grab
    :return: Seconds since epoch that the job was started at
    """
    queue = db.lrange(queue_name, idx, idx)
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
    dtime = datetime.strptime(timestring, "%Y-%m-%d %H:%M:%S.%f")
    return dtime.timestamp()
