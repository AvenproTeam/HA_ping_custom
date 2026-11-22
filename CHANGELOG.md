# Changelog

## [1.1.1] - 2026-11-22

### Fixed
- Restore the original GC-6612Pro compatible ping. Version 1.1.0 replaced it with `icmplib`, which sends standard ICMP packets the device does not answer, so it always showed as disconnected. The echo request is again byte-for-byte identical to 1.0.x (ID `0x0001`, sequence 1, payload `homeassistant`, swapped checksum bytes), now with:
  - `ping_count` honoured (N identical requests).
  - Only echo replies from the device IP with ID 1 accepted; other ICMP traffic ignored, IP header length read instead of assumed.
  - Hostnames resolved before sending.
- Removed the `icmplib` requirement.

### Added
- Integration icon (light and dark variants) in `brand/`, shown by Home Assistant 2026.x for custom integrations. Sources in `assets/`.
- Test asserting the sent packet matches the original bytes.

## [1.1.0] - 2026-11-22

### Breaking
- Domain renamed from `GC-6612Pro_Ping` to `gc6612pro_ping` and folder to `custom_components/gc6612pro_ping`. The old domain was invalid (uppercase and hyphen, folder name mismatch), which is the root cause of the "Invalid handler specified" errors. Existing entries must be added again.

### Added
- Latency (ms) and packet loss (%) sensors, grouped under one device per host.
- `scan_interval` option (default 30 s) and reconfigure step to change the host.
- English, Spanish and Catalan translations.
- Tests for setup, entities, config, options and reconfigure flows.

### Changed
- Ping is done with `icmplib` through a `DataUpdateCoordinator`: honours `ping_count`, supports hostnames and IPv6, matches replies correctly when several hosts are pinged at once, and falls back to unprivileged ICMP when raw sockets are not allowed.
- Hostname lookup failures report the host as offline instead of raising.
- Binary sensor attributes now include `ip_address`, `latency_min_ms`, `latency_max_ms` and `packet_loss`.

### Fixed
- Changing the host in options had no effect (the sensor only read the original host).
- `ping_count` was stored as a float and ignored by the ping routine.
- Empty host validation never aborted (missing `return`).

### Removed
- Leftover `custom_components/ping_custom/manifest.json`, stray root `__init__.py` and tracked `.DS_Store` files.

## [1.0.6] - 2026-01-01

### Release
- Bump version to 1.0.6.

## [1.0.5] - 2026-01-01

### Fixed
- Fix options flow handler initialization and manifest domain to resolve config flow load errors ("Invalid handler specified" / missing module import).

## [1.0.4] - 2026-01-01

### Release
- Publish v1.0.4 release.
- Updated README file.
- Fix "Invalid handler specified" error.

## [1.0.3] - 2026-01-01

### Changed
- Rename integration display name to **GC-6612Pro Ping** (`manifest.json` and `hacs.json`).

## [1.0.2] - 2026-01-01

### Release
- Bump version to 1.0.2.

## [1.0.1] - 2026-01-01

### Fixed
- Fix config flow to properly store `host` in the entry `data` and provide a default `ping_count` option.
- Add missing constants `CONF_PING_COUNT` and `DEFAULT_PING_COUNT`.

### Misc
- Bumped `manifest.json` version to `1.0.1`.
