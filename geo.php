<?php

/* =========================
   CORS (must be first)
========================= */

header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Origin: https://myipnow.net");
header("Access-Control-Allow-Methods: GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

/* =========================
   AUTOLOAD
========================= */

require_once __DIR__ . '/vendor/autoload.php';

use MaxMind\Db\Reader;

/* =========================
   CONFIG
========================= */

$cityDb = '/usr/share/GeoIP/GeoLite2-City.mmdb';
$asnDb  = '/usr/share/GeoIP/GeoLite2-ASN.mmdb';

/* =========================
   GET CLIENT IP (CLOUDFLARE SAFE)
========================= */

function getClientIP() {

    $host = $_SERVER['HTTP_HOST'] ?? '';

    // Cloudflare real IP
    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        $ip = $_SERVER['HTTP_CF_CONNECTING_IP'];

        // Force IPv4 endpoint
        if ($host === 'ipv4.myipnow.net' &&
            filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
            return $ip;
        }

        // Force IPv6 endpoint
        if ($host === 'ipv6.myipnow.net' &&
            filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) {
            return $ip;
        }

        // Main domain (accept both)
        if (filter_var($ip, FILTER_VALIDATE_IP)) {
            return $ip;
        }
    }

    return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
}

$ip = getClientIP();

/* =========================
   SPLIT IPv4 / IPv6
========================= */

$ipv4 = null;
$ipv6 = null;

if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
    $ipv4 = $ip;
}

if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) {
    $ipv6 = $ip;
}

/* =========================
   GEO LOOKUP
========================= */

try {

    $cityReader = new Reader($cityDb);
    $asnReader  = new Reader($asnDb);

    $city = $cityReader->get($ip);
    $asn  = $asnReader->get($ip);

} catch (Exception $e) {

    http_response_code(500);
    echo json_encode([
        "error" => "Geo lookup failed"
    ]);
    exit;
}

/* =========================
   OUTPUT
========================= */

echo json_encode([
    "ip"        => $ip,
    "ipv4"      => $ipv4,
    "ipv6"      => $ipv6,

    "city"      => $city['city']['names']['en'] ?? null,
    "region"    => $city['subdivisions'][0]['names']['en'] ?? null,
    "country"   => $city['country']['names']['en'] ?? null,
    "postal"    => $city['postal']['code'] ?? null,
    "latitude"  => $city['location']['latitude'] ?? null,
    "longitude" => $city['location']['longitude'] ?? null,
    "timezone"  => $city['location']['time_zone'] ?? null,

    "asn" => isset($asn['autonomous_system_number'])
        ? "AS" . $asn['autonomous_system_number']
        : null,

    "isp" => $asn['autonomous_system_organization'] ?? null

], JSON_UNESCAPED_UNICODE);

