# Independent review 2789

**Result: PASS_SCOPED.** The isolated replay passed all 16 original-chain fixtures without function interception. Source, ITCM, body, and candidate artifact hashes match. The asserted six profile publications, temporary high-seven-bit write/restore, ordered control and gate writes, low-seven-bit restoration, original 50/5 delays (1730 ITCM iterations), secondary-last call, packed R0, incoming R3 in R1, preserved registers, PRIMASK, and frame matched.

- Wait/service and other indices are outside this fixture set.
- Emulated delays and RAM-backed writes do not establish physical timing or hardware behavior; concurrency is untested.
- Private evidence only; no canonical admission.
