<?php
header('Content-Type: text/plain');

echo "CF_CONNECTING_IP: " . ($_SERVER['HTTP_CF_CONNECTING_IP'] ?? 'none') . "\n";
echo "CF_PSEUDO_IPV4: " . ($_SERVER['HTTP_CF_PSEUDO_IPV4'] ?? 'none') . "\n";
echo "X_FORWARDED_FOR: " . ($_SERVER['HTTP_X_FORWARDED_FOR'] ?? 'none') . "\n";
echo "REMOTE_ADDR: " . ($_SERVER['REMOTE_ADDR'] ?? 'none') . "\n";

