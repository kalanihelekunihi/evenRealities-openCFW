# G2 bootloader runtime control-services source closure

Four bounded services are now source-owned MIT C: the hardware-readiness gate
at `0x0042BF54`, event wait-mask service at `0x0042E2A2`, aligned guarded
dispatcher at `0x0042E4A0`, and register power toggle at `0x0042F1C8`.

Apple clang 21 and Homebrew clang 22 reproduce all 296 authenticated bytes
exactly from mnemonic-only Arm source. Portable tests cover readiness-result
precedence, event mask construction and wait results, aligned versus rejected
dispatch, status decoration, and power-transition register/call ordering. Live
MMIO, floating-point probe, scheduler/event, interrupt-mask, timing, power,
peripheral, and cold-boot behavior is blocked by unavailable physical evidence.
