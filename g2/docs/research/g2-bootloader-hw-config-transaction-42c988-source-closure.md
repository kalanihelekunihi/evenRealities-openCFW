# G2 bootloader hardware-configuration transaction source closure

The executable span `[0x0042C988,0x0042CC34)` is represented by MIT
clean-room C in
`components/bootloader/core_overlay/runtime_hw_config_transaction_42c988.c`.
Its 684-byte Thumb body is byte-exact under canonical Apple clang 21 and
Homebrew clang 22 after seven strict provider calls. Relocated SHA-256 is
`1a89b00660cf0c54c66e781ac95f19dd764bb671587c36959ad2cd34fec53ae5`;
unrelocated SHA-256 is
`904ef19dffe0d14d032fbab68fc23a1902fc9eb9704230e52a4a29e5d302503f`.

Mode 0 reacquires the per-instance resource, optionally restores thirteen
saved register values, restores command-queue state, performs the active-status
wait, clears the saved marker, and enables the mode route. Modes 1 and 2 enforce
the active/pending guard, optionally capture the same thirteen-register
snapshot, disable command-queue state, mark the snapshot valid, clear control
bits 0 and 4, release the resource, and disable the mode route. Portable tests
cover validation, mode bounds, missing snapshot, restore, save, active guards,
control clearing, and status propagation. Direct callers are `0x004304EC` and
`0x00430552`; the Apollo-main analogue at `0x0055C7E8` matches 657 of 684
bytes, differing only at image-local literals and provider edges.

This closes the software representation and production-image routing gap for
the span. Real MMIO, saved-register validity, retained-SRAM, command-queue,
power/clock routing, timing, concurrency, interrupt, reset, and cold-boot
behavior remains **blocked by unavailable physical evidence** because no
authorized G2 hardware is available. No signing, flashing, reset, MMIO, or
hardware operation was performed, and functional completeness is not claimed.
