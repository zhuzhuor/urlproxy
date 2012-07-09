<?php

// Proxy-on-Name PHP Version
// Copyright (c) 2012 Bo Zhu http://zhuzhu.org
// Licensed under the GPLv2 license.

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


$ch = curl_init($url);

if (strtolower($_SERVER['REQUEST_METHOD']) == 'post') {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $_POST);
}

// always send cookies
$cookie = array();
foreach ($_COOKIE as $key => $value) {
    $cookie[] = $key . '=' . $value;
}
// always send session
$cookie[] = SID;
$cookie = implode('; ', $cookie);

curl_setopt($ch, CURLOPT_COOKIE, $cookie);

curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

curl_setopt($ch, CURLOPT_USERAGENT, $_SERVER['HTTP_USER_AGENT']);

list($header, $contents) = preg_split('/([\r\n][\r\n])\\1/', curl_exec($ch), 2);

$info = curl_getinfo($ch);

curl_close($ch);


http_response_code((int) $info['http_code']);

// Split header text into an array.
$header_text = preg_split('/[\r\n]+/', $header);

foreach ($header_text as $header) {
    if (preg_match('/^(?:Content-Type|Content-Language|Set-Cookie):/i', $header)) {
        header($header);
    }
}

echo $contents;


?>
