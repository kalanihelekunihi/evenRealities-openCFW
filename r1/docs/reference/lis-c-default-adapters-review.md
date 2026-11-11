# R1 LIS2DW12 default bus adapters in C

The default read/write callbacks at stock `0x7F17C` and `0x7F188` now use
C. Both ignore the context handle, force bus address `0x18`, forward the
register/buffer/length, discard the bus helper result and return zero.
Signatures match the pinned ST callback types: byte register, 16-bit length,
and const write buffer. The existing assembly request builders now have
explicit four-argument declarations; their instruction bodies are unchanged.

REA confirms the fixed-address calls and forced success return. All 576
modeled comparisons pass through the actual request-builder bodies, with
two handles, six registers, six lengths and four dispatcher statuses for
both directions. Every 20-byte read/write record matches stock, including
all zero-filled bytes, pointer offsets and lengths. Device/op/reserved
dispatcher arguments and final destination data match. Callback mocks
poison r0–r3; r4–r11 and entry SP are preserved. Dispatch scratch and callback
SP both remain at entry SP minus 48 in this build.

Each adapter remains 12 bytes, but its instruction bytes differ from stock.
The request builders, device-ID getter and identity probe have unchanged
allocated function bytes. Private spill contents, complete fault state and
cycle identity remain unproven. The analysis executable maps the locked
memory-clear helper and intercepts device dispatch; this is an ignored probe,
not a firmware source provider. No physical bus or sensor behavior is tested.

All 561 R1 units compile; both compositions pass with unchanged 238/34
application/bootloader unresolved sets and no duplicate strong symbols.
`make sources-check` passes for both trees. No source-plan selection or
workflow gate changed.

[lis-c-default-adapters-review.json](lis-c-default-adapters-review.json)
binds source/object/native bytes, the build report, REA results, comparison
matrix and probe hashes under `build/goal-r1-lis-default/`.

The subsequent [motion request conversion](motion-c-requests-review.md)
replaces the assembly request builders and checks the real dispatch path.
It also records compiler inlining changes to the default callback bodies.
