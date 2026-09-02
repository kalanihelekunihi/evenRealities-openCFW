# G2 bootloader hardware-context claim source closure

The executable span `[0x0042C4C6,0x0042C538)` is represented by MIT
clean-room C in
`components/bootloader/core_overlay/runtime_hw_context_claim_42c4c6.c`.
Its relocation-free 114-byte Thumb body is byte-exact under canonical Apple
clang 21 and Homebrew clang 22. Stock, linked, and unrelocated SHA-256 are
`9727ea0e7e8786ddfab4618f79b101d91192e7291034937b15da4a9246d17db2`.

The service rejects indices outside `[0,8)`, null output storage, and already
claimed slots with status 5, 6, and 7 respectively. Success preserves the
upper state bits, sets ownership bit 24, clears bit 25, stamps the low-24-bit
magic `0x123456`, stores the index, publishes `base + index * 0x8A8`, and
returns zero. Host tests cover validation ordering, non-mutating rejection,
successful state transformation, and address calculation. The Apollo-main
analogue at `0x0055C2BC` matches 110 of 114 bytes; only its two image-local
literal-load encodings differ. The direct call at `0x00430514`, absence of
interior ingress, and absence of a stored bootloader function pointer are
pinned.

This closes the software representation and production-image routing gap for
the span. Real retained-SRAM ownership, concurrency, and peripheral lifecycle
behavior remains **blocked by unavailable physical evidence** because no
authorized G2 hardware is available. No signing, flashing, reset, MMIO, or
hardware operation was performed, and functional completeness is not claimed.
