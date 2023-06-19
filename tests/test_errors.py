import os
from signal import SIGINT
from time import sleep
import pytest
from requests import Session, exceptions
from requests_futures.sessions import FuturesSession

from server import Server, server_port
from definitions import FORBIDDEN_DYNAMIC_OUTPUT_CONTENT, FORBIDDEN_DYNAMIC_SERVER_OUTPUT_CONTENT, FORBIDDEN_STATIC_OUTPUT_CONTENT, FORBIDDEN_STATIC_SERVER_OUTPUT_CONTENT, NOT_FOUND_OUTPUT_CONTENT, NOT_FOUND_SERVER_OUTPUT_CONTENT, NOT_IMPLEMENTED_OUTPUT_CONTENT, NOT_IMPLEMENTED_SERVER_OUTPUT_CONTENT, SERVER_CONNECTION_OUTPUT, SERVER_POST_CONNECTION_OUTPUT
from utils import generate_error_headers, validate_out, validate_response_err


def test_not_found(server_port):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with Session() as session:
            response = session.get(
                f"http://localhost:{server_port}/not_exist.html")
            expected_headers = generate_error_headers(163, 1, 0, 0)
            expected = NOT_FOUND_OUTPUT_CONTENT.format(filename=r"\.\/public\/\/not_exist.html")
            validate_response_err(response, 404, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=r"/not_exist.html") + NOT_FOUND_SERVER_OUTPUT_CONTENT.format(
                length=163, count=1, static=0, dynamic=0, filename=r"\.\/public\/\/not_exist.html")
        validate_out(out, err, expected)

def test_not_implemented(server_port):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with Session() as session:
            response = session.post(
                f"http://localhost:{server_port}/not_exist.html")
            expected_headers = generate_error_headers(155, 1, 0, 0)
            expected = NOT_IMPLEMENTED_OUTPUT_CONTENT.format(method=r"POST")
            validate_response_err(response, 501, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_POST_CONNECTION_OUTPUT.format(
            filename=r"/not_exist.html") + NOT_IMPLEMENTED_SERVER_OUTPUT_CONTENT.format(
                length=155, count=1, static=0, dynamic=0, method=r"POST")
        validate_out(out, err, expected)

@pytest.fixture
def forbidden_file():
    with open("../public/forbidden.html", "w"):
        pass
    os.chmod("../public/forbidden.html", 0o333)
    yield "forbidden.html"
    os.remove("../public/forbidden.html")

def test_forbidden_file_static(server_port, forbidden_file):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with Session() as session:
            response = session.get(
                f"http://localhost:{server_port}/{forbidden_file}")
            expected_headers = generate_error_headers(163, 1, 0, 0)
            expected = FORBIDDEN_STATIC_OUTPUT_CONTENT.format(filename=fr"\.\/public\/\/{forbidden_file}")
            validate_response_err(response, 403, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=fr"/{forbidden_file}") + FORBIDDEN_STATIC_SERVER_OUTPUT_CONTENT.format(
                length=163, count=1, static=0, dynamic=0, filename=fr"\.\/public\/\/{forbidden_file}")
        validate_out(out, err, expected)

@pytest.fixture
def forbidden_folder():
    os.makedirs("../public/forbidden", exist_ok=True)
    yield "forbidden"
    os.rmdir("../public/forbidden")

def test_forbidden_folder_static(server_port, forbidden_folder):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with Session() as session:
            response = session.get(
                f"http://localhost:{server_port}/{forbidden_folder}")
            expected_headers = generate_error_headers(158, 1, 0, 0)
            expected = FORBIDDEN_STATIC_OUTPUT_CONTENT.format(filename=fr"\.\/public\/\/{forbidden_folder}")
            validate_response_err(response, 403, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=fr"/{forbidden_folder}") + FORBIDDEN_STATIC_SERVER_OUTPUT_CONTENT.format(
                length=158, count=1, static=0, dynamic=0, filename=fr"\.\/public\/\/{forbidden_folder}")
        validate_out(out, err, expected)

@pytest.fixture
def forbidden_file_dynamic():
    with open("../public/forbidden_file.cgi", "w"):
        pass
    os.chmod("../public/forbidden_file.cgi", 0o666)
    yield "forbidden_file.cgi"
    os.remove("../public/forbidden_file.cgi")

def test_forbidden_file_dynamic(server_port, forbidden_file_dynamic):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with Session() as session:
            response = session.get(
                f"http://localhost:{server_port}/{forbidden_file_dynamic}")
            expected_headers = generate_error_headers(173, 1, 0, 0)
            expected = FORBIDDEN_DYNAMIC_OUTPUT_CONTENT.format(filename=fr"\.\/public\/\/{forbidden_file_dynamic}")
            validate_response_err(response, 403, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=fr"/{forbidden_file_dynamic}") + FORBIDDEN_DYNAMIC_SERVER_OUTPUT_CONTENT.format(
                length=173, count=1, static=0, dynamic=0, filename=fr"\.\/public\/\/{forbidden_file_dynamic}")
        validate_out(out, err, expected)