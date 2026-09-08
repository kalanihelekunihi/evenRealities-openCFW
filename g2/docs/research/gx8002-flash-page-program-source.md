# Page-program wrapper candidate

Source runtime_gx8002_flash_page_program.c reconstructs package0x15c48.
Zero length returns before reading state or invoking helpers. Otherwise the
wrapped address+length must not exceed usable size. The routine waits once,
computes address&255, enables writes, and snapshots the program callback.
When wrapped length+offset is at most256 it invokes that callback once.
Otherwise it programs256-offset bytes, then loops over unsigned remaining
length in at-most256-byte chunks, enabling writes and reloading the callback
for each. Callback return values are ignored; accepted requests return zero.

Native -Os compilation initially128/120 bytes; -fno-shrink-wrap reduces this
to124. -O2 gives136 (132 without shrink wrapping), -O1 gives140, and -Oz with
no shrink wrapping gives124. Individual disabling of loop-invariant movement,
GCSE or expensive optimizations under -Os did not improve128. The current
candidate is four bytes oversized and is not registered for admission.
Decoded boundary/alias/ABI/callback verification and fitting remain pending.
Physical write behavior and valid buffer constraints are not yet qualified.

Size resolved with -Os -fno-shrink-wrap -fira-algorithm=priority:120/120 bytes
and original32-byte frame. Other allocation/scheduling/pass probes did not
improve124. No source behavior changes were needed for the allocator change.
Initial decoded comparison passes640 cases covering first-page offsets,
256-byte boundaries, zero length, wrapped address/buffer arithmetic, bounds
rejection and dynamically replaced callback pointers with two clobber seeds.
Wait/write-enable order, callback arguments/return ignoring and preserved
registers match. Large length-plus-offset overflow and rejection tests remain
before admission; physical buffer validity is not established by the model.

Expanded qualification adds eight overflow/clobber cases. Wrapped bounds and
length+page-offset sums can accept a single callback whose length approaches
UINT32_MAX; decoded stock and source agree. Six tests check zero-length state
avoidance, bounds rejection, partial/full/final-page splitting, enable/wait
counts, callback reload enforcement and frame rejection. Prepared reviewed
admission adapter/report;640 boundary cases plus eight overflow cases pass.
Package registration and full macOS integration are next. No hardware writes.

Integrated page-program wrapper on macOS. Native codec build passes all183
tests; full EVENOTA build and verify-artifacts pass under apple-clang.
Page-program contributes120 C bytes without envelope fill, with640 decoded
boundary cases and eight overflow/clobber cases. Current ownership:6938
compiled C,2040 source data,80 metadata,296 fill,316738 retained bytes.
There are108 functions/124 code occurrences and16 data regions (140 total).
Codec SHA-256:3c3009eb0bcc3f4c9a36f033bfc83ad059beccb0d3d19e7ef6a2937444edf164.
Package SHA-256:b0e409bbbc10c96c8f85af87a50adefac582365ed581593254b42bd00d5113a6.
The manifest pins the new candidate; matching that pin is not vendor binary
identity or hardware qualification. No hardware operation was performed.
OTP callbacks, device/interface data, BSS/startup ownership, other codec code
and the other firmware components remain. Full source-only goal stays active.
