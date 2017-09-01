# coding=utf-8
import Queue
from collections import deque


class LruQueue(Queue.Queue):
    '''Lru Queue base on thread-safe queue.'''

    def _init(self, maxsize):
        self.queue = deque([])

    def _get(self):
        return self.queue.popleft()

    def _put(self, item):
        self.queue.append(item)

    def items(self):
        return self.queue
