# GC-6612Pro Ping for Home Assistant

GC-6612Pro Ping is a Home Assistant custom integration that checks whether a host answers ICMP ping and exposes the result as a connectivity binary sensor, plus latency and packet-loss sensors.

---

## 🔧 Installation

1) HACS (recommended)

- Add this repository to your HACS custom repositories (Category: Integration).
- Install **GC-6612Pro Ping** and restart Home Assistant.
- Go to Settings → Devices & Services → Add Integration → search for **GC-6612Pro Ping**.

2) Manual install

- Copy the `custom_components/gc6612pro_ping` folder into your Home Assistant `config/custom_components/` directory.
- Restart Home Assistant.
- Go to Settings → Devices & Services → Add Integration → search for **GC-6612Pro Ping**.

Requires Home Assistant 2025.8 or newer.

---

## ⚙️ Configuration

- **Host**: IP address or hostname to monitor. **Name** is optional (defaults to the host).
- To change the host later use **Reconfigure** on the integration entry.
- **Options**:
  - `ping_count` — echo requests per check (1–20, default 3). The host is reachable if at least one reply arrives.
  - `scan_interval` — seconds between checks (5–3600, default 30).

Each host becomes a device with these entities:

| Entity | Description |
| --- | --- |
| `binary_sensor.<name>` | On when the host answers. Attributes: `ip_address`, `latency_ms`, `latency_min_ms`, `latency_max_ms`, `packet_loss`. |
| `sensor.<name>_latency` | Average round-trip time in ms (long-term statistics). |
| `sensor.<name>_packet_loss` | Packet loss in % (diagnostic). |

The GC-6612Pro does not answer standard pings, so the integration sends its own ICMP echo request (`ping_util.py`): ID `0x0001`, sequence `1`, payload `homeassistant` and a checksum with its bytes swapped compared with the standard. **Do not replace it with a standard ping library.** It needs raw sockets, so Home Assistant must run as root (Home Assistant OS and the official container do). Hostnames are resolved to IPv4.

---

## ⚠️ Upgrading from 1.0.x

The integration domain changed from `GC-6612Pro_Ping` (not a valid Home Assistant domain, which caused the "Invalid handler specified" errors) to `gc6612pro_ping`. Delete the old `custom_components/GC-6612Pro-Ping` and `custom_components/ping_custom` folders and any old entries, restart, and add the hosts again.

---

## 🧪 Tests

```bash
pip install -r requirements.test.txt
pytest
```

---

## 📦 Changelog

See `CHANGELOG.md`.
