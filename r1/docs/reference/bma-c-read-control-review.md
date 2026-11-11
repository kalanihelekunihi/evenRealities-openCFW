# R1 Bosch read-control function in C

The read-control function at stock `0x54534` now uses C. It validates the
device before the output pointer and forwards ordinary register reads
directly. For register `0x5E`, it obtains the saved power byte, conditionally
disables power saving, rejects odd/excessive lengths or failed power setup
with -10, and chooses direct or chunked transfer using the live chunk limit.
Successful transfers restore power saving only when the reloaded saved byte
is exactly one. REA confirms this control flow and access order.

All 1,791 comparisons pass. The matrix covers ordinary/feature registers,
zero/odd/boundary/full-width lengths, feature/chunk limits, power values,
independent helper errors, null output and callbacks that change the exposed
scratch byte or context limits. Complete call traces, ordered context-limit
reads, data, final context and status match stock. Mocks poison r0–r3;
r4–r11, entry SP and callback eight-byte alignment pass.

The first C candidate had 11 mismatches because it retained an earlier power
byte across the transfer. A const volatile read view now forces both stock
reloads. The underlying object remains an ordinary byte so helper writes
through the exposed ordinary pointer remain valid. Before/after evidence
is bound in the JSON. This test allows callback retention during the byte's
active lifetime; it does not claim physical callbacks currently do that.

All helper entry points are explicit mocks here. The direct-read routine
with its scratch-buffer behavior and the identity probe retain assembly;
their instruction bytes and those of the power getter are unchanged. No
physical bus/power-state, complete fault, timing, private-stack or byte-
identity claim is made.

All 561 R1 units compile and both compositions pass with unchanged 238/34
application/bootloader unresolved sets and no duplicate strong symbols.
`make sources-check` passes for both device trees. No source-plan selection
or workflow gate changed.

[bma-c-read-control-review.json](bma-c-read-control-review.json) binds source,
build, native/candidate bytes, REA results, the initial reload failures and
ignored probe artifacts under `build/goal-r1-bma-read-control/`.

The later [identity-probe review](bma-c-identity-review.md) replaces that
probe with C; direct transport scratch handling still retains assembly.
