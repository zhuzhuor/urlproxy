#!/usr/bin/env python

# the default number of domain roots to be removed
NUM_REMOVED_ROOTS = 3

import tornado.web
import tornado.ioloop
import tornado.httpclient

#tornado.httpclient.AsyncHTTPClient.configure(
#        "tornado.curl_httpclient.CurlAsyncHTTPClient"
#)

#from pprint import pprint


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

    def _get_real_domain(self, num_removed_roots=NUM_REMOVED_ROOTS):
        # e.g., httpbin.org.127.0.0.1.xip.io will return httpbin.org
        d = self.request.host.split(':')[0]
        if d.endswith('.127.0.0.1.xip.io'):
            return d[:-17]

        l = d.split('.')
        assert len(l) > num_removed_roots
        return '.'.join(l[:(-num_removed_roots)])

    def _handle_response(self, response):
        self.set_status(response.code)

        #print
        #print self.request.uri
        #pprint(response.headers)

        # check the last comment of http://goo.gl/4w5yj
        for h in response.headers.keys():
            if h.lower() not in disallowed_response_headers:
                list_values = response.headers.get_list(h)
                # set_header should always be preferred
                # using only add_header will cause some problems
                # e.g. _clear_headers_for_304 doesn't work for _list_headers
                if len(list_values) == 1:
                    #print h, list_values[0]
                    self.set_header(h, list_values[0])
                else:
                    for v in list_values:
                        #print h, v
                        self.add_header(h, v)

        if response.body:
            self.write(response.body)

        #self.flush()
        self.finish()

    @tornado.web.asynchronous
    def get(self, uri):
        real_domain = self._get_real_domain()
        real_url = 'http://' + real_domain + uri
        #print real_domain
        #print real_url

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
        [(r'(.*)', ProxyHandler)],
        debug=True  # please set to false in production environments
)

if __name__ == "__main__":
    print 'Open your browser and try to access'
    print 'http://httpbin.org.127.0.0.1.xip.io:8888'
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
