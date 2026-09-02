# G2 bootloader hardware-instance configurator source closure

The authenticated Thumb entry `[0x0042CC34,0x0042CDB0)` is a 380-byte
hardware-instance validation and mode-specific configuration service. Its sole
direct caller is `0x00430562`; no interior entry or stored function pointer is
present. The Apollo-main analogue begins at `0x0055CA94` and shares 352 of 380
bytes.

`runtime_hw_instance_configure_42cc34.c` is first-party MIT clean-room source.
Canonical Apple clang 21 and Homebrew clang 22 both emit the stock body exactly
after the single strict `R_ARM_THM_CALL` relocation at body offset `0x7C` to
the source-owned clock encoder at `0x0042C26A`. The relocated body SHA-256 is
`d881da0882c4dcc9f1385402b877bcb3d8c379de014c78707c8db99f5b03aa93`;
the unrelocated SHA-256 is
`cd9cd51d75de4bf4ffa5587acfeab18036746f59f4c60d9b5c2ce91edac3f631`.

The portable model and focused tests cover invalid handles, the eight-instance
bound, active-state rejection, dynamic rate and flag bounds, encoded-clock and
control publication, the authenticated 100 kHz / 400 kHz / 1 MHz fixed-rate
register maps, buffer-end safety, window computation and clamping, and clearing
four per-instance slots. The census, overlay registration, redirect manifest,
dual-toolchain extraction, ingress topology, main analogue, source review, and
component byte conservation are pinned by the exhaustive post-MSPI analyzer.

No hardware operation occurred. Live SRAM, MMIO, clock encoding, DMA/buffer
coherency, peripheral timing, concurrency, interrupt, reset, and cold-boot
qualification is blocked by unavailable physical evidence. Firmware-wide
functional completeness is not claimed.
