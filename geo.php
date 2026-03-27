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
   GET IP (typed or visitor)
========================= */
function getClientIP() {
    $host = $_SERVER['HTTP_HOST'] ?? '';

    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        $ip = $_SERVER['HTTP_CF_CONNECTING_IP'];

        if ($host === 'ipv4.myipnow.net' &&
            filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) return $ip;

        if ($host === 'ipv6.myipnow.net' &&
            filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) return $ip;

        if (filter_var($ip, FILTER_VALIDATE_IP)) return $ip;
    }

    return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
}

// Use typed IP if provided
$ip = $_GET['ip'] ?? getClientIP();

// Validate
if (!filter_var($ip, FILTER_VALIDATE_IP)) {
    http_response_code(400);
    echo json_encode(["error" => "Invalid IP"]);
    exit;
}

/* =========================
   SPLIT IPv4 / IPv6
========================= */
$ipv4 = filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) ? $ip : null;
$ipv6 = filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6) ? $ip : null;

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
    echo json_encode(["error" => "Geo lookup failed"]);
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
