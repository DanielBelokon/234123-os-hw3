from signal import SIGINT
from time import sleep
import pytest
from requests import Session, exceptions
from requests_futures.sessions import FuturesSession

from server import Server, server_port
from definitions import DYNAMIC_OUTPUT_CONTENT, SERVER_CONNECTION_OUTPUT
from utils import spawn_clients, generate_dynamic_headers, validate_out, validate_response_full, validate_response_full_with_dispatch, random_drop_formula


def test_sanity(server_port):
    with Server("./server", server_port, 1, 1, "random") as server:
        sleep(0.1)
        with FuturesSession() as session1:
            future1 = session1.get(
                f"http://localhost:{server_port}/output.cgi?1")
            sleep(0.1)
            with Session() as session2:
                with pytest.raises(exceptions.ConnectionError):
                    session2.get(
                        f"http://localhost:{server_port}/output.cgi?1")
            response = future1.result()
            expected_headers = generate_dynamic_headers(123, 1, 0, 1)
            expected = DYNAMIC_OUTPUT_CONTENT.format(
                seconds="1.0")
            validate_response_full(response, expected_headers, expected)
        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = SERVER_CONNECTION_OUTPUT.format(
            filename=r"/output.cgi\?1")
        validate_out(out, err, expected)


@pytest.mark.parametrize("threads, queue, amount",
                         [
                             (1, 2, 3),
                             (2, 4, 4),
                             (2, 4, 8),
                             (4, 4, 8),
                             (4, 8, 8),
                             (4, 8, 10),
                         ])
def test_load(threads, queue, amount, server_port):
    with Server("./server", server_port, threads, queue, "random") as server:
        sleep(0.1)
        clients = spawn_clients(amount, server_port)
        count = 0
        connections = []
        for i in range(amount):
            try:
                response = clients[i][1].result()
                clients[i][0].close()
                expected = DYNAMIC_OUTPUT_CONTENT.format(seconds=f"1.{i:0<1}")
                expected_headers = generate_dynamic_headers(123, (count // threads) + 1, 0, (count // threads) + 1)
                expected_dispatch = 0 if i < threads else (
                    1 + 0.2 * (count-threads)) - i * 0.1
                validate_response_full_with_dispatch(response, expected_headers, expected, expected_dispatch)
                count += 1
            except exceptions.ConnectionError:
                pass
        pending = queue - threads
        expected_count = queue
        for i in range(amount - queue):
            if expected_count == queue:
                expected_count = max(expected_count - random_drop_formula(queue, pending), threads)
            if expected_count != queue:
                expected_count += 1
        assert count == expected_count

        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = "^" + ''.join([SERVER_CONNECTION_OUTPUT.format(
            filename=rf"/output.cgi\?1.{i}") + r"(?:.*[\r\n]+)*" for i in connections])
        validate_out(out, err, expected)


@pytest.mark.parametrize("threads, queue, amount_before, amount_after",
                         [
                             (2, 4, 4, 4),
                             (2, 4, 8, 8),
                             (4, 4, 8, 8),
                             (4, 8, 8, 8),
                             (4, 8, 10, 10),
                         ])
def test_available_after_load(threads, queue, amount_before, amount_after, server_port):
    with Server("./server", server_port, threads, queue, "random") as server:
        sleep(0.1)
        clients = spawn_clients(amount_before, server_port)
        count_before = 0
        connections_before = []
        for i in range(amount_before):
            try:
                response = clients[i][1].result()
                clients[i][0].close()
                expected = DYNAMIC_OUTPUT_CONTENT.format(seconds=f"1.{i:0<1}")
                expected_headers = generate_dynamic_headers(
                    123, (count_before // threads) + 1, 0, (count_before // threads) + 1)
                expected_dispatch = 0 if i < threads else (
                    1 + 0.2 * (count_before-threads)) - i * 0.1
                validate_response_full_with_dispatch(response, expected_headers, expected, expected_dispatch)
                count_before += 1
            except exceptions.ConnectionError:
                pass
        pending = queue - threads
        expected_count = queue
        for i in range(amount_before - queue):
            if expected_count == queue:
                expected_count = max(expected_count - random_drop_formula(queue, pending), threads)
            if expected_count != queue:
                expected_count += 1
        assert count_before == expected_count
        clients = spawn_clients(amount_after, server_port)
        count_after = 0
        connections_after = []
        for i in range(amount_after):
            try:
                response = clients[i][1].result()
                clients[i][0].close()
                current_count = (count_before // threads) + \
                    (count_after // threads) + 1
                expected = DYNAMIC_OUTPUT_CONTENT.format(seconds=f"1.{i:0<1}")
                expected_headers = generate_dynamic_headers(123, current_count, 0, current_count)
                expected_dispatch = 0 if i < threads else (
                    1 + 0.2 * (count_after-threads)) - i * 0.1
                validate_response_full_with_dispatch(response, expected_headers, expected, expected_dispatch)
                count_after += 1
            except exceptions.ConnectionError:
                pass
        pending = queue - threads
        expected_count = queue
        for i in range(amount_before - queue):
            if expected_count == queue:
                expected_count = max(expected_count - random_drop_formula(queue, pending), threads)
            if expected_count != queue:
                expected_count += 1
        assert count_after == expected_count

        server.send_signal(SIGINT)
        out, err = server.communicate()
        expected = "^" + ''.join([SERVER_CONNECTION_OUTPUT.format(
            filename=rf"/output.cgi\?1.{i}") + r"(?:.*[\r\n]+)*" for i in connections_before]
            +
            [SERVER_CONNECTION_OUTPUT.format(
                filename=rf"/output.cgi\?1.{i}") + r"(?:.*[\r\n]+)*" for i in connections_after])
        validate_out(out, err, expected)
