# G2 bootloader descriptor registrar source closure

The authenticated executable interval `[0x00430280,0x004303BC)` is now
production-routed from `runtime_descriptor_register_430280.c`. The 316-byte
MIT clean-room body is reproduced exactly by Apple clang 21 and Homebrew clang
22 after eleven strict Thumb-call relocations. Its sole direct caller is
`0x004301DC`; no interior or stored-pointer ingress exists. The Apollo-main
analogue at `0x0053A454` matches 285 of 316 bytes.

The portable model validates null/count rejection, the 12-byte descriptor
stride, types 1, 2, and 4, boolean routing, callback registration, conditional
interrupt setup, seven-word interrupt masks, priority selection, and NVIC
enable accounting. Four shared literal cells and every provider edge are
pinned by the exhaustive frontier analyzer.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live descriptor tables, callback
targets, interrupt masks, SCB/NVIC state, concurrency, reset, and cold boot are
blocked by unavailable physical evidence. No signing, flashing, reset, or
hardware access occurred, and functional completeness is not claimed.
