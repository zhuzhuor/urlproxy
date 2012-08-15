var http = require('http');
var url  = require('url');

http.createServer(function(request, response) {
    console.log(request.connection.remoteAddress + ": " + request.method + " " + request.url);

    var target = url.parse(request.url);
    if (!target.port) {
        target.port = 80;
    }
    request.headers.connection = request.headers['proxy-connection'];
    delete request.headers['proxy-connection'];
    delete request.headers.host;
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
}).listen(8080);
