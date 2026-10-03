# Independent review 2761

**Result: PASS_SCOPED.** Isolated replay passed all 64 original-handler fixtures with no function interception. Source, ITCM, body, and candidate artifacts match. The six profile publication writes, selected packed-byte write to the low-seven-bit field, control/high restore writes, packed R0, incoming R3 in R1, mask, and frame match for newfirst 0–3 and oldfirst 4; no delay or secondary call occurs.

- Wait/service and other indices are outside this fixture set.
- Physical hardware effects, concurrency, and caller ownership are not established.
- Private evidence only; no canonical admission.
