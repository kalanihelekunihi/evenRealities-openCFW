# G2 bootloader MSPI lifecycle source candidates

`am_hal_mspi_enable`, `am_hal_mspi_disable`, and `am_hal_mspi_deinitialize` were admitted as compilable BSD-3-Clause C candidates for the authenticated entries at `0x00425066`, `0x004250f0`, and `0x0042516c`. The completed production proof, including exact object sizes, unreachable stock tails, and dual-profile identities, is recorded in `g2-bootloader-mspi-lifecycle-425066-4251a4-source-closure.md`.

The host state-machine model tests invalid and unconfigured handles, TCB/no-TCB enable paths, command-queue state initialization, idempotent disable, busy refusal, CQ-disable error propagation, CQ termination, conditional XIP delay, and deinitialization. It also preserves the stock behavior in which deinitialize ignores a nested busy/disable error before releasing the handle.

The next body is `am_hal_mspi_control` at `0x004251c0`, after 28 retained literal bytes beginning at `0x004251a4`.

Hardware validation is blocked by unavailable physical evidence. Future authorized qualification must cover CQ, DMA, XIP, interrupt, timing, lifecycle, and cold-boot behavior; this software-only wave makes no physical-validation claim. No flash, reset, signing, or MMIO operation was performed.
