# GC-6612Pro Ping for Home Assistant

GC-6612Pro Ping is a small Home Assistant custom integration that performs ICMP ping checks (via raw sockets) and exposes reachability as a binary sensor with an optional `latency_ms` attribute.

---

## 🔧 Installation

There are two common ways to install this integration:

1) HACS (recommended)

- Add this repository to your HACS custom repositories (Category: Integration) or install it directly if it is already listed.
- Restart Home Assistant.
- Go to Settings → Devices & Services → Add Integration → search for **GC-6612Pro Ping**.

2) Manual install

- Copy the `custom_components/ping_custom` folder into your Home Assistant `config/custom_components/` directory.
- Restart Home Assistant.
- Go to Settings → Devices & Services → Add Integration → search for **GC-6612Pro Ping**.

---

## ⚙️ Configuration

- When adding the integration, provide the host (IP address or hostname) you want to monitor. Optionally set a friendly name.
- In the options you can set the `ping_count` (number of pings per check).

The integration creates a binary sensor entity with unique id `<entry_id>_<host>` and an extra attribute `latency_ms` when reachable.

---

## 🧪 Notes about tests

The test suite uses a development testing environment and may require additional build tools on macOS (some dependencies like `lru-dict` may need a C compiler available). If you see build errors when running `pip install -r requirements.test.txt`, ensure Xcode command line tools are installed (`xcode-select --install`).

---

## 📄 License & Contributing

- License: MIT (see `LICENSE` in the repo or add license file if missing).
- Contributions: open an issue or a PR on the repository.

---

## 📦 Changelog

See `CHANGELOG.md` for details about releases.


## Installation
