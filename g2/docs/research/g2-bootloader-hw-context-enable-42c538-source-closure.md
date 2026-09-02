# G2 bootloader hardware-context enable source closure

The executable span `[0x0042C538,0x0042C63A)` is represented by MIT
clean-room C in
`components/bootloader/core_overlay/runtime_hw_context_enable_42c538.c`.
Its 258-byte Thumb body is byte-exact under canonical Apple clang 21 and
Homebrew clang 22 after three strict calls to the source-owned status router
and command-queue adapter and the retained status-check provider. Relocated
SHA-256 is
`0183cf1cab1b0089fb0b49f71137bf868309198abd9319ca1e35f794ba430f2a`;
unrelocated SHA-256 is
`0541dca0e2b4a414177436b877cf5473f5b854a12b96d4d98724747ac1293da4`.

The service validates the `0x01123456` context magic, treats an already-active
context idempotently, gates activation through the hardware-status router,
initializes optional command-queue state, performs the bounded retained status
check, marks success with bit 25, and clears control bits 0 and 4 on failure.
Host tests cover validation, idempotence, readiness rejection, command-queue
failure, success, and rollback. Its sole bootloader caller is `0x0043056C`.
The Apollo-main analogue at `0x0055C32E` matches 246 of 258 bytes; differences
are confined to image-local literal and provider edges.

This closes the software representation and production-image routing gap for
the span. Real retained-SRAM, MMIO, command-queue, timing, concurrency,
peripheral, interrupt, reset, and cold-boot behavior remains **blocked by
unavailable physical evidence** because no authorized G2 hardware is
available. No signing, flashing, reset, MMIO, or hardware operation was
performed, and functional completeness is not claimed.
