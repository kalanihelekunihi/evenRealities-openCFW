# Source bounded formatter runtime

`build_native_formatter_runtime.py` links public `snprintf` and `vsnprintf`,
the recovered parser, arithmetic and output helpers with no undefined symbols.
Formatting/termination logic is C. Small C-compilable assembly adapters preserve
the native variadic argument stream and outer 40/24-byte frames, including
context words restored in r2/r3. They contain no retained executable blobs.

Direct wrapper tests pass 2,532 cases, including1,096 matching faults and 36
frame-alias cases. Raw r0/r2/r3 and restored callee registers agree; r1 is zero
for nonzero capacity and differs in 24 zero-capacity cases. The 225-case complete
formatter experiment also matches. Device-info passes 65,637 cases with actual
source formatting; the broader 2,896-case protocol/battery graph removes the
formatting fixture and preserves its existing encoder/CRC/fragment/TX checks.

This is bounded source behavior evidence, not full firmware or byte identity.
Private worker/parser frame aliases, zero-capacity scratch registers, APSR,
other compiler/LTO behavior, full startup/configuration, hardware and exact
instruction identity remain gated. The standalone device-info experiment
models lower response; the larger graph models allocator/queue/connection and
hardware endpoints. Stock metadata strings remain stock evidence, not an
OpenCFW release identity.
