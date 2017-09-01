# crawler_proxy
爬虫代理服务器池，保证线程安全，个人小练习

## 亮点
* 仿造request库的风格
* 考虑Python2和Python3的兼容性
* 利用原始socket套接字测试代理服务器是否可用
* 可定制crawler类
* 无阻塞定时爬取代理网站，但是比较简陋，可能有更好的实现方式

## 用法
请看test.py文件，block和timeout参数都是内置模块Queue的参数
https这个参数代表你要获取https代理还是http代理

## Tips
### 为什么我会用原始socket套接字测试代理服务器是否可用？<br>

因为这是开销最小的一种实现方法，你要是用一些封装了的网络库如requests，
即使内部有连接池，但是对这种代理服务器的host全都不一样的情况来说没有任何作用