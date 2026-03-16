# G2 Mock Firmware - Build Guide

The mock firmware runs on ESP32 development boards, simulating the G2 glasses' BLE
protocol for development and testing without physical glasses. Source code is in
`g2-mock-firmware/` at the repository root.

## Supported Boards

| Board | Environment | CPU | BLE | LED GPIO |
|-------|------------|-----|-----|----------|
| ESP32-S3-DevKitC-1 | `esp32s3` | Xtensa dual-core 240 MHz | BLE 5.0 | GPIO 48 (WS2812) |
| Waveshare ESP32-C6-Touch-LCD-1.47-M | `esp32c6` | RISC-V single-core 160 MHz | BLE 5.3 | GPIO 8 (WS2812) |

## Prerequisites

### Python 3.9+

PlatformIO requires Python 3.9 or later.

**macOS:**
```bash
# Python ships with Xcode command line tools, or install via Homebrew:
brew install python
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3 python3-pip
```

**Windows:**

Download and install from [python.org](https://www.python.org/downloads/). Check "Add Python to PATH" during installation.

### PlatformIO Core (CLI)

**All platforms:**
```bash
pip install platformio
```

Verify the installation:
```bash
pio --version
```

If `pio` is not found after install, the binary may be in a user-local path. Common locations:

- **macOS:** `~/Library/Python/3.x/bin/pio`
- **Linux:** `~/.local/bin/pio`
- **Windows:** `%APPDATA%\Python\Python3x\Scripts\pio.exe`

Add the appropriate directory to your shell's `PATH`, or invoke with the full path.

### USB Serial Drivers

Most boards work out-of-the-box on modern operating systems. If your board is not detected:

**ESP32-S3-DevKitC-1:** Uses native USB CDC. No driver needed on macOS/Linux. On Windows, install the [Espressif USB driver](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/establish-serial-connection.html) if the device doesn't appear.

**ESP32-C6-Touch-LCD-1.47-M:** Uses a CH343 USB-UART bridge. Install the [WCH CH343 driver](https://www.wch.cn/downloads/CH343SER_EXE.html) if the board isn't recognized. On macOS, the driver is typically not needed with macOS 12+.

## Building

All commands are run from the `g2-mock-firmware/` directory.

### Build Only (no upload)

```bash
# ESP32-S3
pio run -e esp32s3

# ESP32-C6
pio run -e esp32c6
```

### Build and Flash

Connect the board via USB, then:

```bash
# ESP32-S3
pio run -e esp32s3 -t upload

# ESP32-C6
pio run -e esp32c6 -t upload
```

If PlatformIO can't auto-detect the serial port, specify it manually:

```bash
pio run -e esp32s3 -t upload --upload-port /dev/ttyACM0      # Linux
pio run -e esp32s3 -t upload --upload-port /dev/cu.usbmodem*  # macOS
pio run -e esp32c6 -t upload --upload-port COM3               # Windows
```

### Serial Monitor

```bash
pio device monitor -b 115200
```

Type `help` in the serial console to see all available commands.

To build, flash, and immediately open the monitor:

```bash
pio run -e esp32s3 -t upload && pio device monitor -b 115200
```

### Clean Build

```bash
pio run -e esp32s3 -t clean
pio run -e esp32c6 -t clean
```

## First Build

On the first build, PlatformIO will automatically download and install:

- **pioarduino platform** (Arduino 3.3.7 / ESP-IDF 5.5.2) - provides ESP32-C6 Arduino support
- **Xtensa toolchain** (for S3) or **RISC-V toolchain** (for C6)
- **NimBLE-Arduino 2.3.x** - BLE stack with C6/H2/C2/C5 support
- **Adafruit NeoPixel** - WS2812 RGB LED driver

This takes a few minutes on the first run. Subsequent builds use the cached toolchains.

## Troubleshooting

### "pio: command not found"

PlatformIO installed to a user-local bin directory not in your PATH. Either:

```bash
# Add to PATH (add to your .bashrc/.zshrc for persistence)
export PATH="$PATH:$HOME/.local/bin"            # Linux
export PATH="$PATH:$HOME/Library/Python/3.x/bin" # macOS (replace 3.x with your version)

# Or invoke directly
python3 -m platformio run -e esp32s3
```

### "This board doesn't support arduino framework!"

You're using the official `espressif32` platform instead of pioarduino. The `platformio.ini` in this repo is preconfigured to use pioarduino. If you've overridden the platform, revert to the repository version.

### Upload fails / no serial port detected

1. Check the USB cable supports data (not charge-only).
2. Install the appropriate USB driver (see Prerequisites above).
3. List available ports: `pio device list`
4. On Linux, add your user to the `dialout` group: `sudo usermod -aG dialout $USER` (then log out and back in).

### ESP32-S3 boot loop after flash

The S3 DevKitC-1 uses USB CDC for serial. If the board enters a boot loop, hold the **BOOT** button while pressing **RST** to enter download mode, then flash again.

### ESP32-C6 higher flash usage

The C6 binary uses ~57% of flash vs ~19% on S3. This is normal - the C6 board definition defaults to a smaller partition scheme. The firmware fits comfortably within the available space.

## Capabilities

The mock firmware emulates the full G2 glasses BLE protocol:
- 3 BLE instances (left eye, right eye, case)
- Full auth handshake + heartbeat
- Teleprompter, Conversate, EvenAI, EvenHub display simulation
- File transfer, device info, gestures via NUS
- R1 Ring simulation
- Serial console for gesture injection and brightness control

## Capabilities

The mock firmware emulates the full G2 glasses BLE protocol:
- 3 BLE instances (left eye, right eye, case)
- Full auth handshake + heartbeat
- Teleprompter, Conversate, EvenAI, EvenHub display simulation
- File transfer, device info, gestures via NUS
- R1 Ring simulation
- Serial console for gesture injection and brightness control
