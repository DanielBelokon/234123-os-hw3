STATIC_OUTPUT_HEADERS = {
    "Server": r"OS-HW3 Web Server",
    "Content-Length": r"{length}",
    "Content-Type": r"{content_type}",
    "Stat-Req-Arrival": r"\: \d+.\d+",
    "Stat-Req-Dispatch": r"\: \d+.\d+",
    "Stat-Thread-Id": r"\: \d+",
    "Stat-Thread-Count": r"\: {count}",
    "Stat-Thread-Static": r"\: {count}",
    "Stat-Thread-Dynamic": r"\: {count}"
}

DYNAMIC_OUTPUT_HEADERS = {
    "Server": r"OS-HW3 Web Server",
    "Stat-Req-Arrival": r"\: \d+.\d+",
    "Stat-Req-Dispatch": r"\: \d+.\d+",
    "Stat-Thread-Id": r"\: \d+",
    "Stat-Thread-Count": r"\: {count}",
    "Stat-Thread-Static": r"\: {count}",
    "Stat-Thread-Dynamic": r"\: {count}",
    "Content-length": r"{length}",
    "Content-type": r"text/html"
}

ERROR_OUTPUT_HEADERS = {
    "Content-Type": r"text/html",
    "Content-Length": r"{length}",
    "Stat-Req-Arrival": r"\: \d+.\d+",
    "Stat-Req-Dispatch": r"\: \d+.\d+",
    "Stat-Thread-Id": r"\: \d+",
    "Stat-Thread-Count": r"\: {count}",
    "Stat-Thread-Static": r"\: {count}",
    "Stat-Thread-Dynamic": r"\: {count}"
}

STATIC_OUTPUT_CONTENT = r"" \
    r"<html>[\r\n]+" \
    r"<head>[\r\n]+" \
    r"  <title>OS-HW3 Test Web Page<\/title>[\r\n]+" \
    r"<\/head>[\r\n]+" \
    r"<body>[\r\n]+" \
    r"<h2> OS-HW3 Test Web Page<\/h2>[\r\n]+" \
    r"<p> Test web page: simply awesome.<\/p>[\r\n]+" \
    r"<p> Click <a href=\"https:\/\/www.youtube.com\/watch\?v=dQw4w9WgXcQ\"> here<\/a> for something[\r\n]+" \
    r"even more awesome.<\/p>[\r\n]+" \
    r"<\/body>[\r\n]+" \
    r"<\/html>[\r\n]+$" \

DYNAMIC_OUTPUT_CONTENT = r"" \
    r"<p>Welcome to the CGI program<\/p>[\r\n]+" \
    r"<p>My only purpose is to waste time on the server!<\/p>[\r\n]+" \
    r"<p>I spun for {seconds}\d seconds<\/p>[\r\n]+$" \

SUCCESSFUL_CONNECTION = r"Header: HTTP\/1.0 200 OK[\r\n]+"
SERVER_CONNECTION_OUTPUT = r"GET {filename} HTTP\/1.1\n"
SERVER_POST_CONNECTION_OUTPUT = r"POST {filename} HTTP\/1.1\n"
SERVER_ABORT = r"Aborting server\n"

CLIENT_CONNECTION_RESET = r"Rio_readlineb error: Connection reset by peer\n"

NOT_FOUND_OUTPUT_CONTENT = r"" \
    r"<html>" \
    r"<title>OS-HW3 Error<\/title>"\
    r"<body bgcolor=fffff>[\r\n]+" \
    r"404: Not found[\r\n]+" \
    r"<p>OS-HW3 Server could not find this file: {filename}[\r\n]+" \
    r"<hr>OS-HW3 Web Server[\r\n]+"

NOT_FOUND_SERVER_OUTPUT_CONTENT = r"" \
    r"HTTP\/1.0 404 Not found[\r\n]+" \
    r"Content-Type: text\/html[\r\n]+" \
    r"Content-Length: {length}[\r\n]+" \
    r"Stat-Req-Arrival:: \d+.\d+[\r\n]+" \
    r"Stat-Req-Dispatch:: \d+.\d+[\r\n]+" \
    r"Stat-Thread-Id:: \d[\r\n]+" \
    r"Stat-Thread-Count:: {count}[\r\n]+" \
    r"Stat-Thread-Static:: {static}[\r\n]+" \
    r"Stat-Thread-Dynamic:: {dynamic}[\r\n]+"\
    + NOT_FOUND_OUTPUT_CONTENT

NOT_IMPLEMENTED_OUTPUT_CONTENT = r"" \
    r"<html>" \
    r"<title>OS-HW3 Error<\/title>"\
    r"<body bgcolor=fffff>[\r\n]+" \
    r"501: Not Implemented[\r\n]+" \
    r"<p>OS-HW3 Server does not implement this method: {method}[\r\n]+" \
    r"<hr>OS-HW3 Web Server[\r\n]+"

NOT_IMPLEMENTED_SERVER_OUTPUT_CONTENT = r"" \
    r"HTTP\/1.0 501 Not Implemented[\r\n]+" \
    r"Content-Type: text\/html[\r\n]+" \
    r"Content-Length: {length}[\r\n]+" \
    r"Stat-Req-Arrival:: \d+.\d+[\r\n]+" \
    r"Stat-Req-Dispatch:: \d+.\d+[\r\n]+" \
    r"Stat-Thread-Id:: \d[\r\n]+" \
    r"Stat-Thread-Count:: {count}[\r\n]+" \
    r"Stat-Thread-Static:: {static}[\r\n]+" \
    r"Stat-Thread-Dynamic:: {dynamic}[\r\n]+"\
    + NOT_IMPLEMENTED_OUTPUT_CONTENT

FORBIDDEN_STATIC_OUTPUT_CONTENT = r"" \
    r"<html>" \
    r"<title>OS-HW3 Error<\/title>"\
    r"<body bgcolor=fffff>[\r\n]+" \
    r"403: Forbidden[\r\n]+" \
    r"<p>OS-HW3 Server could not read this file: {filename}[\r\n]+" \
    r"<hr>OS-HW3 Web Server[\r\n]+"

FORBIDDEN_STATIC_SERVER_OUTPUT_CONTENT = r"" \
    r"HTTP\/1.0 403 Forbidden[\r\n]+" \
    r"Content-Type: text\/html[\r\n]+" \
    r"Content-Length: {length}[\r\n]+" \
    r"Stat-Req-Arrival:: \d+.\d+[\r\n]+" \
    r"Stat-Req-Dispatch:: \d+.\d+[\r\n]+" \
    r"Stat-Thread-Id:: \d[\r\n]+" \
    r"Stat-Thread-Count:: {count}[\r\n]+" \
    r"Stat-Thread-Static:: {static}[\r\n]+" \
    r"Stat-Thread-Dynamic:: {dynamic}[\r\n]+"\
    + FORBIDDEN_STATIC_OUTPUT_CONTENT

FORBIDDEN_DYNAMIC_OUTPUT_CONTENT = r"" \
    r"<html>" \
    r"<title>OS-HW3 Error<\/title>"\
    r"<body bgcolor=fffff>[\r\n]+" \
    r"403: Forbidden[\r\n]+" \
    r"<p>OS-HW3 Server could not run this CGI program: {filename}[\r\n]+" \
    r"<hr>OS-HW3 Web Server[\r\n]+"

FORBIDDEN_DYNAMIC_SERVER_OUTPUT_CONTENT = r"" \
    r"HTTP\/1.0 403 Forbidden[\r\n]+" \
    r"Content-Type: text\/html[\r\n]+" \
    r"Content-Length: {length}[\r\n]+" \
    r"Stat-Req-Arrival:: \d+.\d+[\r\n]+" \
    r"Stat-Req-Dispatch:: \d+.\d+[\r\n]+" \
    r"Stat-Thread-Id:: \d[\r\n]+" \
    r"Stat-Thread-Count:: {count}[\r\n]+" \
    r"Stat-Thread-Static:: {static}[\r\n]+" \
    r"Stat-Thread-Dynamic:: {dynamic}[\r\n]+"\
    + FORBIDDEN_DYNAMIC_OUTPUT_CONTENT
