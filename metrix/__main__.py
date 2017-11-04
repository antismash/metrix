"""Command line for the antiSMASH metrics service"""
import argparse
from envparse import Env
from metrix import __version__
from .core import gather_metrics
from prometheus_client import start_http_server
from redis import Redis
import time

_EPILOG = """
metrix is free software, available under the Apache 2.0 license.
Find the code at https://github.com/antismash/metrix/
"""


def main():

    env = Env(
        # Port to expose the metrics on
        METRIX_PORT=dict(cast=int, default=8000),
        # URI of the Redis database to read metrics from
        METRIX_REDIS_URI=dict(cast=str, default="redis://localhost:6379/0"),
        # Refresh interval in seconds
        METRIX_REFRESH_INTERVAL=dict(cast=float, default=5.0),
    )

    parser = argparse.ArgumentParser(description="Metrics for the antiSMASH backend", epilog=_EPILOG)
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('-p', '--port', type=int, default=env('METRIX_PORT'),
            help="Port to expose the metrics on (default: %(default)s)")
    parser.add_argument('-r', '--redis-uri', default=env('METRIX_REDIS_URI'),
            help="URI of the Redis database to read metrics from (default: %(default)s)")
    parser.add_argument('-i', '--interval', type=float, default=env('METRIX_REFRESH_INTERVAL'),
            help="Refresh interval in seconds (default: %(default)s)")

    args = parser.parse_args()

    start_http_server(args.port)
    # TODO: This works for real Redis, but not for mockredis
    db_conn = Redis.from_url(args.redis_uri, charset="utf-8", decode_responses=True)
    while True:
        gather_metrics(db_conn)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
