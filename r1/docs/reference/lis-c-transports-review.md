# R1 LIS2DW12 read/write transports in C

The existing read/write transport candidates now use C instead of naked
inline assembly. Each loads the handle at context +12, then the callback
pointer at +4 for read or +0 for write, and invokes it with the register,
buffer and length unchanged. Access through a volatile context preserves the
two load operations and their ordering. No null guard, retry, status mapping
or read of the trailing private context field was introduced. Field offsets
remain compile-time assertions against the pinned ST header.

The write declaration now matches that header's `int32_t` result and four
parameters. This preserves negative transport statuses as machine return
values and removes the previous untyped, register-only C declaration.

REA inspected both 14-byte stock bodies at `0x757C4` and `0x759E6`.
Decompiler output omits forwarded arguments and treats the indirect tail
branches as unresolved calls; assembly supplies the handle-before-callback
ordering and actual argument preservation. The current Clang candidates
produce 20-byte bodies and preserve callback-entry SP, arguments and the
checked callee-saved registers. They are **not byte-identical**: Clang saves
r7/LR transiently where stock saves r4/r5. A GCC 9 experiment also differed
and was not adopted. No source qualification entry or compiler flag changed.

All 1,023 stock-versus-source transport/FIFO execution comparisons pass with
the actual canonical register frames and field helpers linked. Ten further
checks compare context-load order, mutation of the callback pointer during
the handle read, mutation of the stored handle during the callback-pointer
read, null/truncated contexts and invalid callback targets. Fault checks
compare access kind, address and size; they do not compare complete register
snapshots or private stack contents at the fault. The compiled null-access
behavior is bounded evidence, not a portable C guarantee for invalid pointers.

The burst, FIFO-reader and scratch-sensitive register-frame bridges retain
their existing assembly. Their incoming-register and stack-backed byte
contracts require separate analysis before a C replacement can be kept.
These two C conversions are intermediate candidates, not satisfaction of the
whole-firmware byte-identity target. Exact code generation, private spill
identity, fault-state identity, timing and physical hardware remain open.

Subsequent [burst](lis-c-burst-review.md) and [FIFO reader](lis-c-fifo-review.md)
reviews replace those two bridges with C under their own test scopes. The
scratch-sensitive register frames remain assembly.

A subsequent nine-variant Clang probe checked optimization/frame-pointer
settings, rejected fixed-register switches and experimental LLVM register
reservation settings. None produced the native 14-byte bodies; no tested
flag was adopted. This bounds that experiment rather than proving all
compiler strategies exhausted. The hashed result is linked from the JSON.

All 561 R1 units compile and both compositions pass. Undefined sets remain
unchanged at 241 application and 34 bootloader imports. Source completeness,
final firmware linking and workflow gates are unchanged.

[lis-c-transports-review.json](lis-c-transports-review.json) binds source and
report hashes, native and candidate instruction bytes, REA observations,
execution results and explicit limits. Probes and the neutral REA snapshot
remain under ignored `build/goal-r1-lis-c/`.
