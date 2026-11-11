# FlashDB time-range iterator in ordinary C

The iterator at stock `0x63ad8` now uses C for sector traversal, timestamp binary
search and record callbacks. Its assembly implementation is removed. The C
version preserves direction selection, signed comparisons, midpoint rounding,
cached-sector copying, inclusive ranges, empty records, callback ordering and
live unlock-callback reloads. An exact timestamp match bypasses the additional
reverse probe, preserving the native read sequence.

TSL failures retain the preceding review's unlock-and-return behavior. Local
records are initialized, and a sector read receives a defined fallback cursor
before it can fail without writing. No persistent state is added.

Verification passes 9,903 normal-entry stock/C comparisons. Every one of the
392 native main-body instruction bytes executes, including all three TSL call
sites. Cases cover forward/reverse boundaries, exact and missing timestamps,
signed extremes, cached sectors, null callbacks, diagnostics, lock choices,
callback termination, live unlock replacement and record-address mutation.
Actual C traversal and memory routines execute; reads and callbacks are modeled.

Another 211 C-only cases verify failed reads, stack poison independence and
non-writing sector failures. All 13,944 traversal-helper regressions pass.
Four compiled defects restoring an extra reverse probe, ignored TSL errors,
a cached unlock callback and unsigned direction selection are rejected.

The normal open-source build compiles 852 units and composes both relocatable
payloads. All 841 other nongenerated objects remain unchanged. R1 manifest
validation passes. Imports remain 66 application and 22 bootloader symbols.

These checks do not establish physical flash behavior, full firmware linking,
startup or boot. Callback buffers remain borrowed and synchronous. Arbitrary
invalid pointers, private-stack aliasing, invalid bool return encodings and
concurrency are outside the replay. No fixed frame or interior-entry ABI is
preserved. Byte identity is not required or claimed.

[Machine evidence](flash-iterator-c-review.json) binds REA, sources, normal-entry
replay, negative controls and build reports. This supersedes the retained
iterator-assembly limitation in [flash-defined-c-review.md](flash-defined-c-review.md).
