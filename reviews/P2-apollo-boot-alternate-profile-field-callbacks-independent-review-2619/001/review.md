# Independent review 2619: alternate-profile field callbacks

**Result: PASS_SCOPED.** `accepted` remains false.

Artifact, source, body-span, and literal-pointer pins match. I redirected a replay copy to a fresh destination and all 108 cases passed. Disassembly agrees: the first leaf skips on a zero gate; otherwise it uses an unsigned saved-word threshold of 7, subtracts 6 for eligible values (or chooses zero), then inserts the low 10 bits into the control word. The second leaf clears timing bits 0–5 and sets auxiliary bits 15–16 to 1. Both return zero.

The replay checks ordered writes and widths, return, PC and SP. The saved word is read again on the eligible branch; stable fixture memory means mutation between reads is not exercised. Physical register interpretation and callback ownership remain unresolved. No canonical admission is claimed.
