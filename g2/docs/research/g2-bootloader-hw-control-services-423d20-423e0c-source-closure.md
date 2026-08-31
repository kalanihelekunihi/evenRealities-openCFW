# G2 bootloader global hardware-control service source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Six executable bodies totaling 228 bytes are source-closed in
`[0x00423D20,0x00423E0C)`: global service (56), initializer (34), register
query (32), indexed register test (36), zero-index wrapper (10), and
interrupt-atomic control service (60). Maintained source
`runtime_hw_control_services_423d20.c` is 6,754 bytes with SHA-256
`8d674073290c947333c72b4df9489f914aa68cff144dbe3feddb51dbf15a976c`.
The six final body SHA-256 values are, in address order,
`e4c5106b...40850`, `147c53dc...0e68`, `43b8c7f2...6824`,
`c5f33fc0...3c36`, `721f0a9d...86a6`, and `946b6974...4002`.

Apple Clang 21.0.0 and Homebrew Clang 22.1.8 reproduce every body exactly.
Seven strict call relocations bind the retained register, delay, and PRIMASK
providers plus the source-owned debug service. Four authenticated fixed calls
bind sibling services. The six-byte register-literal span at
`[0x00423D9A,0x00423DA0)`, two-byte alignment at
`[0x00423DCE,0x00423DD0)`, and eight-byte SRAM literal span at
`[0x00423E0C,0x00423E14)` remain classified as retained data.

Six focused host tests pin the bodies and data seams, register-call arguments,
indexed address derivation, success/failure initialization, 500-unit delay,
control-bit clearing, debug-status normalization, countdown/latch behavior,
and PRIMASK-token restoration. These tests validate the software contracts;
they do not claim physical register, timer, interrupt, or debug effects.

Canonical provider accounting is 25,089 source-owned, 16,528 generated patch,
16 alignment, and 122,207 retained official bytes across 299 source-owned
functions, 179 relocated leaves, five caves, and 96 exact in-place leaves.
The provider and 4,745,418-byte package remain byte-identical with SHA-256
`3ae28d27...55eac` and `3c8cdcdb...c785`. The 4,656,017-byte flash plan has
SHA-256
`15fdf5e7b3fb0e99f62ceb0195084a37bdbe1db8a65d66bd3649f7318d3e486f`
with 6,689 placed, zero unresolved, six container-only, and six protected
regions.

No signing, flashing, reset, boot, device, SRAM, register, interrupt, or MMIO
operation occurred. Live qualification is explicitly blocked by unavailable
authorized responsive right-temple evidence. Firmware-wide completeness is
not claimed: the earliest retained executable remains `0x0042308E`, and the
sequential executable frontier is `0x00423E14` after the retained SRAM
literals.
