# Features - User-Facing Protocols

Application-layer feature protocols built on the G2 packet format.

## Feature Protocols

| Document | Service ID | Description |
|----------|------------|-------------|
| [teleprompter.md](teleprompter.md) | 0x06-20 | Scrolling text display with progress callbacks |
| [even-ai.md](even-ai.md) | 0x07-20 | AI assistant Q&A display (12 command types) |
| [navigation.md](navigation.md) | 0x08-20 | Turn-by-turn navigation with 36 icon types |
| [conversate.md](conversate.md) | 0x0B-20 | Real-time ASR speech transcription |
| [eventhub.md](eventhub.md) | 0xE0-20 | EvenHub container layouts (own LVGL UI, no displayConfig needed) |
| [brightness.md](brightness.md) | 0x0D-00 | Brightness control via G2SettingPackage protobuf |
| [gestures.md](gestures.md) | 0x01-01 / 0x0D-01 | Touch gesture events (G2-layer + NUS + R1 Ring) |

## Display System

| Document | Description |
|----------|-------------|
| [display-pipeline.md](display-pipeline.md) | Display lifecycle, mode transitions, codec ownership model |
| [display-output-howto.md](display-output-howto.md) | Practical guide: getting content onto G2 displays, per-feature patterns |
| [display-viewport.md](display-viewport.md) | Two-layer display offset system: GPU framebuffer (640x480) vs visible viewport (576x288) |
