# R1 QMA delay loop moved from naked assembly to C

`r1_qma_delay_units` in `native_qma_transport.c` now expresses its countdown,
primitive invocation, result and return flow in C. The native call boundary
is retained with `noinline`, preventing the retry path from absorbing the
helper. One four-byte MOVS/BEQ assembly primitive remains for the zero path's
observable flags; the hand-written push/pop frame and full assembly loop are
removed. The existing low-level countdown primitive remains unchanged.

REA confirms native entry `0x86e48` invokes `0x9a6a0` with 64,000 once per
unsigned input unit, doing nothing for zero. Raw instructions show that the
last primitive leaves R0 at `0xfffffffe`: subtracting three from 64,000 for
21,334 iterations produces -2. The C implementation returns this defined
word for nonzero input and zero for zero input; it does not read a void
function's caller-clobbered return register. Its compiled body is 26 bytes.
This size is not a byte-identity claim against the stock 28 instruction bytes
and adjacent four-byte literal.

Native zero input uses MOVS, preserving incoming C/V while setting N/Z.
Replacing it with a normal CMP would set C=1 and V=0. The small assembly
boundary preserves this contract while C owns the loop. The real countdown
and final C decrement preserve the native nonzero result flags as verified.

`build/goal-r1-qma-c-delay/verify.py` passes 181 paired cases (362 executions):
112 complete cases with units 0,1,2,3,5,10,100 crossed with C/V, Q and PRIMASK
states, plus 69 first-call checks including random full-width and maximum
unsigned inputs. Actual stock and C countdown primitives execute in the full
cases. The probe checks call counts, the 64,000-cycle argument, R0 result,
APSR flags, preserved registers, caller registers R1-R3/R12, stack restoration,
eight-byte call alignment and interrupt masks. Large counts stop at the first
primitive call; private frame bytes and intermediate allocation are excluded.

A deliberate variant replacing MOVS with CMP is rejected for zero units with
incoming C=0: stock ends with flags `0x40000000`, while the variant produces
`0x60000000`. The negative variant differs from current source only in that
zero-test instruction.

The current object also passes 1,536 stock retry comparisons. That separate
probe models the bus and delay boundaries, including 32 outcome sequences;
it checks the transport behavior rather than claiming a full electrical bus
execution. Seven unrelated functions in the same object retain their prior
instruction bytes. The full build
`build/sources-goal-r1-qma-c-delay-final/report.json` compiles 564 R1 units
without failures or duplicate strong symbols; imports remain 206 application
and 34 bootloader. `make sources-check` passes.
[Machine evidence](qma-c-delay-review.json) records the source, REA snapshot,
execution probes, negative control, retry results and build report hashes.

The canonical source plan is unchanged. Physical elapsed time and QMA behavior,
unbounded execution proof, final source placement and byte identity remain
unproven. G2 workflow gates are unchanged.
