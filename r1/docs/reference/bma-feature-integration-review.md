# R1 Bosch feature-transfer integration

All 636 integrated stock/candidate comparisons pass through the actual chunk
loop, address reset/increment, address arithmetic and device checker. The
candidate links the normal compiled C implementations from the existing
successful 561-unit R1 report. Only direct register read/write entry points
are replaced with controlled operations; the preceding isolated reviews
mocked more of this call chain.

The matrix covers both transfer directions, zero/full/remainder lengths,
zero and odd chunk sizes, address-boundary contexts, individual errors at
the first 24 direct operations, absent callback fields and a chunk-size
change during transfer. It compares complete ordered direct-operation
traces, returned status, final register/context state and hashes of the
entire 4,096-byte caller buffer and 8,192-byte modeled feature store.
Read/write payload hashes are included in the trace. Callback mocks poison
r0–r3; r4–r11, entry SP and eight-byte callback alignment pass. Scratch
pointers are normalized by role; private stack depth differences are recorded.

The feature store is an explicit probe model: address registers form a
12-bit word address, transfer starts at twice that address, and the 8,192-byte
store wraps. This models an inspectable data path; it does not independently
authenticate silicon addressing or validate a physical Bosch device. Failed
operations leave buffers/registers untouched and return the selected error.
Other device failure behavior, timing and enabled divide trapping remain
outside this check. No complete fault-state or byte-identity claim is made.

This extends the [chunk-loop review](bma-c-chunk-loops-review.md) and
[address-control review](bma-c-feature-address-review.md) without changing
firmware sources, source-plan selections or workflow gates. No new build
was needed: all three linked source/object hashes match that report and the
current manifest.

[bma-feature-integration-review.json](bma-feature-integration-review.json)
binds the sources, build report, register-model assumptions and ignored
probe hashes under `build/goal-r1-bma-integrated/`.
