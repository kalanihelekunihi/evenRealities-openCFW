# G2 bootloader format-primitives source closure

The authenticated stock region `[0x004159A0,0x00415AB6)` contains four
complete formatter primitives: unsigned 64-bit decimal output, unsigned
64-bit hexadecimal output, nullable string length, and null-output-aware
repeated-character output. Complete-image Thumb scans authenticate 11 direct
caller edges, all within the neighboring float/format cluster.

Clean-room freestanding C implements each recovered contract without libc.
Decimal output calls the already source-owned shift/add divide-by-ten helper;
the other three leaves have no relocations or runtime dependencies. The four
compiled leaves total 198 bytes and replace 278 stock bytes. Exact identities,
placements, patch bytes, caller topology, dual-toolchain outputs, provider
accounting, packages, and flash plans are enforced by
`tools/analyze_g2_bootloader_numeric.py` and the bootloader overlay tests.

Hardware validation is explicitly blocked by unavailable authorized responsive
right-temple evidence. The subsequent float/formatter closure now owns
`[0x00415AB6,0x00415FAE)`; this document remains the narrower provenance
record for its four prerequisite primitives and authorizes no signing or
hardware operation.
