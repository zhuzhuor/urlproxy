#!/usr/bin/env python

# the base portions of domain names to be removed
BASE_DOMAINS = (
        '127.0.0.1.xip.io',
        'test.zhuzhu.org',
        # add your domain name here
)

import tornado.web
import tornado.ioloop
import tornado.httpclient
from base64 import b64decode
from urlparse import urlparse


CROSSDOMAIN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<cross-domain-policy>
    <allow-access-from domain="*"/>
</cross-domain-policy>"""


disallowed_response_headers = frozenset([
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailers',
    'transfer-encoding',
    'upgrade',
    # all above are hop-by-hop headers
    'content-encoding',  # may cause decoding errors
    'content-length',
])


class ProxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST']

    def _get_real_things(self):
        domain = self.request.host.split(':')[0]
        for base_domain in BASE_DOMAINS:
            if domain.endswith(base_domain):
                if len(domain) > len(base_domain):
                    real_domain = domain[:-(len(base_domain) + 1)]
                    real_url = 'http://' + real_domain + self.request.uri
                else:
                    real_url = self.get_argument('url')
                    if not real_url.startswith('http://'):
                        real_url = b64decode(real_url)
                    real_domain = urlparse(real_url).netloc

                return real_domain, real_url

        # should not reach here
        return None, None

    def _handle_response(self, response):
        self.set_status(response.code)

        # check the last comment of http://goo.gl/4w5yj
        for h in response.headers.keys():
            if h.lower() not in disallowed_response_headers:
                list_values = response.headers.get_list(h)
                # set_header should always be preferred
                # using only add_header will cause some problems
                # e.g. _clear_headers_for_304 doesn't work for _list_headers
                if len(list_values) == 1:
                    self.set_header(h, list_values[0])
                else:
                    for v in list_values:
                        self.add_header(h, v)

        if response.body:
            self.write(response.body)

        self.finish()

    @tornado.web.asynchronous
    def get(self):
        if self.request.uri == '/favicon.ico':
            self.send_error(404)
            return

        elif self.request.uri == '/crossdomain.xml':
            self.set_status(200)
            self.set_header('Content-Type', 'text/xml')
            self.write(CROSSDOMAIN_XML)
            self.finish()
            return

        real_domain, real_url = self._get_real_things()
        if not real_domain or not real_url:
            self.send_error(403)
            return

        headers = self.request.headers
        if 'Host' in headers:
            headers['Host'] = real_domain

        http_req = tornado.httpclient.HTTPRequest(
            url=real_url,
            method=self.request.method,
            body=self.request.body,
            headers=headers,
            follow_redirects=False,
            allow_nonstandard_methods=True
        )

        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            http_client.fetch(http_req, self._handle_response)

        except tornado.httpclient.HTTPError, err:
            self.handle_response(err.response)

        except Exception, err:
            self.set_status(500)
            self.write('Internal Server Error: ' + str(err))
            self.finish()

    # def self.post() as self.get()
    post = get


application = tornado.web.Application(
        [(r'.*', ProxyHandler)],
        debug=True  # please set to false in production environments
)

if __name__ == "__main__":
    print 'You can try'
    print 'http://httpbin.org.127.0.0.1.xip.io:8888/get'
    print 'or'
    print 'http://127.0.0.1.xip.io:8888/?url=aHR0cDovL2h0dHBiaW4ub3JnL2dldA=='
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
