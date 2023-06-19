from copy import copy
import re
from time import sleep
import requests
from requests_futures.sessions import FuturesSession
import math

from definitions import DYNAMIC_OUTPUT_HEADERS, ERROR_OUTPUT_HEADERS, STATIC_OUTPUT_HEADERS


def generate_static_headers(length, count, static_count, dynamic_count, content_type="text/html"):
    headers = copy(STATIC_OUTPUT_HEADERS)
    headers['Content-Length'] = headers["Content-Length"].format(length=length)
    headers['Content-Type'] = headers["Content-Type"].format(content_type=content_type)
    headers['Stat-Thread-Count'] = headers['Stat-Thread-Count'].format(count=count)
    headers['Stat-Thread-Static'] = headers['Stat-Thread-Static'].format(count=static_count)
    headers['Stat-Thread-Dynamic'] = headers['Stat-Thread-Dynamic'].format(count=dynamic_count)
    return headers

def generate_dynamic_headers(length, count, static_count, dynamic_count):
    headers = copy(DYNAMIC_OUTPUT_HEADERS)
    headers['Content-length'] = headers["Content-length"].format(length=length)
    headers['Stat-Thread-Count'] = headers['Stat-Thread-Count'].format(count=count)
    headers['Stat-Thread-Static'] = headers['Stat-Thread-Static'].format(count=static_count)
    headers['Stat-Thread-Dynamic'] = headers['Stat-Thread-Dynamic'].format(count=dynamic_count)
    return headers

def generate_error_headers(length, count, static_count, dynamic_count):
    headers = copy(ERROR_OUTPUT_HEADERS)
    headers['Content-Length'] = headers["Content-Length"].format(length=length)
    headers['Stat-Thread-Count'] = headers['Stat-Thread-Count'].format(count=count)
    headers['Stat-Thread-Static'] = headers['Stat-Thread-Static'].format(count=static_count)
    headers['Stat-Thread-Dynamic'] = headers['Stat-Thread-Dynamic'].format(count=dynamic_count)
    return headers

def validate_out(out: str, err: str, expected: str):
    return
    assert not err
    assert re.match(expected, out),\
        f"\nExpected:\n{expected}"\
        f"\nGot:\n{out}"


def validate_response(response: requests.models.Response, expected_headers: dict, expected: str):
    assert response.status_code == 200
    assert response.headers.keys() == expected_headers.keys(),\
        f"\nExpected:\n{list(expected_headers.keys())}"\
        f"\nGot:\n{list(response.headers.keys())}"
    for header, value in expected_headers.items():
        assert re.fullmatch(value, response.headers[header]),\
            f"\nHeader: {header}"\
            f"\nExpected:\n{value}"\
            f"\nGot:\n{response.headers[header]}"
    assert re.match(expected, response.text),\
        f"\nExpected:\n{expected}"\
        f"\nGot:\n{response.text}"


def validate_response_full(response: requests.models.Response, expected_headers: dict, expected: str):
    assert response.status_code == 200
    assert response.headers.keys() == expected_headers.keys(),\
        f"\nExpected:\n{list(expected_headers.keys())}"\
        f"\nGot:\n{list(response.headers.keys())}"
    for header, value in expected_headers.items():
        assert re.fullmatch(value, response.headers[header]),\
            f"\nHeader:\n{header}"\
            f"\nExpected:\n{value}"\
            f"\nGot:\n{response.headers[header]}"
    assert re.fullmatch(expected, response.text),\
        f"\nExpected:\n{expected}"\
        f"\nGot:\n{response.text}"


def validate_response_full_with_dispatch(response: requests.models.Response, expected_headers: dict, expected: str, dispatch: float):
    assert response.status_code == 200
    assert response.headers.keys() == expected_headers.keys(),\
        f"\nExpected:\n{list(expected_headers.keys())}"\
        f"\nGot:\n{list(response.headers.keys())}"
    for header, value in expected_headers.items():
        assert re.fullmatch(value, response.headers[header]),\
            f"\nHeader:\n{header}"\
            f"\nExpected:\n{value}"\
            f"\nGot:\n{response.headers[header]}"
    assert re.fullmatch(expected, response.text),\
        f"\nExpected:\n{expected}"\
        f"\nGot:\n{response.text}"
    assert abs(float(response.headers['Stat-Req-Dispatch'][2:]) - dispatch) < 0.1,\
        f"\nExpected:\n{dispatch}"\
        f"\nGot:\n{float(response.headers['Stat-Req-Dispatch'][2:])}"


def validate_response_binary(response: requests.models.Response, expected_headers: dict, expected: str):
    assert response.status_code == 200
    assert response.headers.keys() == expected_headers.keys(),\
        f"\nExpected:\n{list(expected_headers.keys())}"\
        f"\nGot:\n{list(response.headers.keys())}"
    for header, value in expected_headers.items():
        assert re.fullmatch(value, response.headers[header]),\
            f"\nHeader:\n{header}"\
            f"\nExpected:\n{value}"\
            f"\nGot:\n{response.headers[header]}"
    assert response.content

def validate_response_err(response: requests.models.Response, status: int, expected_headers: dict, expected: str):
    assert response.status_code == status
    assert response.headers.keys() == expected_headers.keys(),\
        f"\nExpected:\n{list(expected_headers.keys())}"\
        f"\nGot:\n{list(response.headers.keys())}"
    for header, value in expected_headers.items():
        assert re.fullmatch(value, response.headers[header]),\
            f"\nHeader:\n{header}"\
            f"\nExpected:\n{value}"\
            f"\nGot:\n{response.headers[header]}"
    assert re.fullmatch(expected, response.text),\
        f"\nExpected:\n{expected}"\
        f"\nGot:\n{response.text}"


def spawn_clients(amount, server_port):
    clients = []
    for i in range(amount):
        session = FuturesSession()
        clients.append((session, session.get(f"http://localhost:{server_port}/output.cgi?1.{i}")))
        sleep(0.1)
    return clients


def random_drop_formula(queue_size, in_queue):
    return math.ceil(in_queue * 0.5)
