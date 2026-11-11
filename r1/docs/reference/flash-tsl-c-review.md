# R1 FlashDB log-reader control in C

The outer TSL reader at `0x87e14` now expresses read, status decoding and
record updates in C. REA observes the contiguous 68-byte native body through
`0x87e57` in the stock-derived analysis ELF. The locked application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

The reader loads the flash address from TSL +12, requests 32 bytes and ignores
the read status before scanning six status slots. It stores the decoded low
byte at TSL +0. Status zero or one selects the live database word at +88,
`0xffffffff` and zero for TSL +8, +16 and +4. Other statuses select scratch
words +24, +28 and +20 in that order. Volatile packed word views retain
unaligned accesses and live reads when these views overlap.

A 14-byte assembly entry bridge retains the native 48-byte frame: 36 local
bytes and saved R4/R5/LR. Its first 32 bytes remain the flash destination at
caller `SP-48`. The C worker receives this existing RAM explicitly. It does
not zero-fill failed reads or use an uninitialized C scratch array. Helper
frames below that region remain outside the local equivalence claim.

[Machine-readable evidence](flash-tsl-c-review.json) binds:

- 9,310 paired stock/C cases: 480 read-adapter, 262 status-scanner and 8,568
  outer-reader cases. These include partial/non-writing failures, mode flags,
  unaligned database and TSL views, overlapping database/TSL/scratch storage,
  every status stopping position, complete native frame bytes, ordered shared
  accesses, output guards, result, saved registers, SP and masks.
- 10,368 paired integration cases execute the C outer control, read adapter,
  scanner, selected FAL partition read and cache lookup together. They check
  actual bounds/wrapping rules, device lookup, final driver arguments,
  diagnostics, partial failures, record fields and the native frame.
- Zeroing the scratch bytes and snapshotting metadata before the native live
  read order are each rejected by the same comparison harness.
- The existing read-adapter/scanner instruction bytes and relocations, all
  other 574 objects, manifest and composed import sets are unchanged. All 575
  R1 units compile without failures or duplicate strong symbols; imports remain
  175 application and 34 bootloader. `make sources-check` passes.

Five qualification variants compile; none selects an exact region. The
canonical plan remains unchanged at 3,881 source-built application bytes,
642,279 binary pull-through bytes and 248 resource bytes. The fresh hybrid
application equals stock with source completeness explicitly false.

Partition IO is modeled in direct cases. Integration executes the real C
FAL path while modeling the final flash driver and diagnostics. The partition
table/cache are seeded, so startup placement, physical flash, concurrency,
arbitrary corrupt pointers, helper-private frames, caller-clobbered registers
and flags are not established. This does not resolve the separate outer
sector-reader frame constraint. Complete source linking and full-source byte
identity remain outstanding; no G2 gate advances. The goal remains active.
