# R1 application-bundle dependency boundary

## What the current bundle proves

The Nordic SDK target links the openR1 application from C/assembly source files and compiler
runtime libraries. Its source lists do not consume a stock application, bootloader, SoftDevice,
vendor algorithm archive, or other firmware blob. The owner DFU packager writes exactly three ZIP
members:

- `application.bin`, copied from the locally linked application;
- `application.dat`, the owner-signed Nordic init packet; and
- `manifest.json`, containing only the `application` entry.

The linker now retains every reconstructed module in `.openr1_reconstructed_code`, including the
Goodix, GoMore, shared-runtime, peripheral, middleware, and generated-model objects. This prevents
`--gc-sections` from silently turning “compiles from source” into “absent from the firmware.”
`tools/verify_sdk_image.py` checks all reconstructed object families, representative symbols, the
vector table, flash bounds, exact image length, and GCC-9.3.1 image hashes.

## Remaining opaque runtime boundary of this legacy target

This is an **application-only** DFU bundle, not yet a fully self-contained open device stack. The
application starts at `0x00027000`, calls Nordic SVC interfaces, and declares SoftDevice requirement
`0x0100` (S140 7.2.0). It therefore requires a compatible S140 already installed on the ring. The
ZIP does not copy or redistribute that SoftDevice, and it does not include or replace the installed
secure bootloader.

Consequently, the bundle itself contains no opaque firmware member, but running it still depends on
an opaque preinstalled BLE stack and boot/update environment. The project must replace the S140
calls with a source-built BLE/controller stack and provide a source-built installation/boot path
before claiming a fully opaque-free complete-device firmware bundle.

That blocker is now closed by the separate source-built Zephyr/MCUboot target.
It does not change the dependency boundary of this Nordic SDK application-only
archive: this archive still requires S140 and the retail bootloader. The
alternate target builds its Bluetooth host/controller and boot path from pinned
source and emits a canonical full-flash image; see
[`SOURCE-BUILT-ZEPHYR-BUNDLE.md`](SOURCE-BUILT-ZEPHYR-BUNDLE.md). Its remaining
gaps are typed hardware/provider adapters and owned-ring validation rather than
opaque BLE or boot firmware.

## Reproduction

```sh
python3 tools/verify_application_bundle_boundary.py
python3 tools/verify_zephyr_source_boundary.py
python3 tools/verify_sdk_image.py
python3 -m unittest tests/test_sign_r1_firmware.py
```
