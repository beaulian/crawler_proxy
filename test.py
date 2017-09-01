# coding=utf-8
from crawler_proxy import ProxyPool


proxy_pool = ProxyPool()
proxy_pool.set_unblocking_producer()

print proxy_pool.get()
