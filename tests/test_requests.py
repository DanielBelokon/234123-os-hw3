import os
from signal import SIGINT
from time import sleep
import pytest

from server import Server, server_port
from definitions import NOT_FOUND_OUTPUT_CONTENT, NOT_IMPLEMENTED_OUTPUT_CONTENT, STATIC_OUTPUT_CONTENT, DYNAMIC_OUTPUT_CONTENT, SERVER_CONNECTION_OUTPUT
from utils import generate_dynamic_headers, generate_error_headers, generate_static_headers, validate_out, validate_response_err, validate_response_full
from requests_futures.sessions import FuturesSession


@pytest.fixture
def gif_file():
    with open("../public/file.gif", "w") as f:
        f.write("I am gif")
    yield "file.gif"
    os.remove("../public/file.gif")


def test_gif(server_port, gif_file):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/{gif_file}")
            response = future.result()
            expected_headers = generate_static_headers(
                8, 1, 1, 0, content_type="image/gif")
            expected = "I am gif"
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=fr"/{gif_file}")
        validate_out(out, err, expected)


@pytest.fixture
def jpg_file():
    with open("../public/file.jpg", "w") as f:
        f.write("I am jpg")
    yield "file.jpg"
    os.remove("../public/file.jpg")


def test_jpg(server_port, jpg_file):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/{jpg_file}")
            response = future.result()
            expected_headers = generate_static_headers(
                8, 1, 1, 0, content_type="image/jpeg")
            expected = "I am jpg"
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=fr"/{jpg_file}")
        validate_out(out, err, expected)

@pytest.fixture
def plain_file():
    with open("../public/file", "w") as f:
        f.write("I am plain")
    yield "file"
    os.remove("../public/file")


def test_plain(server_port, plain_file):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/{plain_file}")
            response = future.result()
            expected_headers = generate_static_headers(
                10, 1, 1, 0, content_type="text/plain")
            expected = "I am plain"
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=fr"/{plain_file}")
        validate_out(out, err, expected)

def test_static_slash(server_port):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/")
            response = future.result()
            expected_headers = generate_static_headers(293, 1, 1, 0)
            expected = STATIC_OUTPUT_CONTENT
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=r"/")
        validate_out(out, err, expected)

def test_statistics(server_port):
    with Server("./server", server_port, 1, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/")
            response = future.result()
            expected_headers = generate_static_headers(293, 1, 1, 0)
            expected = STATIC_OUTPUT_CONTENT
            validate_response_full(response, expected_headers, expected)
        with FuturesSession() as session:
            future = session.get(
                f"http://localhost:{server_port}/not_exist.html")
            response = future.result()
            expected_headers = generate_error_headers(163, 2, 1, 0)
            expected = NOT_FOUND_OUTPUT_CONTENT.format(filename=r"\.\/public\/\/not_exist.html")
            validate_response_err(response, 404, expected_headers, expected)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/")
            response = future.result()
            expected_headers = generate_static_headers(293, 3, 2, 0)
            expected = STATIC_OUTPUT_CONTENT
            validate_response_full(response, expected_headers, expected)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/output.cgi?1")
            response = future.result()
            expected_headers = generate_dynamic_headers(123, 4, 2, 1)
            expected = DYNAMIC_OUTPUT_CONTENT.format(
                seconds="1.0")
            validate_response_full(response, expected_headers, expected)
        with FuturesSession() as session:
            future = session.post(
                f"http://localhost:{server_port}/not_exist.html")
            response = future.result()
            expected_headers = generate_error_headers(155, 5, 2, 1)
            expected = NOT_IMPLEMENTED_OUTPUT_CONTENT.format(method=r"POST")
            validate_response_err(response, 501, expected_headers, expected)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/")
            response = future.result()
            expected_headers = generate_static_headers(293, 6, 3, 1)
            expected = STATIC_OUTPUT_CONTENT
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=r"/")
        validate_out(out, err, expected)