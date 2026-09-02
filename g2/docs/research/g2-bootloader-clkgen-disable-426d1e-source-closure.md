# G2 bootloader CLKGEN disable source closure

## Authenticated boundary

The stock entry is `[0x00426D1E,0x00426D2C)`, 14 bytes, SHA-256
`b6e29296fa925d2ee116e96d5fa22e60265cdccedfe9072766a7adf69042a70e`.
Its complete behavior is to read CLKGEN register `0x40004050`, clear bit 0
while preserving every other bit, write the result, and return zero. The only
direct callers are `0x0042191E` and `0x00422082`; no interior halfword has a
direct caller or stored entry pointer. The register literal remains typed
official data at `0x00426D44`.

The next four bytes `[0x00426D2C,0x00426D30)` are padding, and
`[0x00426D30,0x00426D48)` is a 24-byte literal pool. The next executable
frontier therefore begins at `0x00426D48`.

## Production C route

`components/bootloader/core_overlay/runtime_clkgen_disable_426d1e.c` is an
810-byte clean-room MIT C source file, SHA-256
`0d6d5eb220150a2b1aadb53f5d0392911612a4177a0b1ba378cc45f622e0bee1`.
Apple clang 21.0.0 and Homebrew clang 22.1.8 independently emit the same
relocation-free 20-byte Thumb body, SHA-256
`cbe1ab0d26505fa34fdac078e0935015001b2f3138109d8bad340acef1bbb48a`.
It occupies authenticated generated-NOP space at
`[0x00415C50,0x00415C64)`; the stock entry becomes a bounded `B.W` followed
by five NOPs. Host tests cover already-clear, bit-set, and all-other-bits-set
register states.

## Image and ownership evidence

The canonical Apple provider is 163,840 bytes, SHA-256
`c979561dca62accdb4f2a4bbd3c6d2ac02518225b59f4a9639401b1e959765f3`;
the reviewed Linux provider is 163,824 bytes, SHA-256
`621f22b25a857c6081bf979eabc2a3d7aad57c21b766fee2439a36e1a9251751`.
Apple accounts for 34,661 source-owned, 16,456 generated patch-site, 16
generated-alignment, and 112,707 retained bytes. Linux accounts for 34,643
source-owned, 16,456 generated patch-site, 16 generated-alignment, and the
same retained complement.

The complete deterministic packages are 4,749,540 bytes, SHA-256
`a1b56ff04cdd1249f1b95324469ca253d11cefe602e8708b198536f31a3b04c9`,
and 4,749,524 bytes, SHA-256
`3e0e89e8eaa83a4e4da5baefbebbb5aaa17a9bd05588643a8de52a0d7c49b983`.
They contain 6,640 and 3,627 placed flash regions, respectively, with zero
unresolved regions and zero unclassified ownership. Fresh independent Apple
and Linux canonical receipts bind source-input closure
`f542d2ad31ada9eb68bbb3c7c0c7319f93861ab8589e2aee2e2471be24a58ae9`.

No signing, flashing, reset, MMIO access, or other hardware operation was
performed. Clock, oscillator, timing, cold-boot, and physical register
qualification is blocked by unavailable physical evidence. Firmware-wide
functional completeness is not claimed.
