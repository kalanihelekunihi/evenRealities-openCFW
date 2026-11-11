# Clock update and pending setter without assembly constraints

Both entries in `native_time_update.c` now use ordinary C. All inline assembly, fixed-register declarations and forced private frame geometry are removed. The existing clock state, registration and backend remain canonical.

The pending setter stores one byte at offset 11 and returns 1. The adapter retains the full incoming offset comparison, conditional calendar clears, raw pending-byte XOR decision and live backend/context reloads after get. Its volatile cached pending decision survives callbacks that change shared registration. No null-backend guard is invented.

Clang and license-free GCC each pass 16,496 adapter comparisons and 4,096 setter comparisons: **41,184 pairs total**. Tests execute actual native/source snapshot and memory-clear helpers, check callback arguments/order, shared state, return status, saved registers, restored/aligned stack and interrupt masks. They cover every pending-byte value, signed offset boundaries, exposed-slot replacements and 32 matching null-backend faults per compiler. An independent oracle checks the setter's exact byte effect. Seven compiled defects are rejected.

The fixture tracks the actual snapshot output pointers for mutations. It does not require a fixed compiler stack offset or incidental caller-scratch values. Those earlier requirements were instruction-matching constraints and are superseded for the current C build target. Physical RTC behavior, concurrency and arbitrary private-stack aliases remain unverified.

The normal 893-unit R1 build passes without failures or duplicate strong symbols. All 882 other nongenerated source/object pairs, the manifest and strong symbols remain unchanged. Imports remain 74 application and 22 bootloader; no persistent state is added. The tested Clang object equals the normal-build object. Source-plan/cache files remain unchanged; no new byte-identity qualification is claimed.

This is relocatable composition rather than a bootable firmware image. See [the evidence receipt](time-update-pure-c-review.json) for hashes, exact contracts, tests and limitations.
