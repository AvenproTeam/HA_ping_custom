"""Test the GC-6612Pro compatible ping."""

import socket
import struct
from unittest.mock import patch

import pytest

from custom_components.gc6612pro_ping import ping_util
from custom_components.gc6612pro_ping.ping_util import (
    HostLookupError,
    build_packet,
    is_reply,
    ping,
)

# Exact bytes sent by the original ping_util.py (v1.0.x). The checksum bytes
# (0x6904) are swapped compared with RFC 1071 on purpose: keep them.
ORIGINAL_PACKET = bytes.fromhex("0800690400010001686f6d65617373697374616e74")

DEVICE = "192.168.1.50"


def ip_header(src: str, ihl_words: int = 5) -> bytes:
    """Minimal IPv4 header; only version/IHL and source address matter."""
    header = bytearray(ihl_words * 4)
    header[0] = 0x40 | ihl_words
    header[12:16] = socket.inet_aton(src)
    return bytes(header)


def echo_reply(src: str, icmp_id: int = 1, icmp_type: int = 0, ihl: int = 5) -> bytes:
    """Build an IP packet carrying an ICMP message."""
    icmp = struct.pack("!BBHHH", icmp_type, 0, 0, icmp_id, 1) + b"homeassistant"
    return ip_header(src, ihl) + icmp


class FakeSocket:
    """Raw socket double that replays queued packets."""

    def __init__(self, replies: list[tuple[bytes, str]]) -> None:
        self.replies = list(replies)
        self.sent: list[tuple[bytes, tuple]] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def settimeout(self, value):
        pass

    def sendto(self, data, addr):
        self.sent.append((data, addr))

    def recvfrom(self, size):
        if not self.replies:
            raise TimeoutError
        packet, src = self.replies.pop(0)
        return packet, (src, 0)


@pytest.fixture
def fake_socket():
    """Patch socket creation and DNS in ping_util."""

    def install(replies):
        sock = FakeSocket(replies)
        patch.object(ping_util.socket, "socket", return_value=sock).start()
        patch.object(ping_util.socket, "gethostbyname", return_value=DEVICE).start()
        patch.object(ping_util.time, "sleep").start()
        return sock

    yield install
    patch.stopall()


def test_packet_is_identical_to_original() -> None:
    """The echo request must not change: the device depends on it."""
    assert build_packet() == ORIGINAL_PACKET


def test_is_reply_filters() -> None:
    """Only echo replies from the device with ID 1 count."""
    assert is_reply(echo_reply(DEVICE), DEVICE, DEVICE)
    assert is_reply(echo_reply(DEVICE, ihl=6), DEVICE, DEVICE)  # IP options
    assert not is_reply(echo_reply("10.0.0.9"), "10.0.0.9", DEVICE)
    assert not is_reply(echo_reply(DEVICE, icmp_id=2), DEVICE, DEVICE)
    assert not is_reply(echo_reply(DEVICE, icmp_type=8), DEVICE, DEVICE)
    assert not is_reply(b"\x45", DEVICE, DEVICE)


def test_ping_sends_original_packet_count_times(fake_socket) -> None:
    """Each request uses the original packet and other traffic is skipped."""
    sock = fake_socket(
        [
            (echo_reply("10.0.0.9"), "10.0.0.9"),  # someone else's reply
            (echo_reply(DEVICE), DEVICE),
            (echo_reply(DEVICE, icmp_type=8), DEVICE),  # our own request
            (echo_reply(DEVICE), DEVICE),
        ]
    )
    stats = ping("device.local", count=3, timeout=0.5, interval=0)

    assert [data for data, _ in sock.sent] == [ORIGINAL_PACKET] * 3
    assert all(addr == (DEVICE, 1) for _, addr in sock.sent)
    assert stats.address == DEVICE
    assert stats.sent == 3
    assert len(stats.rtts) == 2


def test_ping_no_reply(fake_socket) -> None:
    """Timeouts are lost packets, not errors."""
    fake_socket([])
    stats = ping(DEVICE, count=2, timeout=0.1, interval=0)
    assert stats.rtts == []
    assert stats.sent == 2


def test_ping_unresolvable_host() -> None:
    """DNS failures raise HostLookupError."""
    with (
        patch.object(
            ping_util.socket, "gethostbyname", side_effect=socket.gaierror("nope")
        ),
        pytest.raises(HostLookupError),
    ):
        ping("nope.invalid")
