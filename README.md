# urlproxy-php

A PHP verion of the [urlproxy](https://github.com/zhuzhuor/urlproxy).

To make a proxy to the content at a target URL, such as http://httpbin.org/get, you can simply put the target URL as a parameter of the request, such as http://127.0.0.1.xip.io/proxy.php?url=http://httpbin.org/get.

If the target URL is somewhat complicated (e.g., having several query parameters concatenated with `&`), to avoid troubles the target URL can be encoded by base64. For example, to access http://httpbin.org/get?a=1&b=2, you can try http://127.0.0.1.xip.io/proxy.php?url=aHR0cDovL2h0dHBiaW4ub3JnL2dldD9hPTEmYj0y.
