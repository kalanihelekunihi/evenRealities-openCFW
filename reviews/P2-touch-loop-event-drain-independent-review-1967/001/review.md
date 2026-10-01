# Independent review 1967 — loop event drain

**Result: PASS_SCOPED.** Candidate `touch-loop-event-drain-3a80-1960/001`; receipt SHA-256 `8a77754f975c11e3bcf792ab9bf3189838413a5afead1b435a04ef3023a07de7`.

Source/artifact pins match. Body [0x3A80,0x3ADC) is 92 bytes/40 instructions; literal pool starts at 3ADC. Isolated replay passes all 36 combinations and exactly matches replays.json.

Disassembly verifies PRIMASK save/disable through 4492, snapshots two byte flags and a halfword, clears both bytes before restoring PRIMASK via 449A, then calls 404C only when first snapshot is nonzero and 3A38 only when second snapshot is nonzero. The 404C result is ignored. The 3A38 return selects either logger call and its corresponding literal/temporary arguments.

Fixtures vary each flag over 0/1/255 and second-helper return over 0/7, asserting snapshot and ordered side effects, halfword stack argument, call order/arguments, frame and restored PRIMASK. R0 is correctly described as incidental, not a defined result.

The logger and both callbacks are controlled; callback mutation and concurrent flag changes are not exercised. No physical event semantics or canonical admission is established.
