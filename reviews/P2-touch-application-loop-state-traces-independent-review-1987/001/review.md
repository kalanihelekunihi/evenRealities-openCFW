# Independent review 1987

**Result:** PASS_SCOPED.

- Receipt file hashes and source image hash match.
- An isolated replay regenerated all 16 traces exactly. The fixtures cover states 2 and 3, predicate/counter values 0 and 1, and both initial PRIMASK values.
- The recorded state/counter transitions and ordered calls match the bounded code path: state 2 with predicate zero changes state only when counter is zero; state 3 selects state 1/counter 640 on readiness, otherwise state 2/counter 160. Mask-save/restore helpers preserve the initial mask and SP.

**Limits:** Predicate, sensor/state, readiness and timing boundaries are controlled; readiness is only sampled as specified, and state 1, invalid states, mutable events and physical behavior are outside these traces. This is bounded loop evidence, not complete loop or canonical coverage. No canonical admission is made.
