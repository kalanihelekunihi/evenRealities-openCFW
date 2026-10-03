# Independent review 2597: floating transition helper

**Result: PASS_SCOPED.** `accepted` remains false.

Receipt artifact hashes, source-image hash, and the original body digest `[0x42CED8, 0x42CFE0)` match. I reran an isolated copy of the replay with only its output path changed; all 152 cases pass.

The input encodings cover all four categories, exact thresholds and adjacent encodings, signed zero, positive and negative infinity, and quiet/signaling NaNs. The observed categories are 0 for `[-273,35)`, 1 for `[35,50)`, 2 for `[50,1000)`, and 3 otherwise; unordered NaN comparisons take the invalid category. The replay independently computes the binary32 output words and checks ordered writes, flags, child calls, memory, result, R4, D8, PRIMASK and SP. In particular, category 1 stores lower bound 33 despite threshold 35, and category 2 stores 48 despite threshold 50. Invalid inputs skip the child, write two zero bounds, and return 1.

The original child path is executed without interception, but its gate/mode/boost state is fixed to enabled/3/15. Stable input memory, physical interpretation, concurrent mutation, other child branches, and callback ownership remain unresolved. No canonical admission is claimed.
