import socket
import struct
import time

ICMP_ECHO = 8
ID = 0x0001

def checksum(data):
    if len(data) % 2:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        part = data[i] + (data[i+1] << 8)
        s += part
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff

def build_packet(seq):
    payload = b"homeassistant"
    header = struct.pack("!BBHHH", ICMP_ECHO, 0, 0, ID, seq)
    chk = checksum(header + payload)
    header = struct.pack("!BBHHH", ICMP_ECHO, 0, chk, ID, seq)
    return header + payload

def ping(host, timeout=1, count=1):
    """Ping host and return (success: bool, latency_ms: float or None)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.settimeout(timeout)
    packet = build_packet(1)

    try:
        start_time = time.time()
        sock.sendto(packet, (host, 1))
        reply, _ = sock.recvfrom(1024)
        end_time = time.time()

        icmp = reply[20:28]
        r_type, r_code, r_checksum, r_id, r_seq = struct.unpack("!BBHHH", icmp)

        if r_type == 0 and r_id == ID:
            latency_ms = round((end_time - start_time) * 1000, 2)
            return True, latency_ms

        return False, None

    except Exception:
        return False, None

    finally:
        sock.close()
