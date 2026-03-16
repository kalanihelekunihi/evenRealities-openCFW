# Protocols - Transport & Infrastructure

Core BLE communication protocols for the Even G2 glasses.

| Document | Description |
|----------|-------------|
| [overview.md](overview.md) | High-level protocol stack overview, 3 BLE lanes, document index |
| [packet-structure.md](packet-structure.md) | G2 packet format (AA header), CRC-16, multi-packet fragmentation |
| [ble-uuids.md](ble-uuids.md) | BLE service/characteristic UUIDs, ATT handles, base UUID |
| [services.md](services.md) | Complete 2-byte service ID registry (0x80-xx through 0xE0-xx) |
| [all-services-detailed.md](all-services-detailed.md) | Detailed breakdown of all service handlers |
| [complete-service-reference.md](complete-service-reference.md) | Comprehensive service reference with firmware handler mappings |
| [authentication.md](authentication.md) | Auth handshake - fast 3-packet and full 7-packet sequences |
| [heartbeat.md](heartbeat.md) | Type-14 keepalive protocol and sync mechanism |
| [connection-lifecycle.md](connection-lifecycle.md) | BLE connection flow, error classification, reconnection logic |
| [nus-protocol.md](nus-protocol.md) | Nordic UART Service - simple commands, mic control, text display, audio streaming |
| [notification.md](notification.md) | Push notification file transfer (0xC4/0xC5), CRC32C checksum, JSON payload format |
