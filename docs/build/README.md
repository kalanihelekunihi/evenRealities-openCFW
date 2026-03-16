# Build System

Build instructions and configuration for the project's compiled artifacts.

## Guides

| Document | Description |
|----------|-------------|
| [mock-firmware.md](mock-firmware.md) | ESP32-C6/S3 mock firmware: prerequisites, build, flash, troubleshoot |

## Other Build Targets

- **iOS app**: Open `EvenG2Shortcuts.xcodeproj` in Xcode 16+, select the `EvenG2Shortcuts`
  scheme, and build for a physical iOS device (`generic/platform=iOS`).
- **Firmware tools**: Python scripts in `tools/` have no build step (run directly with Python 3.9+).
