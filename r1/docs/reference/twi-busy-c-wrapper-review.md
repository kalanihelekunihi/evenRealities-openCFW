# Software-TWI busy delay C wrapper correction

This review records the earlier excluded C-only candidate. The current
[source closure](twi-delay-tail-closure-review.md) qualifies the corrected
wrapper and admits it to normal composition. Historical results below remain
scoped to that earlier source and build.

The excluded `sdk_delay_busy.c` candidate now calls `r1_rtt_delay_cycles`
instead of implementing a volatile countdown on the stack. REA analysis of
stock wrappers `0x7a6dc` and `0x7a6ec` confirms that each tests the original
microsecond argument before shifting it left six bits and tail-calling its
subtract-three primitive. Thus a nonzero argument whose shift wraps to zero
still invokes the primitive. The C wrapper retains that distinction.

Stock primitives `0x9a640` and `0x9a650` have identical six-byte instruction
bodies. The existing source primitive is byte-identical to both and remains
aligned to 16 bytes. It uses supported assembly mnemonics to retain the
timing-sensitive loop. The new wrapper itself is ordinary C and compiles to
12 bytes with the current compiler.

The ignored `build/goal-r1-twi-busy-wrapper/verify.py` probe passes 1,608
three-way comparisons, executing each case against both native wrappers and
the compiled C wrapper: 4,824 executions total. There are 566 full-return
cases, with shifted arguments bounded to 65,536, and 1,042 cases that stop
at primitive entry to verify full-width wrapping and handoff. The latter
do not claim completion of large countdowns. Zero inputs return directly.
Checks cover the primitive argument, bounded final R0/flags, callee-saved
registers, SP/LR, interrupt masks, unchanged stack memory and absence of
data writes. The actual six-byte primitive executes in full-return cases
with nonzero inputs; it is not replaced by a mocked delay.

This is not wrapper identity: native nonzero wrappers load the primitive
address into volatile R1 and read its literal word. The compiled C wrapper
retains incoming R1 and has a different branch sequence. Physical bus/ADC
wait timing, complete register/fault equivalence and cycle identity remain
unproven. The candidate therefore stays excluded, and `r1_twi_delay_busy`
remains unresolved in normal composition.

All 562 R1 units compile without failures or duplicate strong symbols.
Both normal composition outputs retain their exact previous hashes; imports
remain 227 application and 34 bootloader. Source checks pass. Exact source,
manifest, native spans, REA analyses, output hashes and probe bindings are in
[the machine-readable review](twi-busy-c-wrapper-review.json). No provider
selection, source-plan qualification or G2 gate changes.
