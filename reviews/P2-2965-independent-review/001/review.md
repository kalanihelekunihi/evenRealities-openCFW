# Independent review 2965/001

**PASS_SCOPED**; `accepted` remains false.

All 640 fixtures pass in an isolated replay. Source and body pins match for the caller, decoder, and interrupt-save helper; replay hashes match. The grid varies two operation words, four categories, five requested/current bytes, four flags, two clocks, and two incoming PRIMASK values. With equal requested/current state, the transition helper is skipped while the original decoder still runs and publishes exactly two global words. Status zero, R4–R12/SP, and PRIMASK restoration pass.

Unequal-state transitions, other snapshots, aliasing/volatile changes, and hardware effects remain outside scope.

Candidate receipt SHA-256: `bef39ee3a3ddca4114d54ef8b3d395694f62357d02de582cd0e579d3a9b513cd`.
