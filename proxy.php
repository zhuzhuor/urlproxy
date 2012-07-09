<?php

// Proxy-on-Name PHP Version
// Copyright (c) 2012 Bo Zhu http://zhuzhu.org
// Licensed under the MIT license.

// Based on Simple PHP Proxy by Ben Alman
// Project Home - http://benalman.com/projects/php-simple-proxy/
// Copyright (c) 2010 "Cowboy" Ben Alman,
// Dual licensed under the MIT and GPLv2 licenses.
// http://benalman.com/about/license/


require_once('http_response_code.php');


$url = $_GET['url'];

if (!$url) {
    http_response_code(400);  // bad request
    echo 'ERROR: url not specified';
    exit(400);
}

if (substr($url, 0, len('http://')) !== 'http://')
    $url = base64_decode($url);


// get content by using curl
$ch = curl_init($url);

if (strtolower($_SERVER['REQUEST_METHOD']) == 'post') {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $_POST);
}

$cookie = array();  // always send cookies
foreach ($_COOKIE as $key => $value) {
    $cookie[] = $key . '=' . $value;
}
$cookie[] = SID;  // always send session
$cookie = implode('; ', $cookie);

curl_setopt($ch, CURLOPT_COOKIE, $cookie);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);

list($header, $content) = preg_split('/([\r\n][\r\n])\\1/', curl_exec($ch), 2);
$info = curl_getinfo($ch);

curl_close($ch);


// start sending response
http_response_code((int) $info['http_code']);

$header_text = preg_split('/[\r\n]+/', $header);  // split header text into an array

foreach ($header_text as $header) {
    if (preg_match('/^(?:Content-Type|Content-Language|Set-Cookie):/i', $header)) {
        header($header);
    }
}

echo $content;

?>
