# Parent 32b61c optional callback register review

Status: prepared adapter remains unselected pending callback contract review.

The authenticated instruction range 32b774..32b7c4 calls 3246c0,
then 312918, and optionally calls the pointer loaded from 801a14. Between
312918's return and that optional JL, the native body changes R0 and R1
but does not write R2 through R12. It changes callee-saved context registers
R13 through R16 for its own state.

The prepared adapter captures and restores R2 through R7, which its target
disassembly and six-canary host fixture verify. Its optional-call wrapper
uses R12 as the snapshot address. Therefore those checks alone do not
establish equivalence for a callback that consumes native incoming R8
through R12, or depends on additional native context. No producer or
complete callable contract for the pointer at 801a14 has yet been accepted.

The native 3246c0 call also has a delay-slot byte store at 32b778. The parent
C candidate stores the corresponding selected byte before entering its
wrapper; that ordering must be justified against the child-visible state
and asynchronous or aliased mutation contract before admission.

These gates do not prevent integration of the independently reviewed full
312918 body and the two timing children. They prevent calling this parent
adapter a fully qualified native ABI replacement.

Evidence: pinned ARC objdump with cpu=em,dsp, native image base 302400,
range 32b774..32b7d4; associated-regs-target/receipt.json and prepared
init_associated_cycle_ambient_r2.c. This is source and instruction evidence,
not live ARC or hardware execution.
