# G2 bootloader command-queue public services at `0x00427794..0x00427C80`

## Result

The eleven contiguous authenticated command-queue functions in
`[0x00427794,0x00427C80)` are now production-routed to reviewable
BSD-3-Clause C at their original public entry addresses. Together with the
private index updater at `0x00427754`, this closes the complete recovered
Apollo510 command-queue family used by the bootloader.

The production source is
`components/bootloader/core_overlay/runtime_cmdq_services_427794.c`. It
implements initialization, enable/disable, block allocation/release/post,
status, termination, error recovery, reset, and looping post. It contains no
encoded instruction directives; the only target-specific instruction is the
reviewable `dmb sy` memory barrier required before publishing SSRAM-backed
queue contents to hardware.

## Upstream and binary authentication

The authoritative implementation is
`mcu/apollo510/hal/mcu/am_hal_cmdq.c` from the official Ambiq repository at
immutable commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`. The 35,930-byte
source has SHA-256
`60aa2126ca01cd72f746a92d6f34a13e909fdab24ebfab6d6b0a70b026d8fa83`
and Git blob `0a286e565cad27cef801c389b5dedae826a2669a`. The complete family is an
exact independent Apollo-main match at `0x00538D58..0x00539244`.

The authenticated stock spans are:

| Service | Stock span | Stock bytes | Apple C bytes | Linux C bytes |
|---|---:|---:|---:|---:|
| init | `0x427794..0x427878` | 228 | 184 | 176 |
| enable | `0x427878..0x4278C8` | 80 | 68 | 68 |
| disable | `0x4278C8..0x42790A` | 66 | 52 | 52 |
| alloc block | `0x42790A..0x4279BE` | 180 | 148 | 148 |
| release block | `0x4279BE..0x4279F0` | 50 | 48 | 48 |
| post block | `0x4279F0..0x427A56` | 102 | 92 | 88 |
| get status | `0x427A56..0x427AD6` | 128 | 104 | 108 |
| terminate | `0x427AD6..0x427B38` | 98 | 88 | 88 |
| error resume | `0x427B38..0x427BAA` | 114 | 88 | 88 |
| reset | `0x427BAA..0x427C12` | 104 | 88 | 84 |
| post loop block | `0x427C12..0x427C80` | 110 | 96 | 96 |

The canonical Apple provider owns 1,056 compiled bytes in place. The 204
remaining stock bytes after those compiled return paths have no public or
direct interior ingress and remain explicitly typed as authenticated
unreachable tails. Linux owns its independently pinned compiled prefix for
each leaf. No function-entry redirect is needed, so all existing callers and
stored ABI expectations retain the original addresses.

## Recovered ABI and behavior

The target ABI is pinned to the upstream 44-byte queue state, 40-byte register
table, 12-byte configuration, 8-byte entry, and status booleans at offsets
12–14. The recovered fixed objects are the twelve-element state table at
`0x200262F0` and register table at `0x00430880`; the handle prefix is valid
when its low 25 bits equal `0x01CDCDCD`.

The source preserves all material behavior:

- interface, pointer, size, handle, lifecycle, pending-allocation, and capacity
  validation with the recovered Ambiq status values;
- priority and enable bits in the queue configuration register;
- eight-bit hardware indices backed by monotonic 32-bit software epochs;
- contiguous allocation, circular-buffer wrap entries, index-update entries,
  optional update interrupts, release rollback, and hardware end publication;
- SSRAM `dmb sy` ordering before enable or end-index publication;
- processed/posted/allocated status plus transaction, pause, and error flags;
- non-forced in-use termination, forced termination, reset, and pause-mask
  cleanup; and
- error traversal across queue-address wrap entries, interrupt-bit clearing,
  queue-address repositioning, and disabled return state.

Allocation, status, and termination each have one strict
`R_ARM_THM_CALL` relocation to the already source-routed updater at
`0x00427754`, at object offsets `0x26`, `0x18`, and `0x16` respectively. The
other eight leaves are relocation-free. Apple clang 21.0.0 and Homebrew clang
22.1.8 outputs, stock replacement prefixes, full stock bodies, all direct
caller sets, and all eleven exact Apollo-main analogues are pinned by the
frontier analyzer.

## Verification and hardware boundary

The host fixture uses an address-token resolver rather than host pointers, so
the target's 32-bit queue-entry ABI is exercised without MMIO. Tests cover
invalid initialization, idempotent lifecycle control, SSRAM barriers,
contiguous and wrapped allocation, capacity exhaustion, release/post, pending
status, flag decoding, forced termination, wrapped error recovery, reset, and
loop posting. Both reviewed Thumb profiles compile and relocate every leaf;
the Apple and Linux raw providers rebuild with zero unclassified ownership.

Live MMIO, DMA/coherency, interrupt races, peripheral-specific pause/error
behavior, queue timing, downstream transactions, reset, and cold boot are
**blocked by unavailable physical evidence**. No signing, flashing, reset,
live register access, or other hardware mutation was performed. Firmware-wide
functional completeness is not claimed.
