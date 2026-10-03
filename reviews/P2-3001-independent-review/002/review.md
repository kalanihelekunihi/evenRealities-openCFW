# Independent review 3001 — correction

**Result:** PASS_SCOPED_WITH_CORRECTION; `accepted: false`.

Candidate `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-clock-encode-map-3000/002` retains the same pinned original image and exact 148-instruction spans. Receipt-listed files match and the isolated static replay passes all 148 decoded instructions.

The earlier review 001 misstated the R2 preservation contract. The fifth stack argument aliases the frame's saved-R2 slot, so normal return pops `R12-1` into R2; early exits before that write return incoming R2, and the special second-call path returns zero. R3 remains restored. Candidate 002 corrects the prose and preserves the static-only and unresolved hardware/dynamic limits.
