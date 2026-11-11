# Motion batch producer in C

`r1_motion_thirty_sample_batch_producer` now uses C instead of naked
assembly. Stock entry `0x6f4a0` accepts a nonnull destination and length
188, requests 30 samples and returns zero after a negative FIFO result.
For a nonnegative result it zeroes eight calibration bytes, invokes the
calibration reader, truncates the result to a 16-bit count, adjusts those
samples, stores count at offset 180, calls the clock, stores timestamp at
offset 184 and returns 188. The context argument and calibration return
value are ignored. REA/Ghidra confirms that sequence.

A packed packet layout asserts the native size and metadata offsets.
The existing C adjustment helper now uses packed may-alias halfword
views instead of bytewise load/store helpers. This matches native access
widths and preserves axis order, unsigned 16-bit wrap, per-sample bypass
queries, and the all-`0xffff` calibration sentinel that clears all three
offsets. Volatile accesses preserve count-before-clock-before-timestamp
ordering and changes made by callbacks.

Stock/source comparison passes 604 scenarios with the actual C FIFO
dispatcher and adjustment helper executing. Provider FIFO, calibration
read, bypass getter and clock are mocked and clobber caller-saved
registers/flags. Cases cover zero, 30, overreported and truncated counts;
negative results; partial calibration writes and sentinel values;
changing bypass decisions; offset/sample changes between iterations;
metadata changes during the clock; invalid lengths/null destination;
unaligned packets; and interrupt masks.

Probes compare ordered selection, sample, offset and metadata accesses
with their actual widths, callback traces, full output buffers, return
values, callee-saved registers, restored stack and masks. An independent
byte oracle checks sample arithmetic and final metadata. Offset traces
cover their logical lifetime after calibration and before the clock;
private saved-register reads during epilogues are excluded.

The producer trusts the provider count as stock does, then truncates it
to 16 bits. Overreported-count cases use a larger controlled buffer to
compare existing behavior; no new cap is inserted. The C producer is
94 bytes plus an 84-byte adjustment helper, versus the stock 154-byte
combined instruction body. All other stream function bodies remain
unchanged. Calibration-read and mixed-return interrupt assembly remain.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-motion-batch/report.json`; imports remain 227
application and 34 bootloader. Physical sensor/storage operation, timing,
complete fault state, final linking and byte identity remain unverified.
No source-plan selection or G2 workflow gate changed.

[Machine-readable evidence](motion-c-batch-review.json) binds source,
manifest, build/native hashes, REA observations and ignored probes under
`build/goal-r1-motion-batch/`.
