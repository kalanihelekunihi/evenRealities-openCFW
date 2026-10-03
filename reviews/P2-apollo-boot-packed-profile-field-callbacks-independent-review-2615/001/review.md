# Independent review 2615: packed-profile field callbacks

**Result: PASS_SCOPED.** `accepted` remains false.

The source and artifact hashes match. All three code-span hashes are correct; adjacent bytes at `0x42BD9C..0x42BDA0` and the literal at `0x42BDE4` are outside the bodies. An isolated replay copy with a fresh destination passes all 36 fixtures.

Disassembly confirms the three operations: insert 6 into bits 25–29; conditionally copy state+32 bits 7–16 into control bits 0–9; and conditionally copy state+104 bits 2–7 into timing bits 0–5, followed by a fresh state+104 read to copy bits 0–1 into auxiliary bits 15–16. Ordered writes, both gate outcomes, three source patterns, zero/all-one target words, return zero, and SP match the replay assertions.

Fixtures use distinct stable RAM regions. Aliasing, mutation between reads, physical interpretation, callback installation ownership, and enclosing reachability are not established. No canonical admission is claimed.
