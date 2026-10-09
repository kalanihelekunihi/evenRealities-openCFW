# UART callback through existing PCM2.2 transition children

Reused already-sealed native transition/TON bodies within the enclosing UART→PCM2.2 callback→planner→apply/selector chain. **32 compositions recorded:24 have complete read/write trace equality;8 have a source-only extra timer-status read.** All32 match ordered MMIO writes, published target/trim state, cached profile fields, defined common-provider arguments and masks up to their boundary. [Full results and differences](results.json), [exact receipt](reproduction-receipt.json), [successor ledger](INDEX.md). This is **partial access-trace validation**, not32fully equivalent PASS cases.

Eight paths complete under the synthetic fixtures. Twenty-four stop before real delay provider4807A0 with argument50, after selected transition publication/register work. No delay success or physical settling is fabricated. The native27-entry transition table is a fixture relocation of authenticated initialized DATA to corresponding compiled function symbols, not firmware patching or retained executable blobs. Original table targets execute stock bodies on the original side. Shared source headers/bodies are unchanged and hash-pinned.

## Real read discrepancy retained

For temperature selector2/3 and CPUstate0 (UARTdomains11/14, incomingPRIMASK0/1), stock reads400083E0 once at the affected step while source reads it twice consecutively before the same TON/register operations. This is not the previously corrected interrupt-clear inference: it is a **direct ordered-access trace difference** in every affected fixture. Both sides have the same stable fixture value0 and subsequent ordered writes/state/provider arguments, but equality under stable values does not prove behavior with a changing or side-effecting register.

Source sequence0 checks timer-active for a cancellation condition and then its sharedfinish_previous helper rereads timer-active. The corresponding stock path reuses its prior condition. Preserving stock snapshot/read sequencing is an actionable successor reconstruction requirement. This batch does not edit the sealed transition implementation or claim it is production-safe. Earlier transition tests largely validated final state/ordered writes; this composition adds the stricter read sequence evidence.

## What progressed

Both native planners and PCM2.2 apply/selector now reach real native transition/TON bodies within actual enclosing control flow, beyond the previous before-child cut. Synthetic calibration words explicitly vary by profile. Common delay/timer/clock providers remain actual entry boundaries; selected delay50 is an intended microsecond API argument from existing evidence, not measured elapsed time. Active transition completion, actual timerIRQ/physical power and scheduler handover remain unproven.

The full transition family already had readable source and bounded comparisons in [prior transition recovery](../audio-transition-producers-closure-2026-10-08/REPORT.md); these bodies are reused, not falsely counted as new opaque recovery. Existing revision producer, startup sentinel and initialized-ITCM evidence are reused. The uncachedFFFFFFFF trim word does not identify runtime silicon/family.

ISR notifier now proves ready/pending-ready lists and software wake flags only; it does not establish exception delivery. Codec UART3 role remains GX8002 control/DFU. Ring oldest-byte eviction and stream rejected suffix remain synthetic pressure. No Git mutations, commits, production/device/shared-state edits.
