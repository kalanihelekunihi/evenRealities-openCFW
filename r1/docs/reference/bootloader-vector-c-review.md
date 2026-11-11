# R1 bootloader startup vectors in C

`r1/src/bootloader/runtime/native_startup_vectors.c` replaces the last R1
compiled assembly unit, the pinned Nordic SDK 17.1.0 nRF52840 GCC startup
table. The C source declares its 128-word vector table, weak default handlers,
and the same 16 KiB stack and 16 KiB heap reservations. The existing C
`Reset_Handler` continues to own initialized-data copy and startup handoff.
The obsolete generated assembly entry was removed from `r1/src/sources.json`.

All 54 nonzero vector positions and 74 zero positions match the pinned SDK
table. The 951-unit R1 composition at
`build/r1-c-startup-final-20261110/report.json` compiles without failures or
duplicate strong symbols. The strict bootloader link at
`build/r1-c-startup-final-20261110/boot-link/report.json` has no
undefined references and verifies the linked 512-byte vector at `0xf8000`,
initial SP `0x20040000`, and a Thumb reset vector to the C handler. The
link map retains 16 KiB stack and heap sections and passes the RAM overlap
assertion. The C-linked bootloader text is 16 bytes smaller than the prior
assembly-linked diagnostic.

The current strict bootloader receipt at
`build/r1-boot-link-ram-checked-20261111/report.json` also verifies the RAM
layout: `.bss` ends at `0x20007f68`, the 16 KiB heap ends at `0x2000bf68`,
and the 16 KiB MSP reservation spans `0x2003c000..0x20040000`. The vector's
MSP equals the linker RAM top; no region overlaps. The image remains 23,024
bytes with SHA-256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
A 4 KiB stack candidate under ignored
`build/r1-boot-stack-negative-20261111/` fails the new linker assertion and
strict RAM gate.

The bootloader vector conversion does not establish stock byte identity or
physical boot. The application now strictly links with validated static
flash/RAM placement; runtime stack depth and hardware behavior remain open.
