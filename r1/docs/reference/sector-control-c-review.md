# R1 sector header and traversal control in C

The later [sector stepper](sector-stepper-c-review.md) supersedes the partial
dispatch status below. This receipt records the earlier header/advance round.

The sector reader at `0x87c24` now uses C workers for header validation,
status decoding, metadata selection, bounds setup and traversal arithmetic.
The native assembly scaffold still owns provider calls, loop dispatch,
diagnostics and assertions. Its instruction/alignment span falls from 360
to 228 bytes. This is a partial extraction, not a complete C sector entry.

REA observes the contiguous 360-byte stock body through `0x87d8b`. Evidence
is bound to locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The existing function-name data owner is unchanged. Retained assembly literals
are explicitly aligned after shortening the scaffold.

The earlier whole-kernel attempt changed the nested log-reader stack location.
This extraction keeps header and nested TSL calls at their native stack
positions. The outer 104-byte local region remains at caller `SP-128`; the
nested 32-byte read view remains at caller `SP-176`. Before entering either
C worker, the scaffold temporarily reserves 48 more bytes, placing C-private
frames below the future nested view. It releases that reservation before
calling the providers. Failed reads therefore retain their existing bytes.

The C workers preserve volatile read/store order when views overlap. In
particular, the second length read precedes the updated traversal-address
store. Error paths retain native diagnostics and assertion loops. Bounds and
alignment arithmetic retains unsigned wrapping rather than adding guards or
initializing unavailable flash bytes.

[Machine-readable evidence](sector-control-c-review.json) records 12,230
paired stock/C cases, separated by outcome:

- 11,820 return cases compare header magic, status combinations, metadata,
  partial/non-writing reads, aliased database/sector/header fields, traversal
  bounds, diagnostics, ordered shared accesses, outer frame, nested raw bytes,
  result, saved registers, SP and interrupt masks.
- 170 cases reach the same native assertion after matching diagnostics.
- 240 corrupt-size cases match through a 16-read prefix. They do not prove
  termination of the extremely long stock traversals.

The real C preparation/advance, read adapter, status scanner and TSL control
execute together. Partition reads, printf and the database-path getter are
modeled. Removing the protected stack reservation and delaying the second
length read are both rejected by the comparison harness.

All other 574 object hashes, the manifest, data owner and composed import
sets remain unchanged. All 575 R1 units compile with no failures or duplicate
strong symbols; imports remain 175 application and 34 bootloader.
`make sources-check` passes. Five qualification variants compile, with no
exact region selected. The canonical plan remains at 3,881 source-built
application bytes, 642,279 binary pull-through bytes and 248 resource bytes.
The fresh hybrid application equals stock; source completeness remains false.

C-private frames below the nested view, temporary saved/unused words between
that view and outer scratch, caller-clobbered registers and flags are excluded.
This receipt does not establish full FAL/device execution, physical flash,
concurrency or arbitrary corrupt pointers. Complete source linking and full
source byte identity remain outstanding. No G2 gate advances; the goal remains
active.
