# G2 bootloader CLKGEN HFADJ disable source closure

The authenticated entry `[0x00426C7E,0x00426C8C)` clears only bit 0 of CLKGEN
HFADJ register `0x40004020`, preserves every other register bit, and returns
zero.

`runtime_clkgen_hfadj_disable_426c7e.c` expresses the contract as freestanding
MIT C. Apple clang 21.0.0 and Homebrew clang 22.1.8 emit the same 20-byte,
relocation-free Thumb leaf. Because the stock entry is 14 bytes, the compiled
body occupies authenticated generated-NOP space at
`[0x00426C38,0x00426C4C)` after the adjacent HFADJ configuration cave. A
generated `B.W` at `0x00426C7E` transfers control to the C body; there is no
fallthrough or interior ingress into the cave.

Host tests verify bit-preserving disable and the zero return value. Both
canonical profiles, the provider contract, manifest, and post-MSPI census
verify the route. No live MMIO, package transmission, signing, reset, erase,
or flash operation was performed. Live-device qualification is blocked by
unavailable physical evidence.
