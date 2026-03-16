# Even G2 Swift SDK - Documentation

Complete documentation for the Even Realities G2 smart glasses protocol, firmware,
and iOS SDK implementation.

## Sections

### [protocols/](protocols/) - Transport & Infrastructure
Core BLE communication: packet format, service IDs, authentication, heartbeat,
Nordic UART, connection lifecycle.

### [features/](features/) - User-Facing Protocols
Application-layer features: Teleprompter, EvenAI, Navigation, Conversate, EvenHub,
brightness control, gestures, display pipeline.

### [devices/](devices/) - Hardware
Device specifications for G2 glasses, G2 case, R1 ring, and R1 cradle.

### [firmware/](firmware/) - Firmware & Reverse Engineering
Firmware update pipeline, binary analysis, per-component structure, module deep dives,
decompilation artifacts, and dated investigation logs.

### [android/](android/) - Android App Reverse Engineering
Flutter/Dart protocol internals from the Even.app APK: API endpoints, protobuf message
catalog, BLE connectivity layer, audio pipeline, API signing and security.

### [reference/](reference/) - Cross-Cutting Material
Protocol constants, magic numbers, confidence ratings, and catalog of unknowns.

### [planning/](planning/) - Development Planning
Project roadmap, active task tracking, firmware RE planning, remaining fixes.

### [build/](build/) - Build System
Mock firmware build guide (ESP32-C6/S3), Xcode project configuration.

### [opencfw/](opencfw/) - Clean-Room Custom Firmware
26 architecture documents for the openCFW custom firmware effort: hardware bundles,
transport formats, connection/identity model, lifecycle, settings, diagnostics, and
implementation roadmap. Derived entirely from the local RE corpus.

### [community-research/](community-research/) - External Protocol Research
Community BLE protocol reverse engineering (i-soxi) and EvenHub SDK documentation
(nickustinov). Preserved for attribution; our own docs now supersede most of this.

### [community-apps.md](community-apps.md) - Community App Catalog
24 open-source EvenHub apps from the community with author, description, and SDK
usage patterns.

## External Directories

These directories contain source code or working data (not documentation) and are
not duplicated here. Their documentation has been consolidated into this tree:

- **`decompiledFW/`** - Decompilation working directory with tools and raw output.
  Analysis docs mirrored under `firmware/decompilation/`.
- **`openCFW/`** - Custom firmware source code. Docs consolidated into `opencfw/`.
- **`third_party/`** - Third-party SDKs and community app source.
  Research docs consolidated into `community-research/`; app catalog in `community-apps.md`.
- **`g2-mock-firmware/`** - ESP32 mock firmware source. Build docs in `build/mock-firmware.md`.

## Quick Reference

| Topic | Go to |
|-------|-------|
| Packet format (AA header, CRC-16) | [protocols/packet-structure.md](protocols/packet-structure.md) |
| Service ID registry | [protocols/services.md](protocols/services.md) |
| Display output guide | [features/display-output-howto.md](features/display-output-howto.md) |
| EvenHub containers | [features/eventhub.md](features/eventhub.md) |
| Firmware file format (EVENOTA) | [firmware/firmware-files.md](firmware/firmware-files.md) |
| API signing algorithm | [android/api-signing.md](android/api-signing.md) |
| G2 hardware BOM | [devices/g2-glasses.md](devices/g2-glasses.md) |
| Project roadmap | [planning/roadmap.md](planning/roadmap.md) |
| Custom firmware architecture | [opencfw/README.md](opencfw/README.md) |
| Community EvenHub apps | [community-apps.md](community-apps.md) |
