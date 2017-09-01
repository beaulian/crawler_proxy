# coding=utf-8
import time
import schedule
import threading

from .constants import (
    MAXSIZE, MAX_CRAWL_DEPTH, CRAWL_INVERTAL
)
from .structures import LruQueue
from .proxy_crawler import (
    ProxyCrawlerMixin, default_crawler_class
)


class ProxyPool(ProxyCrawlerMixin):
    def __init__(self, maxsize=MAXSIZE,
                 max_crawl_depth=MAX_CRAWL_DEPTH,
                 crawl_interval=CRAWL_INVERTAL):

        self._http_queue = LruQueue(maxsize=maxsize)
        self._https_queue = LruQueue(maxsize=maxsize)

        self._is_start = False
        self._maxsize = maxsize
        self._max_crawl_depth = max_crawl_depth
        self._crawl_interval = crawl_interval

    def get(self, block=True, timeout=None, https=False):
        return self._try_get(block=block, timeout=timeout, https=https)

    def _try_get(self, block=True, timeout=None, https=False):
        if https:
            queue = self._https_queue
        else:
            queue = self._https_queue

        proxy = queue.get(block=block, timeout=timeout)
        while not proxy.try_connect() or proxy.is_expired():
            proxy = queue.get(block=block, timeout=timeout)
        queue.put(proxy)

        return proxy

    def _try_put(self, proxy, block=True, timeout=None, https=False):
        if proxy.try_connect():
            if https:
                self._http_queue.put(proxy, block=block, timeout=timeout)
            else:
                self._https_queue.put(proxy, block=block, timeout=timeout)

    def set_unblocking_producer(self, crawler_class=default_crawler_class):
        self.timing_fetch(crawler_class=crawler_class)

        def schedule_run():
            while True:
                schedule.run_pending()
                time.sleep(1)

        t = threading.Thread(target=schedule_run)
        t.setDaemon(True)
        t.start()


