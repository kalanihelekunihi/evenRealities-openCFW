# G2 bootloader CLKGEN HFADJ configuration source closure

The authenticated entry `[0x00426C72,0x00426C7E)` publishes a caller-supplied
CLKGEN HFADJ configuration after forcing enable bit 0 and returns zero. Its
authenticated register target is `0x40004020`.

`runtime_clkgen_hfadj_config_426c72.c` expresses the contract as freestanding
MIT C. Apple clang 21.0.0 and Homebrew clang 22.1.8 emit the same 16-byte,
relocation-free Thumb leaf. Because the complete stock entry is only 12 bytes,
the compiled body occupies authenticated generated-NOP space at
`[0x00426C28,0x00426C38)` inside the already-routed divider entry tail. A
generated `B.W` at `0x00426C72` transfers control to the C body; there is no
fallthrough or interior ingress into the cave.

Host tests verify full configuration publication, forced bit 0, and the zero
return value. Both canonical profiles, the provider contract, manifest, and
post-MSPI census verify the route. No live MMIO, package transmission, signing,
reset, erase, or flash operation was performed. Live-device qualification is
blocked by unavailable physical evidence.
