#!/usr/bin/env python

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

    def handle_response(self, response):
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
    def get(self):
        headers = {h: v for (h, v) in self.request.headers.items() \
                if not h.lower().startswith('proxy')
        }

        http_req = tornado.httpclient.HTTPRequest(
            url=self.request.uri,
            method=self.request.method,
            body=self.request.body,
            #headers=self.request.headers,
            headers=headers,
            follow_redirects=False,
            allow_nonstandard_methods=True
        )

        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            http_client.fetch(http_req, self.handle_response)

        except tornado.httpclient.HTTPError, err:
            self.handle_response(err.response)

        except Exception, err:
            self.set_status(500)
            self.write('Internal Server Error: ' + str(err))
            self.finish()

    # def self.post() as self.get()
    post = get

application = tornado.web.Application([(r'.*', ProxyHandler)], debug=True)


if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
