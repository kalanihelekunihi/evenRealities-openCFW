# R1 smart ring firmware

The target is the stock R1 application `2.2.6.0009`, together with its Secure
DFU bootloader and UICR, on a Nordic nRF52840 with the S140 7.2.0 SoftDevice.
The goal is C source that compiles, with the original toolchain, into images
byte-identical to those pinned in
[`blobs/official/2.2.6.0009/PROVENANCE.md`](blobs/official/2.2.6.0009/PROVENANCE.md).
The phased plan is in [`../docs/roadmap.md`](../docs/roadmap.md).

| Fact | Value | Where |
| --- | --- | --- |
| SDK | nRF5 SDK 17.1.0 (`ddde560`), S140 7.2.0 | [`docs/toolchain-and-dependencies.md`](docs/toolchain-and-dependencies.md) |
| RTOS | FreeRTOS-Kernel 10.5.1 with the Nordic nRF52 port, CMSIS-FreeRTOS 10.5.1 | same |
| Compiler | Arm Compiler 5 (armcc/armlink; `__main`, `__scatterload`) | same |
| Functions | 2,687 application + 285 bootloader, all classified by provider | [`docs/reference/FUNCTION-OWNERSHIP.md`](docs/reference/FUNCTION-OWNERSHIP.md) |
| Memory map | app `0x27000`, FDS `0xD1000`, FAL `0xD4000`, bootloader `0xF8000` | [`docs/memory-map.md`](docs/memory-map.md) |
| Hardware | TWIM/soft-TWI buses, sensors, PMIC, NFC charging | [`docs/hardware-pinout.md`](docs/hardware-pinout.md), [`../docs/hardware/r1-ring.md`](../docs/hardware/r1-ring.md) |

## Layout

```
r1/
├── Makefile               test, verify, oracle, vendor-audit, Ghidra runs
├── blobs/official/        versioned firmware mirrors; local image captures
│                          remain ignored
├── config-recovered/      sdk_config.h, FreeRTOSConfig.h, linker, FAL/FDB and
│                          bootloader configuration seeds, stock-proven vs guessed
├── docs/                  memory map, protocol, storage formats, pinout,
│                          toolchain, security; correlation/, boundaries/,
│                          closures/, reference/ (function ownership, BSim)
├── reconstructed/         reference pseudocode for binary-only vendor libraries
│                          (GoMore, Goodix algorithms, GXT310, QMA6100, YHM2710,
│                          unidentified frameworks); not byte-matched, not built
├── research/
│   ├── decompilation/     whole-image Ghidra export for application and
│   │                      bootloader, plus the exact-byte image oracle in rebuild/
│   ├── bootloader-reconstruction/  named bootloader export, SDK overlay, write-ups
│   └── source-correlation/ BSim runs against symbol-bearing SDK references
└── tools/                 Ghidra export/verify scripts and headless drivers
```

## Commands

```sh
make -C r1 test            # structural check of the tracked decompilation corpus
make -C r1 verify          # plus the exact-byte image oracle (needs official images)
make -C r1 vendor-audit SDK_ROOT=... FLASHDB_ROOT=...   # see third-party/fetched/
```

## History

The earlier clean-room "openR1" reimplementation, with its Zephyr, signing,
probe and iOS tooling, was removed on 2026-09-29. It deliberately did not
reproduce stock bytes. Its protocol, storage and configuration knowledge was
consolidated into [`docs/`](docs) and [`config-recovered/`](config-recovered)
first, and the code remains in Git history (commit `832137ec`).
