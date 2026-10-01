# Independent review 1993

**Result:** PASS_SCOPED.

- All candidate and source pins match the receipt; the failed /001 attempt remains untouched.
- An isolated replay reproduces all 24 rows exactly. The busy state-one branch calls A528 (not A58C), its modeled completion clears the readiness bit after the selected waits, and the original readiness/mask/event code executes.
- Recorded transitions match modulo-2^32 decrement: zero counter with zero predicate wraps to 0xFFFFFFFF and remains state 1; a decrement to zero selects state 2/counter 160; nonzero predicate reloads 640 and remains state 1. SP and initial PRIMASK are preserved.

**Limits:** A528 completion and sensor/predicate/timing helpers are controlled; only the specified bounded waits are exercised. This does not establish physical event delivery, unbounded-wait behavior, state transitions outside these fixtures, or whole-loop completeness. No canonical admission is made.
