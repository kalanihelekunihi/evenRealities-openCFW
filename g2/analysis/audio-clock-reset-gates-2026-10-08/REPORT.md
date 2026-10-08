# Clock-reset gates and retained-state reinitialization

[Readable partial-path C](../../components/audio/clock_reset_gates_offline/gates.c), [interfaces](../../components/audio/clock_reset_gates_offline/gates.h) and [source-guided pseudocode](pseudocode.md) pass **392 comparisons against the exact ELF**:361 gate/bitmap/epilogue block fixtures plus31 complete original-function gated-path fixtures. [Exact validation](exact-build-validation.json), [tests](verify.py), [results](results.json), [complete annotated stock disassembly/calls](disassembly-evidence.txt).

## Newly verified side effect

Function0x44B158 requires reset register0x4000885C bit1 clear and retained0x40008858 high16 equal0x5AF0 before considering active recovery. Even then, low-six request bits allzero skip recovery. Regardless of those gates, the function **writes retained state0, rereads it, and installs high16 signature0x5AF0**. Request flags are consumed/reset even on a power-on or invalid-signature path. The read-modify-write sequence is preserved rather than collapsed into one store.

The new full gated-path fixtures execute original0x44B158 to return and compare every observed write in0x40000000..0x40021FFF, including the retained register. All31 produce only the two reinitialization writes, no active-recovery calls. Predicate tests cover wrong/valid signatures, reset-bit variants and every low-six request bitmap with unrelated high bits. Native gated helper has an explicit precondition: recovery must be skipped; it is not a replacement for the complete clock-reset function.

This tightens the prior common-suffix evidence: those tests executed the actual original helper, but their write hooks did not include0x40008858. The prior report's “gated out” language applies to **active recovery only**, not retained-register side effects. Its old seals are preserved; this additive batch directly verifies the omitted side effect.

## Practical implication and limits

CFW startup/clock diagnostics should read or log retained clock-request state before invoking this routine: afterward it contains a fresh signature and cleared requests, even if recovery was ineligible. This does not demonstrate that any requested hardware clock was successfully recovered. The active path at0x44B1D0 still needs source-to-instruction matching and readiness fixtures; source outlines three staged enable/reset/revert phases. No physical clock trace or patch-safety claim is made.

All **1359 prior sealed entries**,110 audit inputs,four checkpoints and root index were verified before additive sealing. No commits, staging, production changes or device writes. These helper bodies model stock blocks; full source recovery and byte-identical OTA remain incomplete. [Current navigation and source-lead boundary](INDEX.md). Available pinned-source leads remain; source exhaustion has not been reached.
