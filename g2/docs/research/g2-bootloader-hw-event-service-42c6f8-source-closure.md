# G2 bootloader hardware-event service source closure

The executable span `[0x0042C6F8,0x0042C980)` is represented by MIT
clean-room C in
`components/bootloader/core_overlay/runtime_hw_event_service_42c6f8.c`.
Its 648-byte Thumb body is byte-exact under canonical Apple clang 21 and
Homebrew clang 22 after nine strict calls to already source-owned helpers and
one retained event-application provider. Relocated SHA-256 is
`7272867858e1c23f8ad5e5938ef7f5e02d59289de7c3c76eb6c7ea69fcec5958`;
unrelocated SHA-256 is
`68622fb39f74db4f8713335ee263e25dc024684d86d5e59bc43f600a11ee72b4`.

The service authenticates the hardware context, accumulates interrupt/event
bits, advances and republishes ring descriptors, classifies and dispatches
callbacks, applies event masks, drains command-queue completions, resumes or
enables/disables the command queue, and performs terminal register cleanup.
Portable tests cover validation, ungated accumulation, descriptor retirement,
callback clearing, next-descriptor publication, terminal cleanup, event-mask
application, and command-queue failure propagation. Its sole direct caller is
`0x00430636`. The Apollo-main analogue at `0x0055C558` matches 621 of 648
bytes; differences are confined to image-local literals and provider edges.

This closes the software representation and production-image routing gap for
the span. Real MMIO, retained-SRAM, DMA, callback execution, command-queue,
interrupt, timing, concurrency, reset, and cold-boot behavior remains
**blocked by unavailable physical evidence** because no authorized G2 hardware
is available. No signing, flashing, reset, MMIO, callback, or hardware
operation was performed, and functional completeness is not claimed.
