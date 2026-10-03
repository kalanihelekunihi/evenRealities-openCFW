# Independent review 2829 — all-handler wait/service prefix

**Result: PASS_SCOPED.** The source image pins and candidate artifacts match. The isolated 192-fixture replay passes. For each of the 24 mapped nontrivial handlers, the replay independently compares the candidate's decoded body bytes with the locked image, then runs the prefix through the service/runtime/inactive-op4 chain and stops before the first publish literal.

The assertions cover exact prefix writes and call order, PRIMASK behavior, ready versus timeout delay counts, ITCM iterations, and stop PC. This is not a full-handler return or frame test. Inputs are constrained to the shared documented prefix state; alternate flags, active op4, other paths, dynamic hardware, physical effects, and caller ownership remain unresolved. `accepted` remains false.
