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

    // Cloudflare real IP (correct)
    if (!empty($_SERVER['HTTP_CF_CONNECTING_IP']) &&
        filter_var($_SERVER['HTTP_CF_CONNECTING_IP'], FILTER_VALIDATE_IP)) {
        return $_SERVER['HTTP_CF_CONNECTING_IP'];
    }

    // X-Forwarded-For (first real public IP)
    if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
        $ips = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
        foreach ($ips as $ip) {
            $ip = trim($ip);
            if (filter_var($ip, FILTER_VALIDATE_IP)) {
                return $ip;
            }
        }
    }

    // Default
    return $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
}

$ip = getClientIP();

/* =========================
   IPv4 / IPv6 SPLIT
========================= */

$ipv4 = null;
$ipv6 = null;

if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
    $ipv4 = $ip;
}
elseif (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV6)) {
    $ipv6 = $ip;
}

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
    "ipv4" => $ipv4,
    "ipv6" => $ipv6,

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
], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
