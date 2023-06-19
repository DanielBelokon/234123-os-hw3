from signal import SIGINT
from time import sleep
import pytest

from server import Server, server_port
from definitions import STATIC_OUTPUT_CONTENT, DYNAMIC_OUTPUT_CONTENT, SERVER_CONNECTION_OUTPUT
from utils import generate_dynamic_headers, generate_static_headers, validate_out, validate_response_full
from requests_futures.sessions import FuturesSession


def test_static(server_port):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/home.html")
            response = future.result()
            expected_headers = generate_static_headers(293, 1, 1, 0)
            expected = STATIC_OUTPUT_CONTENT
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=r"/home.html")
        validate_out(out, err, expected)


def test_dynamic(server_port):
    with Server("./server", server_port, 4, 8, "block") as server:
        sleep(0.1)
        with FuturesSession() as session:
            future = session.get(f"http://localhost:{server_port}/output.cgi?1")
            response = future.result()
            expected_headers = generate_dynamic_headers(123, 1, 0, 1)
            expected = DYNAMIC_OUTPUT_CONTENT.format(
                seconds="1.0")
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=r"/output.cgi\?1")
        validate_out(out, err, expected)
