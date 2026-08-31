# G2 bootloader MSPI lifecycle source closure

## Result

The authenticated `am_hal_mspi_enable`, `am_hal_mspi_disable`, and
`am_hal_mspi_deinitialize` entries now execute structured, freestanding
BSD-3-Clause C in production at `0x00425066`, `0x004250F0`, and
`0x0042516C`. The routed objects contribute 128, 112, and 56 bytes,
respectively. Enable and disable return before their 10-byte and 6-byte stock
tails, which remain authenticated but unreachable. The additional six bytes
at `[0x00425166,0x0042516C)` remain alignment/literal data.

This closes the lifecycle software implementation gap; it does not establish
physical-device behavior. Live CQ, DMA, XIP, interrupt, timing, attached-flash,
warm-reset, and cold-boot qualification is **blocked by unavailable physical
evidence**. No flash, sign, erase, reset, MMIO, or other hardware operation was
performed.

## Recovered behavior

Enable validates the allocated handle and configured state, rejects a second
enable, initializes command-queue state when a TCB is present, clears pending
and high-priority bookkeeping, programs the recovered queue-set bits, and
marks the handle enabled.

Disable is idempotent for an already-disabled handle, rejects active command
queue or high-priority work, propagates CQ-disable errors, terminates the CQ,
clears `DEV0XIP.XIPEN0`, applies the configured XIP-off delay, and clears the
enabled bit. Deinitialize invokes disable when needed and intentionally ignores
that nested return value before clearing the initialized bit and module field,
matching the authenticated stock ordering.

## Object admission

Apple Clang 21 and Homebrew LLVM Clang 22 emit identical reviewed objects:

| Entry | Compiled bytes | Unrelocated SHA-256 | Relocated SHA-256 | Strict calls |
|---|---:|---|---|---:|
| enable `0x00425066` | 128 | `48e3ad6232bc4611f275c1b2e02f56fcccb5afa95a049eb2d6f6a85446ceee48` | `c876636f4730b39f87086fb8139b51776718a9d893416679d4ec5b5f479495c4` | 1 |
| disable `0x004250F0` | 112 | `d691afe79b669a61d3d71ea8ca375f48848c99261ac81af229f0849bb5d36a7f` | `f446afa834abdde425a837d4d7e20dd8fcbd1ec0fd8b0cc6d155a419d86aec49` | 3 |
| deinitialize `0x0042516C` | 56 | `efb6f9ca3e303b73d14e3d46abce0f02e36f8748d272a79f94e7029d983805e6` | `2b647746b8f49c15a6b428c66e1e23a77b991bc324f3a94847573d5dc2f833fc` | 1 |

The relocations bind enable to the already-routed CQ initializer; disable to
CQ disable, CQ termination, and the microsecond delay service; and
deinitialize to its same-source disable sibling. Strict relocation admission
permits no undeclared call or data dependency.

## Verification and remaining frontier

The host state-machine oracle covers invalid and unconfigured handles,
TCB/no-TCB enable paths, queue initialization, idempotent disable, busy
refusal, CQ-disable error propagation, CQ termination, conditional XIP delay,
and deinitialization after both successful and busy nested disable paths. The
audit independently compiles both target profiles, authenticates stock bodies
and callers, checks AmbiqSuite semantic anchors, verifies production routing,
and enforces component byte conservation.

Canonical provider identities are now:

- Apple Clang: 163,840 bytes,
  `ce19a1a4423dbb5a892d144bf52dac4fdccaac956614775a8b02c685dca7042e`.
- Linux Clang: 163,824 bytes,
  `a5f9492da37c7f96ad2998a281f83c60e8308f40f42970386260524626a0d2aa`.

Apple bootloader accounting is 30,071 source-owned, 16,490 generated, and
117,279 retained bytes. The first retained byte after a newly routed lifecycle
entry is the unreachable enable tail at `0x004250E6`; the next executable
software frontier is `am_hal_mspi_control` at
`[0x004251C0,0x004262E0)`. Firmware-wide functional completeness is not
claimed.
