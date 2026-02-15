<?php
require_once __DIR__ . '/vendor/autoload.php';

use MaxMind\Db\Reader;

/* =========================
   CONFIG
========================= */

$cityDb = '/usr/share/GeoIP/GeoLite2-City.mmdb';
$asnDb  = '/usr/share/GeoIP/GeoLite2-ASN.mmdb';

/* =========================
   GET REAL CLIENT IP
========================= */

function getClientIP() {

    // Force server IPv4 (for your JS dual request)
    if (isset($_GET['force_ipv4'])) {
        return $_SERVER['SERVER_ADDR'];
    }

    // Cloudflare
    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP'])) {
        return $_SERVER['HTTP_CF_CONNECTING_IP'];
    }

    // Proxy / Load balancer
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ips = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        return trim($ips[0]);
    }

    // Default
    return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
}

$ip = getClientIP();

/* =========================
   LOOKUP
========================= */

try {
    $cityReader = new Reader($cityDb);
    $asnReader  = new Reader($asnDb);

    $city = $cityReader->get($ip);
    $asn  = $asnReader->get($ip);

} catch (Exception $e) {
    echo json_encode(["error" => "Geo lookup failed"]);
    exit;
}

/* =========================
   OUTPUT
========================= */

echo json_encode([
    "ip" => $ip,

    "ipv4" => filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4) ? $ip : null,
    "ipv6" => filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6) ? $ip : null,

    "city" => $city['city']['names']['en'] ?? null,
    "region" => $city['subdivisions'][0]['names']['en'] ?? null,
    "country" => $city['country']['names']['en'] ?? null,
    "postal" => $city['postal']['code'] ?? null,
    "latitude" => $city['location']['latitude'] ?? null,
    "longitude" => $city['location']['longitude'] ?? null,
    "timezone" => $city['location']['time_zone'] ?? null,

    "asn" => isset($asn['autonomous_system_number'])
        ? "AS" . $asn['autonomous_system_number']
        : null,

    "isp" => $asn['autonomous_system_organization'] ?? null
]);

