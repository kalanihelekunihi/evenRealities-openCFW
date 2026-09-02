# G2 bootloader state/range/dispatch source closure

The authenticated bootloader bodies at `0x0042CDF8..0x0042CEA4`,
`0x0042CED8..0x0042CFE0`, and `0x0042D562..0x0042D5C2` are now produced by
reviewable MIT-licensed C in
`components/bootloader/core_overlay/runtime_state_range_dispatch_42cdf8.c`.

The first service applies a bounded seven-bit state adjustment when the
associated mode gates are active. The second classifies a floating-point
sample into three valid ranges, updates the range bounds and transition flag,
and reports invalid/out-of-range samples. The third routes the byte-sized event
ABI to its authenticated providers, including the range-update service.

Both reviewed compiler profiles reproduce all three stock bodies exactly after
the declared Thumb call relocations. The same bodies also match their Apollo
main analogues at `0x005A001C`, `0x005A00FC`, and `0x005A0786`. Host-side tests
cover boundary classification, state saturation, dispatch routes, source
reviewability, and the relocation contracts. Hardware behavior remains
blocked by unavailable physical evidence.
