from codecs import raw_unicode_escape_decode
from math import ceil
import random
from signal import SIGINT
from time import sleep
import pytest
import psutil

from server import Server, server_port
import requests
from utils import *
from definitions import *

"""
The tests in this file are based on the description of the tests given by the course staff last semester.
"""


@pytest.mark.parametrize("policy",
                         [
                             "dh",
                             "dt",
                             "random",
                             "block"
                         ])
def test_basic(policy, server_port):
    """check if the webserver can serve requests"""
    with Server("./server", server_port, 1, 1, policy) as server:
        sleep(0.1)
        for req in ["output.cgi?1", "favicon.ico", "home.html"]:
            session = FuturesSession()
            r = session.get(f"http://localhost:{server_port}/{req}").result()
            assert r.status_code == 200
            assert r.content
        server.send_signal(SIGINT)
        out, err = server.communicate()


@pytest.mark.parametrize("policy",
                         [
                             "dh",
                             "dt",
                             "random",
                             "block"
                         ])
def test_nobusywait(policy, server_port):
    """test to make sure you are not busy-waiting"""
    with Server("./server", server_port, 1, 1, policy) as server:
        sleep(0.3)
        p = [p for p in psutil.process_iter() if server.pid == p.pid][0]
        assert p.cpu_percent() == 0
        r = requests.get(f"http://localhost:{server_port}/output.cgi?1")
        assert r.status_code == 200
        assert r.content
        assert p.cpu_percent() < 1


@pytest.mark.parametrize("policy, threads, queue_size",
                         [
                             ("block", 2, 10),
                             ("block", 4, 15),
                             ("block", 6, 20),
                             ("dh", 2, 10),
                             ("dh", 4, 15),
                             ("dh", 6, 20),
                             ("dt", 2, 10),
                             ("dt", 4, 15),
                             ("dt", 6, 20),
                             ("random", 2, 10),
                             ("random", 4, 15),
                             ("random", 6, 20),
                         ])
def test_pool(policy, threads, queue_size, server_port):
    """check if using a fixed size thread pool"""
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        stats = [stats for stats in psutil.process_iter() if server.pid == stats.pid][0]
        assert stats.num_threads() == threads + 1


SINGLE_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
                '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")]
                }


@pytest.mark.parametrize("policy, threads, num_clients, queue_size, times, files",
                         [
                             ("block", 1,  25, 30, 20, SINGLE_FILES),
                             ("dh", 1,  25, 30, 20, SINGLE_FILES),
                             ("dt", 1,  25, 30, 20, SINGLE_FILES),
                             ("random", 1,  25, 30, 20, SINGLE_FILES),
                         ])
def test_single(policy, threads, num_clients, queue_size, times, files, server_port):
    """single thread serving many requests server params: threads 1, Q_size 30. 
    25 clients each requesting ['/home.html', '/favicon.ico'], 20 times"""
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        for _ in range(times):
            for file_name, options in files.items():
                clients = []
                for _ in range(num_clients):
                    session = FuturesSession()
                    clients.append((session, session.get(f"http://localhost:{server_port}/{file_name}")))
                for client in clients:
                    response = client[1].result()
                    client[0].close()
                    expected = options[1]
                    expected_headers = options[2]
                    if options[0]:
                        validate_response_full(response, expected_headers, expected)
                    else:
                        validate_response_binary(response, expected_headers, expected)


LIGHT_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
               '/output.cgi?0.1': [True, DYNAMIC_OUTPUT_CONTENT.format(count=r"\d+", static=r"\d+", dynamic=r"\d+", seconds="0.1"),  generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
               '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")],
               '/output.cgi?0.02': [True, DYNAMIC_OUTPUT_CONTENT.format(count=r"\d+", static=r"\d+", dynamic=r"\d+", seconds="0.0"),  generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")]
               }

LIGHT2_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
                '/output.cgi?0.0112': [True, DYNAMIC_OUTPUT_CONTENT.format(count=r"\d+", static=r"\d+", dynamic=r"\d+", seconds="0.0"),  generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
                '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")]
                }


@pytest.mark.parametrize("policy, threads, num_clients, queue_size, times, files",
                         [
                             ("block", 20, 5, 10, 20, LIGHT_FILES),
                             ("block", 16, 4, 32, 30, LIGHT2_FILES),
                             ("dh", 20, 5, 10, 20, LIGHT_FILES),
                             ("dh", 16, 4, 32, 30, LIGHT2_FILES),
                             ("dt", 20, 5, 10, 20, LIGHT_FILES),
                             ("dt", 16, 4, 32, 30, LIGHT2_FILES),
                             ("random", 20, 5, 10, 20, LIGHT_FILES),
                             ("random", 16, 4, 32, 30, LIGHT2_FILES),
                         ])
def test_light(policy, threads, num_clients, queue_size, times, files, server_port):
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        for _ in range(times):
            for file_name, options in files.items():
                clients = []
                for _ in range(num_clients):
                    session = FuturesSession()
                    clients.append((session, session.get(f"http://localhost:{server_port}/{file_name}")))
                for client in clients:
                    response = client[1].result()
                    client[0].close()
                    expected = options[1]
                    expected_headers = options[2]
                    if options[0]:
                        validate_response_full(response, expected_headers, expected)
                    else:
                        validate_response_binary(response, expected_headers, expected)


LOCKS_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
               '/output.cgi?0.3': [True, DYNAMIC_OUTPUT_CONTENT.format(seconds="0.3"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
               '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")]
               }

LOCKS2_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
                '/output.cgi?0.3': [True, DYNAMIC_OUTPUT_CONTENT.format(seconds="0.3"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
                '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")],
                '/output.cgi?0.2': [True, DYNAMIC_OUTPUT_CONTENT.format(seconds="0.2"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")]
                }

LOCKS3_FILES = LOCKS2_FILES

LOCKS4_FILES = {'/output.cgi?0.01': [True, DYNAMIC_OUTPUT_CONTENT.format(seconds="0.0"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
                '/output.cgi?0.02': [True, DYNAMIC_OUTPUT_CONTENT.format(seconds="0.0"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
                '/output.cgi?0.005': [True, DYNAMIC_OUTPUT_CONTENT.format(seconds="0.0"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")]
                }


@pytest.mark.parametrize("policy, threads, num_clients, queue_size, times, files",
                         [
                             ("block", 8, 20, 16, 20, LOCKS_FILES),
                             ("block", 32, 40, 64, 10, LOCKS2_FILES),
                             ("block", 64, 50, 128, 6, LOCKS3_FILES),
                             ("block", 25, 20, 27, 20, LOCKS4_FILES),
                             ("dt", 32, 40, 64, 10, LOCKS2_FILES),
                             ("dt", 64, 50, 128, 6, LOCKS3_FILES),
                             ("dt", 25, 20, 27, 20, LOCKS4_FILES),
                             ("dh", 32, 40, 64, 10, LOCKS2_FILES),
                             ("dh", 64, 50, 128, 6, LOCKS3_FILES),
                             ("dh", 25, 20, 27, 20, LOCKS4_FILES),
                             ("random", 32, 40, 64, 10, LOCKS2_FILES),
                             ("random", 64, 50, 128, 6, LOCKS3_FILES),
                             ("random", 25, 20, 27, 20, LOCKS4_FILES),
                         ])
def test_locks(policy, threads, num_clients, queue_size, times, files, server_port):
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        for _ in range(times):
            for file_name, options in files.items():
                clients = []
                for _ in range(num_clients):
                    session = FuturesSession()
                    clients.append((session, session.get(f"http://localhost:{server_port}/{file_name}")))
                for client in clients:
                    response = client[1].result()
                    client[0].close()
                    expected = options[1]
                    expected_headers = options[2]
                    if options[0]:
                        validate_response_full(response, expected_headers, expected)
                    else:
                        validate_response_binary(response, expected_headers, expected)


EQUAL_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
               '/output.cgi?0.3': [True, DYNAMIC_OUTPUT_CONTENT.format(count=r"\d+", static=r"\d+", dynamic=r"\d+", seconds="0.3"),  generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
               '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")]
               }


@pytest.mark.parametrize("policy, threads, num_clients, queue_size, times, files",
                         [
                             ("block", 8, 20, 8, 10, EQUAL_FILES),
                             ("block", 32, 32, 32, 20, EQUAL_FILES),
                             ("block", 16, 12, 16, 20, EQUAL_FILES),
                             ("dh", 32, 32, 32, 20, EQUAL_FILES),
                             ("dh", 16, 12, 16, 20, EQUAL_FILES),
                             ("dt", 32, 32, 32, 20, EQUAL_FILES),
                             ("dt", 16, 12, 16, 20, EQUAL_FILES),
                             ("random", 32, 32, 32, 20, EQUAL_FILES),
                             ("random", 16, 12, 16, 20, EQUAL_FILES),
                         ])
def test_equal(policy, threads, num_clients, queue_size, times, files, server_port):
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        for _ in range(times):
            for file_name, options in files.items():
                clients = []
                for _ in range(num_clients):
                    session = FuturesSession()
                    clients.append((session, session.get(f"http://localhost:{server_port}/{file_name}")))
                for client in clients:
                    response = client[1].result()
                    client[0].close()
                    expected = options[1]
                    expected_headers = options[2]
                    if options[0]:
                        validate_response_full(response, expected_headers, expected)
                    else:
                        validate_response_binary(response, expected_headers, expected)


FEWER_FILES = {'/home.html': [True, STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")],
               '/output.cgi?0.3': [True, DYNAMIC_OUTPUT_CONTENT.format(count=r"\d+", static=r"\d+", dynamic=r"\d+", seconds="0.3"),  generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
               '/favicon.ico': [False, None, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/plain")]
               }


@pytest.mark.parametrize("policy, threads, num_clients, queue_size, times, files",
                         [
                             ("block", 16, 20, 8, 20, FEWER_FILES),
                             ("dt", 16, 20, 8, 20, FEWER_FILES),
                             ("dh", 16, 20, 8, 20, FEWER_FILES),
                             ("random", 16, 20, 8, 20, FEWER_FILES),
                         ])
def test_fewer(policy, threads, num_clients, queue_size, times, files, server_port):
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        for _ in range(times):
            for file_name, options in files.items():
                clients = []
                for _ in range(num_clients):
                    session = FuturesSession()
                    clients.append((session, session.get(f"http://localhost:{server_port}/{file_name}")))
                dropped = 0
                for client in clients:
                    try:
                        response = client[1].result()
                    except requests.exceptions.ConnectionError:
                        dropped += 1
                        continue
                    finally:
                        client[0].close()
                    expected = options[1]
                    expected_headers = options[2]
                    if options[0]:
                        validate_response_full(response, expected_headers, expected)
                    else:
                        validate_response_binary(response, expected_headers, expected)
                assert dropped == (num_clients - queue_size if policy != "block" and ".cgi" in file_name else 0)


@pytest.mark.parametrize("threads, num_clients, queue_size, times",
                         [
                             (2, 14, 8, 5),
                         ])
def test_drop_head(threads, num_clients, queue_size, times, server_port):
    with Server("./server", server_port, threads, queue_size, "dh") as server:
        sleep(0.1)
        for _ in range(times):
            slowers = []
            dropped = []
            alive = []
            dropped_size = (num_clients - queue_size)
            for _ in range(threads):
                session = FuturesSession()
                slowers.append((session, session.get(f"http://localhost:{server_port}/output.cgi?3")))
            sleep(0.2)
            for _ in range(dropped_size):
                session = FuturesSession()
                dropped.append((session, session.get(f"http://localhost:{server_port}/home.html")))

            sleep(1)
            for _ in range(num_clients - threads - dropped_size):
                session = FuturesSession()
                alive.append((session, session.get(f"http://localhost:{server_port}/home.html")))

            for client in slowers:
                response = client[1].result()
                client[0].close()
                expected = DYNAMIC_OUTPUT_CONTENT.format(seconds="3.0")
                expected_headers = generate_dynamic_headers(123, r"\d+", r"\d+", r"\d+")
                validate_response_full(response, expected_headers, expected)

            for client in dropped:
                with pytest.raises(requests.exceptions.ConnectionError):
                    client[1].result()
                client[0].close()

            for client in alive:
                response = client[1].result()
                client[0].close()
                expected = STATIC_OUTPUT_CONTENT
                expected_headers = generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")
                validate_response_full(response, expected_headers, expected)


@pytest.mark.parametrize("threads, num_clients, queue_size, times",
                         [
                             (2, 12, 8, 5),
                         ])
def test_drop_tail(threads, num_clients, queue_size, times, server_port):
    with Server("./server", server_port, threads, queue_size, "dt") as server:
        sleep(0.1)
        for _ in range(times):
            slowers = []
            alive = []
            dropped = []
            alive_size = (queue_size - threads)
            for _ in range(threads):
                session = FuturesSession()
                slowers.append((session, session.get(f"http://localhost:{server_port}/output.cgi?3")))
            sleep(0.2)
            for _ in range(alive_size):
                session = FuturesSession()
                alive.append((session, session.get(f"http://localhost:{server_port}/home.html")))

            sleep(1)
            for _ in range(num_clients - threads - alive_size):
                session = FuturesSession()
                dropped.append((session, session.get(f"http://localhost:{server_port}/home.html")))

            for client in slowers:
                response = client[1].result()
                client[0].close()
                expected = DYNAMIC_OUTPUT_CONTENT.format(seconds="3.0")
                expected_headers = generate_dynamic_headers(123, r"\d+", r"\d+", r"\d+")
                validate_response_full(response, expected_headers, expected)

            for client in alive:
                response = client[1].result()
                client[0].close()
                expected = STATIC_OUTPUT_CONTENT
                expected_headers = generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")
                validate_response_full(response, expected_headers, expected)

            for client in dropped:
                with pytest.raises(requests.exceptions.ConnectionError):
                    client[1].result()
                client[0].close()


@pytest.mark.parametrize("threads, num_clients, queue_size, times",
                         [
                             (2, 12, 8, 5),
                         ])
def test_drop_random(threads, num_clients, queue_size, times, server_port):
    with Server("./server", server_port, threads, queue_size, "random") as server:
        sleep(0.1)
        for _ in range(times):
            slowers = []
            others = []
            for _ in range(threads):
                session = FuturesSession()
                slowers.append((session, session.get(f"http://localhost:{server_port}/output.cgi?2")))
            sleep(0.5)
            in_queue = 0
            expected_drop = 0
            for _ in range(num_clients - threads):
                if threads + in_queue >= queue_size:
                    temp_in_queue=in_queue
                    in_queue -= random_drop_formula(queue_size, temp_in_queue)
                    expected_drop += random_drop_formula(queue_size, temp_in_queue)
                session = FuturesSession()
                others.append((session, session.get(f"http://localhost:{server_port}/home.html")))
                in_queue += 1

            for client in slowers:
                response = client[1].result()
                client[0].close()
                expected = DYNAMIC_OUTPUT_CONTENT.format(seconds="2.0")
                expected_headers = generate_dynamic_headers(123, r"\d+", r"\d+", r"\d+")
                validate_response_full(response, expected_headers, expected)

            dropped = 0
            for client in others:
                try:
                    response = client[1].result()
                    expected = STATIC_OUTPUT_CONTENT
                    expected_headers = generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+", "text/html")
                    validate_response_full(response, expected_headers, expected)
                except requests.exceptions.ConnectionError:
                    dropped += 1
                client[0].close()
            assert expected_drop == dropped


STATS_FILES = {'/home.html': [STATIC_OUTPUT_CONTENT, generate_static_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
               '/output.cgi?0.1': [DYNAMIC_OUTPUT_CONTENT.format(count=r"\d+", static=r"\d+", dynamic=r"\d+", seconds="0.1"), generate_dynamic_headers(r"\d+", r"\d+", r"\d+", r"\d+")],
               }


STATS_EXTRACTOR = r"Header: Stat-Thread-Id:: (\d+)[\r\n]+" \
    r"Header: Stat-Thread-Count:: (\d+)[\r\n]+" \
    r"Header: Stat-Thread-Static:: (\d+)[\r\n]+" \
    r"Header: Stat-Thread-Dynamic:: (\d+)[\r\n]+"


@pytest.mark.parametrize("policy, threads, queue_size, dynamic, static",
                         [
                             ("block", 1, 8, 4, 4),
                             ("block", 4, 10, 4, 4),
                             ("block", 20, 100, 50, 50),
                             ("dt", 1, 8, 4, 4),
                             ("dt", 4, 10, 4, 4),
                             ("dt", 20, 100, 50, 50),
                             ("dh", 1, 8, 4, 4),
                             ("dh", 4, 10, 4, 4),
                             ("dh", 20, 100, 50, 50),
                             ("random", 1, 8, 4, 4),
                             ("random", 4, 10, 4, 4),
                             ("random", 20, 100, 50, 50),
                         ])
def test_stats(policy, threads, queue_size, dynamic, static, server_port):
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        ask_for = ['/home.html'] * static + ['/output.cgi?0.1'] * dynamic
        random.shuffle(ask_for)
        clients = []
        for i in range(len(ask_for)):
            session = FuturesSession()
            clients.append((session, session.get(f"http://localhost:{server_port}/{ask_for[i]}")))
            sleep(0.1)

        threads_stats = {}
        for i in range(len(ask_for)):
            response = clients[i][1].result()
            clients[i][0].close()
            expected, expected_headers = STATS_FILES[ask_for[i]]
            validate_response_full(response, expected_headers, expected)
            tid = response.headers["Stat-Thread-Id"][2:]
            all = response.headers["Stat-Thread-Count"][2:]
            s = response.headers["Stat-Thread-Static"][2:]
            d = response.headers["Stat-Thread-Dynamic"][2:]
            threads_stats[tid] = (int(all), int(s), int(d))

        assert sum(all for all, s, d in threads_stats.values()) == dynamic + static
        assert sum(s for all, s, d in threads_stats.values()) == static
        assert sum(d for all, s, d in threads_stats.values()) == dynamic


@pytest.mark.parametrize("policy, threads, num_clients, queue_size",
                         [
                             ("block", 2, 4, 10),
                             ("dt", 2, 4, 10),
                             ("dh", 2, 4, 10),
                             ("random", 2, 4, 10),
                         ])
def test_stats_dispatch_time(policy, threads, num_clients, queue_size, server_port):
    """dispatch time should be greater than 1 secs when sending 1sec 4 dynamic requests. the server only has 2 worker threads."""
    with Server("./server", server_port, threads, queue_size, policy) as server:
        sleep(0.1)
        clients = []
        for _ in range(num_clients):
            session = FuturesSession()
            clients.append((session, session.get(f"http://localhost:{server_port}/output.cgi?1")))

        dispatches = []
        for client in clients:
            response = client[1].result()
            client[0].close()
            expected = DYNAMIC_OUTPUT_CONTENT.format(seconds="1.0")
            expected_headers = generate_dynamic_headers(123, r"\d+", 0, r"\d+")
            validate_response_full(response, expected_headers, expected)
            dispatches.append(round(float(response.headers["Stat-Req-Dispatch"][2:])))

        dispatches.sort()

        for i, t in enumerate(dispatches):
            assert i // threads == t
