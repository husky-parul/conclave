import salmon.job
from . import sharemind, spark


def dispatch_all(peer, jobs):

    # create a lookup from job class to instantiated dispatcher
    dispatchers = {
        salmon.job.SharemindJob: sharemind.SharemindDispatcher(peer),
        salmon.job.SparkJob: spark.SparkDispatcher(peer)
    }

    # dispatch each job
    for job in jobs:
        try:
            # look up dispatcher and dispatch
            dispatchers[type(job)].dispatch(job)
        except Exception as e:
            print(e)
