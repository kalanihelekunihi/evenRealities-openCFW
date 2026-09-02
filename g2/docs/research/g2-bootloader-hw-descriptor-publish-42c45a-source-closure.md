# G2 bootloader hardware-descriptor publisher source closure

The executable span `[0x0042C45A,0x0042C4C6)` is now represented by MIT
clean-room C in
`components/bootloader/core_overlay/runtime_hw_descriptor_publish_42c45a.c`.
Its 108-byte Thumb body is byte-exact under the canonical Apple clang 21 and
Homebrew clang 22 profiles. The stock, linked, and unrelocated SHA-256 is
`0deea2026365cb9c3471cdd81a7644c3fa519db2239154f3456da25ab88c5525`;
the function has no linker relocations.

The function advances a producer index modulo the configured ring length,
selects the corresponding 32-byte descriptor, and publishes six descriptor
fields to one hardware-instance register bank. The portable model verifies
successor selection, wraparound, and the observed field order
`[0, 1, 4, 2, 3, 5]`. Static ingress analysis identifies the sole direct call
at `0x0042C7EC` and no stored function pointer.

This closes the software representation and production-image routing gap for
the span. Execution against the real register bank remains **blocked by
unavailable physical evidence**: no authorized G2 hardware is available in
this workspace. No flashing, signing, reset, or MMIO experiment was performed,
and this note does not claim hardware validation or overall functional
completeness.
