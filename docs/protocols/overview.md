# Even Realities G2 & R1 Protocol Overview

This document provides a high-level overview of the Even Realities G2 smart glasses and R1 ring BLE protocol stack. Each section links to a dedicated document with full details.

## Architecture

The G2 glasses expose three BLE communication layers:

```
┌─────────────────────────────────────────────────┐
│                 Phone / Host                    │
├──────────┬──────────┬───────────┬───────────────┤
│ Control  │  File    │ Display   │     NUS       │
│ 0x5401/02│ 0x7401/02│ 0x6402    │ 6E400002/03   │
├──────────┴──────────┴───────────┼───────────────┤
│  G2 Packet Protocol (AA 21/12)  │ Simple 1-2    │
│  Protobuf payloads, CRC-16      │ byte commands │
├─────────────────────────────────┴───────────────┤
│              BLE (MTU 512)                      │
└─────────────────────────────────────────────────┘
          │
     R1 Ring ──── BAE80001 service ──── Gesture bridge
```

### G2 Packet Protocol (Primary)

All feature communication uses the G2 packet format with an 8-byte header, protobuf-encoded payload, and CRC-16 trailer. Commands flow on 0x5401 (write) and responses arrive on 0x5402 (notify).

- **Packet format**: `[AA] [type] [seq] [len] [total] [num] [svc_hi] [svc_lo] [payload] [crc_lo] [crc_hi]`
- **Command type**: `0x21` (phone -> glasses)
- **Response type**: `0x12` (glasses -> phone)
- **CRC**: CRC-16/CCITT (init 0xFFFF, poly 0x1021), over payload bytes only

See [packet-structure.md](protocols/packet-structure.md) for full details.

### Nordic UART Service (Secondary)

A parallel communication channel using simple 1-2 byte commands with no packet envelope. Used for gestures, microphone control, text display, BMP images, and audio streaming.

See [nus-protocol.md](protocols/nus-protocol.md) for full details.

### R1 Ring (Gesture Bridge)

The Even R1 ring connects to both the phone and the G2 glasses simultaneously. Ring gestures are decoded on the phone and forwarded to the glasses via NUS commands.

See [r1-ring.md](devices/r1-ring.md) for full details.

### Firmware Update Surfaces

Firmware handling spans two layers:

- **Device DFU mode**: Nordic DFU service exposure (FE59/legacy UUIDs) when glasses are in update bootloader mode.
- **Cloud + OTA pipeline**: app checks backend firmware endpoints (`/v2/g/check_firmware`, `/v2/g/check_latest_firmware`) and then performs staged file/OTA transfer over G2 services.

See [firmware-updates.md](firmware/firmware-updates.md) and [firmware-reverse-engineering.md](firmware/firmware-reverse-engineering.md).

## Service ID Convention

G2 service IDs are 2 bytes in the packet header (bytes 6-7). They follow a pattern:

| Low Byte | Direction | Purpose |
|----------|-----------|---------|
| `0x20`   | Phone -> Glasses | Command / data payload |
| `0x00`   | Glasses -> Phone | Response / query result |
| `0x01`   | Glasses -> Phone | Specific response type (e.g. auth success) |
| `0x02`   | Glasses -> Phone | Transport ACK |

See [services.md](protocols/services.md) for the complete service ID reference.

## Connection Lifecycle

1. **Scan** — find glasses by name prefix (`Even G2_`) or saved peripheral UUID
2. **Connect** — establish BLE connection, negotiate MTU (512)
3. **Discover services** — enumerate characteristics on control, file, display channels
4. **Authenticate** — 3 or 7 packet handshake on services 0x80-00/0x80-20
5. **Feature use** — send commands, receive responses
6. **Disconnect** — clean up, optionally save peripheral UUIDs for quick reconnect

If FE59 is advertised instead of normal G2 services, treat the device as already in DFU/upgrade mode (not a normal runtime session).

See [connection-lifecycle.md](protocols/connection-lifecycle.md) for error handling and reconnection behavior.

## Protocol Documentation Index

### Protocols — Transport & Infrastructure (`protocols/`)
| Document | Description |
|----------|-------------|
| [packet-structure.md](protocols/packet-structure.md) | G2 packet format, CRC, multi-packet fragmentation, decoder tool |
| [ble-uuids.md](protocols/ble-uuids.md) | BLE service/characteristic UUIDs, ATT handles |
| [services.md](protocols/services.md) | Complete service ID reference |
| [authentication.md](protocols/authentication.md) | Auth handshake (fast 3-pkt / full 7-pkt) |
| [heartbeat.md](protocols/heartbeat.md) | Keepalive protocol and sync |
| [connection-lifecycle.md](protocols/connection-lifecycle.md) | BLE connection flow, error handling, reconnection |
| [nus-protocol.md](protocols/nus-protocol.md) | Nordic UART: simple commands, mic, audio |
| [notification.md](protocols/notification.md) | Push notification file transfer (0xC4/0xC5, CRC32C, JSON) |

### Features — User-Facing Protocols (`features/`)
| Document | Service ID | Description |
|----------|------------|-------------|
| [teleprompter.md](features/teleprompter.md) | 0x06-20 | Scrolling text display |
| [even-ai.md](features/even-ai.md) | 0x07-20 | AI assistant Q&A display |
| [navigation.md](features/navigation.md) | 0x08-20 | Turn-by-turn navigation |
| [conversate.md](features/conversate.md) | 0x0B-20 | Real-time speech transcription |
| [eventhub.md](features/eventhub.md) | 0xE0-20 | EvenHub container display layouts |
| [brightness.md](features/brightness.md) | 0x0D-00 | Brightness control (G2SettingPackage protobuf) |
| [gestures.md](features/gestures.md) | 0x01-01 / 0x0D-01 | Touch gesture events |

### Devices — Hardware Specifications (`devices/`)
| Document | Device | Description |
|----------|--------|-------------|
| [g2-glasses.md](devices/g2-glasses.md) | G2 Glasses | Apollo510b SoC, hardware BOM, display, BLE, inter-eye architecture |
| [g2-case.md](devices/g2-case.md) | G2 Case | STM32-like ARM MCU, wired link via G2, battery/charging |
| [r1-ring.md](devices/r1-ring.md) | R1 Ring | Nordic nRF5x, dual-BLE, gesture forwarding, health sensors, MCUboot DFU |
| [r1-cradle.md](devices/r1-cradle.md) | R1 Cradle | Passive charging accessory (no MCU, no BLE) |

### Firmware & Reverse Engineering (`firmware/`)
| Document | Description |
|----------|-------------|
| [firmware-files.md](firmware/firmware-files.md) | **Start here** — device-to-hardware mapping, EVENOTA format, flash layouts, BLE transfer protocols |
| [firmware-updates.md](firmware/firmware-updates.md) | Firmware check APIs, OTA download, EVENOTA format, file command vocabulary |
| [firmware-reverse-engineering.md](firmware/firmware-reverse-engineering.md) | Full firmware binary analysis, hardware BOM (Apollo510b + EM9305), SoC identification |
| [even-app-reverse-engineering.md](firmware/even-app-reverse-engineering.md) | Even.app static RE, DFU bootloader analysis, audio/AI pipeline, Dart protocol internals |
| [s200-firmware-ota.md](firmware/s200-firmware-ota.md) | Apollo510b main application binary — preamble, flash map, software stack |
| [s200-bootloader.md](firmware/s200-bootloader.md) | Apollo510b bootloader — vector table, VTOR handoff, boot decision |
| [ble-em9305.md](firmware/ble-em9305.md) | EM9305 BLE radio patch — segmented format, 4 records, HCI flashing |
| [codec-gx8002b.md](firmware/codec-gx8002b.md) | GX8002B audio codec — FWPK dual-segment, BINH boot images |
| [touch-cy8c4046fni.md](firmware/touch-cy8c4046fni.md) | CY8C4046FNI touch controller — FWPK + CRC32C, I2C DFU |
| [box-case-mcu.md](firmware/box-case-mcu.md) | G2 case MCU — EVEN wrapper, BE checksum, wired relay update |

### Reference (`reference/`)
| Document | Description |
|----------|-------------|
| [magic-numbers.md](reference/magic-numbers.md) | All protocol constants with confidence ratings |
| [unidentified-behaviors.md](reference/unidentified-behaviors.md) | Catalog of protocol unknowns and investigation priorities |

## Device Specifications

| Property | Value |
|----------|-------|
| Model | S200 |
| Display | 576 × 288 px, green micro-LED, 4-bit greyscale (16 levels) |
| BLE MTU | 512 bytes (247 effective after ATT overhead) |
| Naming | `Even G2_XX_L_YYYYYY` / `Even G2_XX_R_YYYYYY` |
| Auth | Application-level (no BLE pairing required) |
| Battery service (0x180F) | Not present on G2 |
| Device info (0x180A) | Present — serial, firmware, hardware, model |
