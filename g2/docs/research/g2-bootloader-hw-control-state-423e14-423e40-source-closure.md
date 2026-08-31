# G2 bootloader hardware-control state-mapper source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The executable body at `[0x00423E14,0x00423E40)` is source-closed by
`runtime_hw_control_state_423e14.c`. The maintained source is 1,273 bytes with
SHA-256 `21490e33954cd21c82d5e1f15980de3d6ddab65057bc1b0e0d5de8d5e234167c`.
Apple Clang 21.0.0 and Homebrew Clang 22.1.8 both reproduce the relocation-free
44-byte body exactly with SHA-256
`7179c8490a752b21bfb18de838e98aa785e90da2cbde22e10356fc75829045c1`.

The function reads the 32-bit state at context offset `0x838`. State one is
advanced to state two and merges `0x40A0` into the caller flags. State two
returns `0x4000` without mutation. Every other value merges `0x4080`. Five
focused tests cover these paths, source cross-compilation, the authenticated
body, and the 74-byte successor identity at `[0x00423E40,0x00423E8A)`.

Canonical provider accounting is 25,133 source-owned, 16,528 generated patch,
16 alignment, and 122,163 retained official bytes across 300 source-owned
functions, 179 relocated leaves, five caves, and 97 exact in-place leaves. The
163,840-byte provider and 4,745,418-byte unsigned package remain byte-identical
with SHA-256 `3ae28d27...55eac` and `3c8cdcdb...c785`. The 4,657,431-byte
flash plan has SHA-256
`ce6175e68c69cecbd2de52dc71a30c7a9eb607c51c224380e88786d3761f85f6`
with 6,691 placed, zero unresolved, six container-only, and six protected
regions.

No signing, flashing, reset, boot, device, SRAM, register, interrupt, or MMIO
operation occurred. Live qualification is explicitly blocked by unavailable
authorized responsive right-temple evidence. Firmware-wide completeness is
not claimed: the earliest retained executable remains `0x0042308E`, and the
sequential executable frontier is `0x00423E40`.
