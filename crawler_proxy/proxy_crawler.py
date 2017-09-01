# coding=utf-8
import schedule
import requests
import threading
from lxml import etree

from .utils import gen_random_user_agent
from .constants import MAX_CRAWL_DEPTH
from .exceptions import CrawlerError
from .proxy import Proxy


class BaseCrawler(object):
    def __init__(self, max_crawl_depth=MAX_CRAWL_DEPTH):
        self._client = requests.Session()
        self._headers = {'User-Agent': gen_random_user_agent()}
        self._max_crawl_depth = max_crawl_depth

    def fetch(self, https=False):
        raise NotImplementedError


class XicidailiCrawler(BaseCrawler):
    def __init__(self, max_crawl_depth=MAX_CRAWL_DEPTH):
        self._base_http_url = 'http://www.xicidaili.com/wt/'
        self._base_https_url = 'http://www.xicidaili.com/wn/'

        super(XicidailiCrawler, self).__init__(max_crawl_depth=max_crawl_depth)

    def fetch(self, https=False):
        if https:
            url = self._base_https_url
        else:
            url = self._base_http_url

        for page_num in range(1, self._max_crawl_depth + 1):
            res = self._client.get(url + str(page_num), headers=self._headers)

            # parse
            html = etree.HTML(res.text)
            tables = html.xpath("//table[@id='ip_list']")
            if not tables:
                yield None
            for tr in tables[0].xpath("//tr")[1:]:
                try:
                    td = tr.xpath('td')[1:]
                    ip, port, scheme, expire = td[0].text, td[1].text, td[4].text, td[7].text
                except ValueError:
                    continue
                else:
                    yield Proxy(address='%s:%s' % (ip, port), schemes=(scheme,), expire=expire)


class KuaidailiCrawler(BaseCrawler):
    # this crawler is temporarily unavailable.
    def __init__(self, max_crawl_depth=MAX_CRAWL_DEPTH):
        self._host = 'http://www.kuaidaili.com'
        self._base_url = 'http://www.kuaidaili.com/free/inha/'

        super(KuaidailiCrawler, self).__init__(max_crawl_depth=max_crawl_depth)

    def __prepare_request(self):
        r = self._client.get(self._host)
        if 'Set-Cookie' not in r.headers:
            raise CrawlerError('cannot crawl this website %s' % self._host)
        self._headers.setdefault('Cookie', r.headers['Set-Cookie'])

    def fetch(self, https=False):
        self.__prepare_request()

        for page_num in range(1, self._max_crawl_depth + 1):
            res = self._client.get(self._base_url + str(page_num), headers=self._headers)

            # parse
            html = etree.HTML(res.text)
            print res.text
            tables = html.xpath("//tbody")
            if not tables:
                yield None

            print tables[0].xpath("//tr")
            for tr in tables[0].xpath("//tr")[1:]:
                try:
                    ip, port, _, schemes = tr.xpath('td')[0:4]
                except ValueError:
                    continue
                else:
                    yield Proxy(address='%s:%s' % (ip, port), schemes=tuple(schemes.split(',')))


default_crawler_class = XicidailiCrawler


class ProxyCrawlerMixin(object):
    def fetch(self, crawler_class=default_crawler_class):
        crawler = crawler_class(max_crawl_depth=self._max_crawl_depth)
        # http
        for proxy in crawler.fetch():
            # put to lru queue
            if proxy is None:
                break
            if self._http_queue.qsize() <= self._maxsize:
                self._try_put(proxy, block=False)

        # https
        for proxy in crawler.fetch(https=True):
            # put to lru queue
            if proxy is None:
                break
            if self._https_queue.qsize() <= self._maxsize:
                self._try_put(proxy, block=False, https=True)

    def __init_queue(self, crawler_class=default_crawler_class):
        t = threading.Thread(target=self.fetch, kwargs={'crawler_class': crawler_class})
        t.setDaemon(True)
        t.start()

    def timing_fetch(self, crawler_class=default_crawler_class):
        self.__init_queue(crawler_class=crawler_class)
        schedule.every(self._crawl_interval).seconds.do(self.fetch, crawler_class=crawler_class)
