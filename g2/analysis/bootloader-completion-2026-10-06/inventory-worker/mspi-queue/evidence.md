# MSPI command-queue source recovery evidence

Image: `g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, load base
`0x410000`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
The tested address spans are listed with their per-span SHA-256 in
`result.json`; addresses are in the image's `0x410000` address space.

The leaf contracts found in the stock instructions are:

* `0x4249a0` clockgen control preserves and restores PRIMASK around edits to
  `0x40004110`; enabling calls the delay provider with raw argument `10`.
  The source masks the input bytes and retains the instruction-level shift
  behavior for module IDs outside the normal range.
* `0x423f28` creates a 12-byte config (`input >> 1`, buffer pointer, option 1)
  and passes interface `(module + 8) & 0xff` and the handle-slot address to
  `0x427794`; the wrapper ignores that helper's status.
* `0x423f8e` requests clock 4 for user `(module + 16) & 0xff`; a nonzero
  status skips queue enable. On success it calls `0x427878` with the pointer
  at MSPI-state offset `0x828`, ignoring status.
* `0x423fac` calls `0x4278c8` with that same queue pointer and propagates its
  status.
* `0x423f54` uses the module value in state offset 4 to select the global
  handle slot, calls `0x427ad6(queue, 1)` if nonnull, ignores status, and
  clears the slot.
* `0x427794`, `0x427878`, `0x4278c8`, and `0x427ad6` are implemented as source
  here, including index refresh (`0x427754`), validity and capacity checks,
  enable/disable flag and MMIO updates, and termination's force/status path.

The Apollo510 SDK tree has public HAL signatures and helper descriptions, but
not the implementation source for these private/generic command-queue bodies.
The generic behavior above was reconstructed from the locked instruction
ranges, rather than copied from or assumed based on a different SDK build.

The resource table at `0x430880` is 12 rows × 10 32-bit words (480 bytes),
SHA-256 `1ed1fa3682f9c16c403ee0e6cee7761b70ca610656a2b6e56de3f0b05cee7fea`.
Every pointer-shaped field in columns 0–4 and 6 is an MMIO address in the
`0x400xxxxx` range; columns 5 and 7–9 are scalar mask/value words. No callback
or executable address is present. The comparison now loads this emitted source
ELF resource segment and verifies exact byte equality to the locked image
before running the queue fixtures.

`result.json` records a PASS across 73 original/source fixtures and 808 distinct
original instruction bytes observed. Covered cases include invalid and valid
queue initialization, interface range, size and null checks, active-state
rejection, MMIO writes, enabled/disabled transitions, DMB threshold behavior,
queue termination with force on/off, index refresh/wrap behavior, wrapper
clock-request success/failure, wrapper handle selection, PRIMASK preservation,
and clockgen bit-field updates. The comparison is limited to synthetic mapped
memory. Clock request and delay are injected providers; no hardware was used.

The following bodies remain external integration dependencies: `0x4222f0`
clock request and `0x41d1c0` delay. The stock `0x41b8ec` critical-save
instructions are executed in the fixture (not replaced by a provider).
