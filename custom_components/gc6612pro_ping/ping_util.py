"""Custom ICMP echo for the GC-6612Pro.

The device does not answer standard pings. The packet below must stay
byte-for-byte identical to the original implementation:

- ICMP echo request, ID 0x0001, sequence 1, payload b"homeassistant".
- The checksum is summed as little-endian words and then packed big-endian,
  so its two bytes are swapped compared with RFC 1071. Do not "fix" it.

Raw sockets are required (Home Assistant OS runs as root). Unprivileged
datagram ICMP sockets are not an option: the kernel rewrites the ICMP ID.
"""

from __future__ import annotations

import socket
import struct
import time
from dataclasses import dataclass, field

ICMP_ECHO = 8
ICMP_ECHO_REPLY = 0
ID = 0x0001
SEQUENCE = 1
PAYLOAD = b"homeassistant"


class HostLookupError(Exception):
    """The hostname could not be resolved."""


@dataclass
class PingStats:
    """Outcome of one round of echo requests."""

    address: str
    sent: int
    rtts: list[float] = field(default_factory=list)  # milliseconds


def checksum(data: bytes) -> int:
    """Checksum exactly as the original firmware-compatible implementation."""
    if len(data) % 2:
        data += b"\x00"
    s = 0
    for i in range(0, len(data), 2):
        part = data[i] + (data[i + 1] << 8)
        s += part
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


def build_packet(seq: int = SEQUENCE) -> bytes:
    """Build the echo request packet."""
    header = struct.pack("!BBHHH", ICMP_ECHO, 0, 0, ID, seq)
    chk = checksum(header + PAYLOAD)
    header = struct.pack("!BBHHH", ICMP_ECHO, 0, chk, ID, seq)
    return header + PAYLOAD


def is_reply(packet: bytes, src: str, address: str) -> bool:
    """Return True if packet is an echo reply from address with our ID."""
    if src != address or len(packet) < 1:
        return False
    ihl = (packet[0] & 0x0F) * 4
    if len(packet) < ihl + 8:
        return False
    r_type, _code, _chk, r_id, _seq = struct.unpack("!BBHHH", packet[ihl : ihl + 8])
    return r_type == ICMP_ECHO_REPLY and r_id == ID


def resolve(host: str) -> str:
    """Resolve host to an IPv4 address."""
    try:
        return socket.gethostbyname(host)
    except (socket.gaierror, UnicodeError) as err:
        raise HostLookupError(host) from err


def ping(
    host: str, count: int = 1, timeout: float = 2, interval: float = 0.2
) -> PingStats:
    """Send count echo requests to host and collect round-trip times.

    Blocking: run it in an executor. Raises PermissionError if raw sockets
    are not allowed and HostLookupError if the host cannot be resolved.
    """
    address = resolve(host)
    packet = build_packet()
    stats = PingStats(address=address, sent=count)

    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
        for i in range(count):
            if i:
                time.sleep(interval)
            start = time.perf_counter()
            deadline = start + timeout
            try:
                sock.sendto(packet, (address, 1))
                while (remaining := deadline - time.perf_counter()) > 0:
                    sock.settimeout(remaining)
                    reply, (src, *_) = sock.recvfrom(1024)
                    if is_reply(reply, src, address):
                        stats.rtts.append((time.perf_counter() - start) * 1000)
                        break
            except TimeoutError:
                pass
            except OSError:
                # e.g. "network unreachable": count as a lost packet.
                pass

    return stats
