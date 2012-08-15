# urlproxy-node.js

A proxy server by manipulating URLs, written based on the non-blocking [node.js](http://nodejs.org).

For example, opening http://targetdomain.com.proxydomain.org/query you may access the real content at http://targetdomain.com/query. You can run the script locally and open http://httpbin.org.127.0.0.1.xip.io:8888/get to test. (Thank 37signals for the great xip.io.)

You can also put the target URL as a parameter of the request, such as http://127.0.0.1.xip.io:8888/?url=http://httpbin.org/get. If the target URL is somewhat complicated (having several query parameters concatenated with `&`), to avoid troubles the target URL can be encoded by base64. For example, to access http://httpbin.org/get?a=1&b=2, you can try http://127.0.0.1.xip.io:8888/?url=aHR0cDovL2h0dHBiaW4ub3JnL2dldD9hPTEmYj0y.

### License

    Copyright (C) 2012 Bo Zhu http://zhuzhu.org

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
