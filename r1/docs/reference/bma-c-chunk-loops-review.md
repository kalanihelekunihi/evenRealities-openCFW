# R1 Bosch feature-transfer loop control in C

The two 120-byte naked assembly chunk loops at stock `0x87E58` and `0x976B8`
now express their transfer control flow in C. The initial quotient/remainder
are computed before address reset. Full iterations continue after errors;
only successful transfer plus address increment advances the 16-bit buffer
offset. Later iterations overwrite earlier status. The remainder runs only
if the last full iteration succeeded, and final address reset runs only if
the current status is zero. Live chunk-size reloads retain their stock order.
REA confirms this behavior.

The two stock UDIV operations per invocation remain in a small inline-assembly
helper. C division by zero is undefined, while hardware division behavior
depends on DIV_0_TRP. The helper avoids introducing that C undefined behavior;
this is a reduction of assembly to the hardware-specific operation, not a
claim that these functions are pure ISO C. Zero divisors match stock in the
emulator's default configuration. Enabled divide trapping and full fault
snapshots are not validated.

All 1,322 comparisons pass across both directions. They cover zero/full/tail
lengths, transfer and increment failure patterns, initial/final reset errors,
overwritten earlier errors, callbacks changing the chunk size, zero divisors,
16-bit offset wrap and 32-bit pointer wrap. Complete ordered size reads and
dependency call arguments/statuses, final size and return value match.
Callbacks poison r0–r3; r4–r11, entry SP and eight-byte callback alignment pass.
Private stack depths differ and are recorded separately.

The normal compiled objects run with transfer/reset/increment entry points
bound to explicit mocks. No physical bus or feature-memory access is tested.
The other functions in the source unit retain their previous instruction
bytes. All 561 R1 units compile and both compositions pass without duplicate
strong symbols, with unchanged unresolved sets of 238 application and 34
bootloader. `make sources-check` passes for both trees. No source-plan
selection or workflow gate changed; byte and timing identity remain open.

[bma-c-chunk-loops-review.json](bma-c-chunk-loops-review.json) binds source,
build/native/candidate hashes, REA results and ignored probe artifacts under
`build/goal-r1-bma-chunks/`.

The subsequent [feature integration review](bma-feature-integration-review.md)
executes the actual C address controls and checker in 636 additional cases,
moving the mock boundary down to direct register I/O.

The inline division helper described here is superseded by the
[shared zero-divisor primitive and C arithmetic](divide-zero-c-review.md).
