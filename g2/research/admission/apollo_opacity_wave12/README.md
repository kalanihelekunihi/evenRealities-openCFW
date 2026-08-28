# Apollo opacity wave 12

The complete post-Wave-11 residual-only closure rooted at `0x004BFED6` contains one contiguous 1,902-byte function and no static callees. Positive register, enum-order, constant, and control-flow evidence identifies it as AmbiqSuite Apollo510 `mspi_device_configure` from `am_hal_mspi.c`.

The maintained SDK 5.1.0 source and provenance are already checked in under `g2/third_party/ambiqsuite-apollo510` with the original BSD-3-Clause terms. The provider model in this directory retains that license and converts all 26 device modes into a pure register-field plan. It performs no MMIO and exists only for deterministic host verification.

Production routing remains excluded. Function identity does not prove the shipped private state layout, exact SDK revision, compiler flags, IAR ABI, optimization/LTO behavior, Cortex-M55 code generation, relocation, link order, or placement.
