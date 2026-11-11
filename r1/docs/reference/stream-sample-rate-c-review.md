# R1 sensor sample-buffer rate conversion in C

The stock helper at `0x7d0d8` (122 code bytes) now has one C candidate,
`r1_stream_sample_rate_copy`, in `runtime/native_stream_sample_rate.c`.
It is a dependency of the still-unimplemented object-registration body.
[Machine receipt](stream-sample-rate-c-review.json).

The helper rejects null source/destination, zero sample width or zero rates.
It divides source bytes by sample width, clamps available samples to source
rate, and computes destination count using the native rounded unsigned
32-bit multiply/add/divide sequence. Count is clamped to destination rate.
Each destination index selects `(i * source_rate) / destination_rate`, with
native 32-bit multiplication and a clamp to the last available sample. Return
value is count times sample width, also in native 32-bit arithmetic.

Each sample is copied separately through the existing overlap-safe native
memory-move interface. The sequential order matters when destination writes
change later source reads; a single whole-buffer copy would change behavior.
Address offsets use explicit unsigned arithmetic rather than undefined C
pointer arithmetic across unrelated objects. No interpolation, extra buffer,
heap allocation or changed rounding policy is introduced.

Verification passed 2,616 paired stock/C cases plus 200 cases executing the
actual native and C memory primitives. The tests compare an independent integer
oracle, ordered copy arguments and contents, return values and the entire
seeded RAM region. Cases cover zero/invalid inputs, rate/width boundaries,
unsigned arithmetic overflow, partial samples, up/down conversion, overlapping
and identical buffers, and interrupt masks. The copy-provider frame is 40 bytes
in both implementations. Five mutants were rejected: missing rounding, wrong
index divisor, wrong copy width, wrong returned byte count and wrong empty
result. Production replay passed again after the negative controls.

Tests are bounded to RAM-safe addresses and copy counts. Huge metadata values
are included where the decoded operation remains bounded or returns zero;
this is not exhaustive large-memory or fault behavior validation. Private
caller-stack aliases, timing, APSR and caller-saved registers are excluded.
In particular, stock additionally saves incoming R12; this candidate does not
claim that extra non-ABI register preservation. Internal primitive frames and
return-register differences are not conflated with the matched outer frame.

All 609 manifest units compile and both relocatable compositions pass without
failures or duplicate strong symbols. All preceding 608 objects are identical.
No imports are added or resolved: totals remain 168 application imports and
34 bootloader imports. The object-registration C provider is still absent,
so it is not yet wired to this helper through a complete C call chain.

The scoped qualifier selects no executable bytes. The canonical source plan
remains unchanged, and the fresh hybrid matches the locked application with
4,271 source-built bytes, 641,889 executable pull-through bytes and 248 resource
bytes. Actual registration integration, live sensor data, source-only linking,
candidate byte identity and physical hardware operation remain unfinished.

The subsequent [object-registration body](stream-register-object-c-review.md)
now calls this converter and replays both actual bodies together. Its deeper
timer/dispatch and architectural boundaries remain open.
