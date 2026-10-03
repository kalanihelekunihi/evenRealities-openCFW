# Independent review 2443

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 5892d673952bf4f2f10828959cb7c8edd57988826a3307a3335d9c2ba773f430; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches. Eleven owned bodies, including A324 and 4480, match their listed hashes; candidate evidence files match receipt hashes.

Independent isolated replay passes all 64 fixtures, with output hash matching pinned replays.json. Original A324 and 4480 execute within the prior dispatcher/measurement/reset/status-wait chain. Only mode setup 6AC0 remains controlled.

A324 reads scale at 0x20000870, scales its input and calls 4480. Original 4480 loop arithmetic yields zero iterations at scale 1 and 64 iterations per A324 call at scale 255; the tested clear-ready cases perform one delay or 315 delays respectively. The status wait continues checking readiness after the delay returns. A324/4480 args, aggregate loops, writes, poll/arithmetic/status and R4-R11/SP pass.

**Limits:** Scales 2 and 0 are seeded but their reset-ready branch skips the delay. Other scale values and physical calibration/time are not established. Readiness/samples are modeled; interrupt effects, hardware timing and controlled mode setup remain unresolved. Wrapper literal ownership/padding limits remain separate. Private bounded evidence only; accepted:false.
