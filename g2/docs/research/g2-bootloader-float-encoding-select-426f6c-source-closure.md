# G2 bootloader floating encoding selector source closure

The 198-byte Thumb-2 function at `0x00426F6C..0x00427032` is byte-identical
to the independently linked Apollo-main body at `0x005395A0..0x00539666`.
Its hard-float entry takes an output pointer in `r0` and two `float` values in
`s0` and `s1`. It rejects a null output with status 6, rejects a second input
outside the authenticated `[60.0, 0x1.e00002p+9)` interval with status 5,
tries the source-routed ratio encoder and then the source-routed multiplier
encoder, returns status 1 if neither can encode the pair, and otherwise
publishes the authenticated fields at output offsets 1, 2, 3, 6, and 8 before
returning status 0.

`runtime_float_encoding_select_426f6c.c` expresses that behavior as ordinary
MIT-licensed C and declares the hard-float PCS explicitly. Apple clang 21.0.0
and Homebrew clang 22.1.8 both emit the same 180-byte function. Its two
strictly bound relocations call the production-routed stock entries at
`0x00426DB4` and `0x00426EAC`; the relocated cave body has SHA-256
`685316ba4585568c3b023923927fe0ef5a399ac92f00c44c8eaa3f3a24ac6b2b`.
The entry is replaced by a generated `B.W` and NOP fill, and the compiled body
occupies authenticated generated-NOP space at
`0x00415EA4..0x00415F58`.

This is software-only evidence. No signing, flashing, reset, MMIO execution,
or physical-device operation was performed. Target behavior remains
`blocked by unavailable physical evidence`.
