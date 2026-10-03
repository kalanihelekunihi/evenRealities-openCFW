# Independent review 2649: apply routing with original index selector

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate, source, body, fixture, and lookup-data pins match. The lookup data is at `0x433498`. I reran a replay copy into a fresh isolated directory; all 1,600 fixtures pass. Original `0x42A2B4` and `0x4156AC` execute, while `0x42A1BC`, `0x42A43A`, and synthetic indirect handlers are controlled.

The composed call order, branch-specific arguments, mixed-low-bit adjustment, route result/index behavior, indirect dispatch, returned R0/R1 words, R4-R8, SP, and sentinel return match the assertions. A selected table byte of 26 produces status 7 and skips indirect dispatch; other tested bytes dispatch through synthetic targets.

This does not establish real table contents or handler semantics. The two comparison children remain controlled, and out-of-range indices, ownership, concurrency, aliasing, and physical effects remain unresolved. Private scoped evidence only; no canonical admission.
