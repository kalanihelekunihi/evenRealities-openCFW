# Independent review 2601: transition state predicate

**Result: PASS_SCOPED.** `accepted` remains false.

Candidate artifact and source hashes match. The body `[0x41F3F0, 0x41F424)` digest is correct. A replay copy redirected to a fresh output directory passes all 36 fixtures. Independent Thumb disassembly confirms the predicate: gate byte must be nonzero; a fresh register read must have a nonzero low nibble; a fresh read must have bit 31 clear; a third fresh read returns the inverse of bit 30.

The replay accurately asserts read counts—one gate read, followed by one, two, or three word reads depending on early exits—as well as result, PC and SP. No writes occur. Stable memory is used, so the effect of concurrent changes between reads is not demonstrated. Hardware meaning and caller ownership remain outside scope; no canonical admission is claimed.
