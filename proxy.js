var http = require('http');
var url = require('url');
var querystring = require('querystring');


// it can also support usage as a proxy server
var support_proxy = true;


// the base portions of domain names to be removed
var base_domains = [
    '127.0.0.1.xip.io',
    'test.zhuzhu.org'
];


// http://stackoverflow.com/questions/646628/javascript-startswith
if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
        return this.slice(0, str.length) == str;
    };
}
if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function (str){
        return this.slice(-str.length) == str;
    };
}


function get_real_target(req_host, req_uri) {
    var real_target = {};
    req_host = req_host.split(':', 1)[0];

    if (support_proxy && req_uri.startsWith('http')) {
        real_target = url.parse(req_uri);
    } else {
        for (var i = 0; i < base_domains.length; i++) {
            if (req_host.endsWith(base_domains[i])) {
                var real_url;
                if (req_host.length > base_domains[i].length) {
                    real_url = 'http://' +
                            req_host.slice(0, req_host.length - base_domains[i].length - 1) + req_uri;
                } else {
                    real_url = querystring.parse(url.parse(req_uri).query).url;
                    if (!real_url.startsWith('http')) {
                        var buf = new Buffer(real_url, 'base64');
                        real_url = buf.toString();
                    }
                }
                real_target = url.parse(real_url);
                break;
            }
        }
    }
    if (!real_target.port)
        real_target.port = 80;
    return real_target;
}


http.createServer(function(request, response) {
    console.log(request.connection.remoteAddress + ': ' + request.method + ' ' + request.url);

    if (request.url === '/favicon.ico') {
        response.writeHead(404);
        response.end();
        return;
    }

    if (request.url === '/crossdomain.xml') {
        response.writeHead(200, {
            'Content-Type': 'text/xml'
        });
        response.end('<?xml version="1.0" encoding="UTF-8"?>\n' +
            '<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>');
        return;
    }

    var target = get_real_target(request.headers.host, request.url);
    if (!target.host) {
        response.writeHead(403);
        response.end();
        return;
    }

    request.headers.host = target.hostname;
    if (request.headers['proxy-connection']) {
        request.headers.connection = request.headers['proxy-connection'];
        delete request.headers['proxy-connection'];
    }
    var options = {
        host: target.host,
        hostname: target.hostname,
        port: +target.port,
        path: target.path,
        method: request.method,
        headers: request.headers
    };
    var proxy_req = http.request(options, function(res) {
        response.writeHead(res.statusCode, res.headers);

        res.on('data', function(chunk) {
            response.write(chunk);
        });
        res.on('end', function() {
            response.end();
        });
    });

    request.on('data', function(chunk) {
        proxy_req.write(chunk);
    });
    request.on('end', function() {
        proxy_req.end();
    });
}).listen(8888);

console.log('You can try');
console.log('http://httpbin.org.127.0.0.1.xip.io:8888/get');
console.log('or');
console.log('http://127.0.0.1.xip.io:8888/?url=aHR0cDovL2h0dHBiaW4ub3JnL2dldA==');
