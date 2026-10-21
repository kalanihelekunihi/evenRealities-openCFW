# R1 firmware source tree

Every reconstructed R1 (nRF52840 application) source lives here. It merges the
former `r1/components`, `r1/source`, `r1/reconstructed`, `r1/source-config`,
`r1/patches`, the FreeRTOS and sensor kernels that lived inside
`r1/research/source-build`, and the bootloader SDK overlay. The pre-merge layout
is preserved at Git tag `pre-consolidation`.

```
r1/src/
├── sources.json     every unit: toolchain, compile profile, role, origin
├── application/     reconstructed application code
│   ├── board/       native drivers and frames (BLE, TWI, sensors, protocol, power)
│   ├── runtime/     libc/math, storage, crash/backtrace, health and model glue
│   ├── rtos/        FreeRTOS 10.5.1 port and kernel slices not provided upstream
│   ├── sdk/         nRF5 SDK deltas
│   ├── checksums/   stock CRC/checksum tables
│   └── adc, crypto, gpio, i2c5, registry, software-twi, st25
├── include/         shared headers (openr1)
├── vendor/          reviewed pseudocode for binary-only vendor libraries (GoMore,
│                    Goodix, GXT310, QMA6100, YHM2710, ...) and extracted model data
├── config/          sdk_config.h, FreeRTOSConfig.h, Goodix, startup and runtime contracts
├── bootloader/      Secure DFU bootloader SDK overlay
└── patches/         patches against the pinned nRF5 SDK and Goodix sources
```

`vendor/` keeps snake_case names because sources include it as
`"software_twi/software_twi.h"` through `-I r1/src/vendor`.

Build with `make sources` (or `make -C r1 sources`); see
[`g2/src/README.md`](../../g2/src/README.md) for the manifest fields, which are
shared. R1 units compile with host Clang, except the GCC 9-2020-q2 profiles that
the hybrid build selected; those run through `tools/build/linux_gcc.py`. Patched
nRF5 SDK files (`nrf_svci_clang.h`, `app_error_handler_gcc_clang.c`) and the SDK
example configuration are generated from `vendor-cache/r1` into the build's
`generated/r1` directory, never tracked.

The function anchors that tie R1 sources to stock entries are in
[`r1/symbols/function-frontier.csv`](../symbols/function-frontier.csv). What was
verified for each family, and how, is in
[`r1/docs/source-reconstruction-findings.md`](../docs/source-reconstruction-findings.md).
Many `native_*` files are `naked` transliterations of stock instructions rather
than C; that document lists which.
