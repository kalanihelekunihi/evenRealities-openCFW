# Remaining defined-C FlashDB read dependencies

Current source inspection confirms that removing only the frame/register
constraints would change data consumed by the database readers:

- `runtime/native_flashdb_log_read.c`: the outer TSL reader passes an existing
  32-byte stack view to flash, ignores the adapter result, then decodes all six
  status slots and metadata. The adapter treats every nonnegative partition
  result as success, so its result does not prove a complete read.
- `runtime/native_flashdb_sector_read.c`: the 80-byte header read also ignores
  the adapter result before magic/status decoding. The protected stepper frame
  preserves a future nested TSL view. Its nested-read loop checks the TSL return,
  but the current TSL entry always returns zero.
- `runtime/native_flashdb_iterator.c`: iterator calls to TSL ignore its return
  before using record time/status. Changing only TSL's error return cannot
  establish failure propagation throughout iteration.
- The FAL and FlashDB wrapper register constraints preserve stack words later
  consumed by these partial/non-writing reads. Their purpose is observable
  stale-memory behavior rather than hardware instructions.

A defined-C conversion must jointly specify ownership/initialization for both
scratch views, establish whether the selected driver reports exact byte counts,
and propagate incomplete reads through sector traversal and iterator search.
Successful complete reads should retain status/metadata order and record format.
Error cases need explicit C-only expectations; stock equality cannot prove a
new deterministic or fail-closed policy. Merely zeroing buffers or returning an
error from the existing TSL entry is insufficient.

This is a source-based dependency analysis, not a claim that error handling or
assembly removal is complete. Existing evidence is in
[flash-read-frame-review.md](flash-read-frame-review.md) and
[flash-tsl-c-review.md](flash-tsl-c-review.md). No flash sources changed in this
analysis. Physical flash behavior remains unverified.

The [FAL read completion repair](fal-read-completion-c-review.md) now splits requests at the confirmed16-bit provider limit and propagates nonzero provider status as-1. This makes lower status failures visible to the FlashDB adapter, but does not make its upper callers consume them. Physical completion and arbitrary provider correctness remain unproven.

The [defined C read-path review](flash-defined-c-review.md) supersedes the scratch/frame and error-propagation dependencies above: TSL/sector scratch is initialized, read admission requires exact counts, nested failures propagate and all three iterator calls check failure before decoding. The iterator remains assembly; final physical behavior and complete normal-route integration remain unverified.

The [C time-range iterator](flash-iterator-c-review.md) now removes the retained iterator assembly. Normal-entry comparison covers all three TSL call sites, including forward and reverse search. Physical flash and final linking/boot remain open.
