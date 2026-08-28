# Apollo opacity wave 12: Apollo510 MSPI device source closure

Wave 12 starts at the authoritative post-Wave-11 residual maximum, `0x004BFED6` / 1,902 bytes. The complete residual-only closure consists solely of this function: it has no static callees, one contiguous authenticated range, and no interior islands.

## Positive identity

The body is AmbiqSuite Apollo510 `mspi_device_configure`:

- `DAT_004C0754` is the installed little-endian MSPI base `0x40060000`;
- the module selector is multiplied by the Apollo510 `0x1000` MSPI stride;
- writes target the `DEV0CFG`, `DEV0XIP`, and `PADOUTEN` register offsets;
- masks `0xFFFFFFE0`, `0xFDFFFFFF`, and `0xFFFFF0FF` update `DEVCFG0`, `SEPIO0`, and `XIPMIXED0`;
- all 26 `am_hal_mspi_device_e` values occur in the exact maintained-source order;
- the `bClkonD4` alternatives use `0x80000013` for serial pads and `0x8000001F` for quad pads.

The authenticated provider is AmbiqSuite SDK 5.1.0 commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, already checked in under `g2/third_party/ambiqsuite-apollo510`. Its original BSD-3-Clause license is retained.

## Software-only provider model

The research admission includes a BSD-3-Clause pure provider model for all 26 modes. It produces `DEVCFG0`, `SEPIO0`, `XIPMIXED0`, and `PADOUTEN` field values without exposing a register address, dereferencing volatile memory, or performing MMIO. A host harness verifies normal and clock-on-D4 plans for every mode plus fail-closed invalid inputs.

Four direct data cells are pinned and reconciled: the MSPI base and three pad-output constants. Their 16 physical bytes add zero function-envelope bytes.

Residual accounting changes from 1,309 functions / 142,400 bytes to 1,308 functions / 140,498 bytes. The next largest envelope is `0x00438FB8` / 1,710 bytes.

## Production admission

Production routing remains excluded. Exact function identity does not prove the firmware’s private state layout, SDK revision, IAR ABI, compiler flags, optimization/LTO choices, Cortex-M55 code generation, relocation, link order, or placement. Both production profiles require reviewed receipts and byte/relocation-equivalent placement proof. No hardware operation or hardware test is performed.
