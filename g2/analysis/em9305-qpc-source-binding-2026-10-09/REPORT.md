# Official QP/C source binding to EM9305 queue and scheduler

Finite question: which public queue fields and scheduler conditions are independently supported by the locked in-image bytes? Stop at unsupported vendor opcodes/IRQ behavior and producing configuration. No compilation, original instruction execution, SDK extraction, device activity or canonical mutation.

Official QP/C v6.5.1 pin416dcec8820b9cdb5827497e645d0d9375db53c6 is the provider comparator, not a newly proven producing checkout. GPL-3.0-or-later OR commercial notices apply. Source hashes match discovery's provenance. Three original ranges match its recorded hashes and were freshly decoded with native ARC binutils; instruction listings are retained.

## Queue initializer: full bounded field correspondence

QEQueue_init[0x310F5C,0x310F74) stores ring pointer at+4 and front event NULL at+0; writes the low byte of qLen to end+8. At0x310F64 it skips head+9/tail+10 clearing when the full incoming qLen is zero. It stores qLen+1 narrowed to a byte at nFree+11, reloads it and copies to nMin+12 in the return delay slot. These correspond precisely to official qf_qeq.c's conditional field operations. No assertion or length validation is present in this bounded routine.

Important edge: zero ring length still supplies one front-event capacity and leaves old head/tail bytes untouched. At qLen255, nFree wraps to0; this initializer alone does not establish that callers permit such a configuration. The 13-byte observable prefix is field evidence, not a claim about total structure padding or v4.2/v4.6 ABI compatibility. This is static source semantics binding, not newly rebuilt24bytes or new executable coverage.

## Scheduler: bounded correspondence, one unresolved instruction

QK_sched_[0x311634,0x31166C) uses root0x801394, loads a16-bit ready set at+6, then contains undecoded word0x3D2F1000 at0x31163E. Its produced priority is subsequently held in r13. The supported downstream instructions return0 when candidate priority is <= byte actPrio+0 or <= byte lockPrio+2; otherwise check candidate<17, use assertion ID410 at target0x3117D8 for an out-of-range candidate, and publish candidate to byte nextPrio+1. This agrees with official qk.c's <=active/<=lock/maximum16/nextPrio conditions. Delay slots are retained in the listing.

The ready-set operation is NOT proved to be the public QPSet_findMax or vendor log2p1 solely from downstream agreement. QK_activate_'s144-byte slice is authenticated/listed for follow-up, not interpreted as a completed provider comparison. There is no official ARC port in the pinned tree; vendor IRQ frames and producing compiler/configuration remain unresolved. The decoder's raw word is an exact stopping boundary for full scheduler semantics; need an authenticated vendor opcode definition or producing object/source for that operation. Timer wrappers remain a separate address-bound lead, not analyzed here.

Practical relevance: queue consumers must respect configured byte-counter bounds and front-event capacity; scheduler readiness is gated by both current priority and lock ceiling. Neither static binding establishes interrupt safety, live priorities, event delivery or physical execution. No global source exhaustion or source-complete firmware claim.
