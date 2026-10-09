# SysTick full extents independently verified

Both candidates pass. [Machine verification](SYSTICK-EXTENTS-VERIFICATION.json), [read-only parser](systick_verify.py), [candidate receipts](../touch-systick14-literal-extents-2026-10-09/results.json).

The existing public-source object hash matches the system-interface receipt and candidate receipt. The locked target hash matches. The prior independently verified compiler/configuration and header receipts apply unchanged, with CY8C4046FNI_T412 retained. No build was repeated.

Cy_SysTick_Enable [0xA620,0xA638) is exactly24bytes:20instruction bytes followed by4literal bytes. Its original LDR at0xA620 addresses0xA634, which contains0xE000E010. Cy_SysTick_SetClockSource [0xA638,0xA650) is exactly24bytes:18instruction bytes, c046 two-byte alignment, and4literal bytes. Its LDR at0xA638 addresses0xA64C, also0xE000E010. ELF $t/$d boundaries independently agree; the code ends in BX LR before either pool. All recorded instruction bytes, literal references and full-span hashes verify. Both sections are relocation-free, adjacent without overlap, and overlap no other selected historical span. Their register-write pseudocode agrees with the recorded instructions: Enable uses two separate read-modify-writes; SetClockSource updates bit2 from argument bit0. No physical timing, interrupt delivery or timer execution follows from this static evidence.

Eligible comparator increment:48bytes (38instructions,2alignment,8literals) and2functions. Reviewed aggregate arithmetic is2320+48=2368bytes across25functions and seven source translation units. Finite54-entry census becomes25reviewed+29remaining:23relocation/extent boundaries,5absent sections,1inline-emission contract. Canonical ledger edits remain the owner's responsibility. These are bounded comparator counts, not whole-firmware completeness or byte-identical bundle completion.

Audio comparisons were not repeated or re-audited for this request. No changes outside the assigned audit directory, device access, or Git mutations.
