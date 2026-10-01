# Independent review 2023

**Result:** PASS_SCOPED.

- Source and receipt artifact hashes match; isolated replay reproduced all 16 fixtures exactly.
- Each success case invokes mode 1 with the entry mask, optional mode 4 under mask 1, observes the original WFI leaf under mask 1, then invokes mode 8 after mask restoration. The mode-4 skip bit suppresses only that pass.
- In failure cases the sentinel probe is retained, no WFI occurs, and one-node mode-2 rollback has a null predecessor and therefore no callback. Stack and incoming PRIMASK are restored.

**Limits:** The synthetic callback and WFI continuation are controlled. These one-node cases do not exercise nonempty rollback predecessors, callback effects, physical wake, or hardware side effects. No canonical admission is made.
