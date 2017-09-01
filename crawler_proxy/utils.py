# coding=utf-8
import re
import socket
import random

from .compat import (
    urlparse, str
)


class Socket(socket.socket):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def reachable(proxy_url):
    if proxy_url is None:
        return False

    netloc = urlparse(proxy_url).netloc
    try:
        host, port = netloc.split(':')
    except ValueError:
        host, port = netloc.split(':')[0], 80

    max_timeout = 2
    with Socket(socket.AF_INET, socket.SOCK_STREAM) as sk:
        sk.settimeout(max_timeout)
        try:
            sk.connect((host, int(port)))
        except socket.timeout:
            return False
        except socket.error:
            return False
        else:
            return True


def gen_random_user_agent():
    user_agent_pool = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3197.0 Safari/537.36',
    ]

    return random.choice(user_agent_pool)


def calc_time_from_str(time_str):
    time_map = {
        '天': 86400,
        '小时': 3600,
        '分': 60,
        '分钟': 60,
        '秒': 1,
        '秒种': 1
    }

    if isinstance(time_str, str):
        time_str = time_str.encode('utf-8')

    number = re.match(r'\d+').group(0)
    assert int(number) != 0
    desc = time_str.lstrip(number)

    return int(number) * time_map.get(desc, 60)
