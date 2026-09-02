# G2 bootloader SPOT-manager temperature initialization source closure

The authenticated dispatch pointer at `0x0041D154` enters the 80-byte
temperature-monitor initializer at `0x0042AC54`. Both reviewed compilers
reproduce the body exactly after its three provider relocations. Host tests
cover both busy gates, enable/configuration errors, timeout mapping, and
success. Live sensor/MMIO validation is blocked by unavailable physical
evidence.
