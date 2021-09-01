from urllib.parse import urlsplit,urlunsplit
from collections import namedtuple

class ProxyUrl:
  proxyBaseUrl = ""

  def __init__(self, host, port):
    self.proxyBaseUrl = host[7:] + ':' + str(port)

  def ComposeProxy(self, url):
    urlParts = urlsplit(url)
    partsTuple = namedtuple('partsTuple', ['scheme', 'netloc', 'path', 'query', 'fragment'])
    urlNewParts = partsTuple(urlParts.scheme, self.proxyBaseUrl, urlParts.path, urlParts.query, urlParts.fragment)

    return urlunsplit(urlNewParts)