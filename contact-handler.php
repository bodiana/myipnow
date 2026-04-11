<?php
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); exit; }

$name    = strip_tags(trim($_POST['name'] ?? ''));
$email   = strip_tags(trim($_POST['email'] ?? ''));
$message = strip_tags(trim($_POST['message'] ?? ''));

if (!$name || !$email || !$message || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Invalid input']);
    exit;
}

$to      = 'contact@myipnow.net';
$subject = 'MyIPNow Contact: ' . $name;
$body    = "Name: $name\nEmail: $email\n\nMessage:\n$message\n\n---\nReply directly to this email to respond to $name at $email";
$headers = "From: $name <$email>\r\nReply-To: $email\r\nContent-Type: text/plain; charset=UTF-8";

$sent = mail($to, $subject, $body, $headers);
header('Content-Type: application/json');
echo json_encode(['ok' => $sent]);
