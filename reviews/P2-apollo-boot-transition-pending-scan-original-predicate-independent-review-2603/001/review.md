# Independent review 2603: pending scan with original state predicate

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate artifact and source hashes match, as does the scan-body digest. An isolated replay copy redirected to a fresh output directory passes all 1,536 fixtures. Crucially, the helper's register pointer aliases the scan's mode word; the fixtures and oracle preserve that shared-address relationship and keep its low nibble within 0–3.

The integrated path runs original code without function interception. The observed scan body checks the gate and index shortcuts, invokes original `0x41F3F0` when required, and then checks the single configured table entry against valid-bit, mask-bit and 9-bit field ranges. Output values and helper-call decisions match; R7 return and SP are checked.

Only one table entry is active per fixture, so multiple-match precedence is not covered. Stable memory, limited mode nibble values, and the separately bounded state-predicate scope remain explicit. Physical meaning and callback ownership are unresolved; no canonical admission is claimed.
