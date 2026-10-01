# Independent review 1871: flash row command prose revision

Status: **REVISE_PROSE**. Accepted: **no**.

Candidate source and file pins match. The isolated replay passed all 60 cases and its output JSON is byte-identical to the candidate. The five fallible invocations are exercised, including failure of the second 8BF4 command followed by an unconditional 8D20 cleanup; command failure takes precedence over cleanup failure.

One instruction-order correction is needed: the body calls 8CA8 to derive the row index at 8D58, then calls 8C74 to validate at 8D60. The opening pseudocode currently states these in reverse order. Rest of the frame, MMIO, branch, status, interrupt-restore, and stack behavior matches the bounded fixture evidence.

All six external helper entries are controlled. Their physical or resident-ROM behavior remains unresolved; the run is synthetic boundary evidence, not physical flash verification. No canonical admission is made.
