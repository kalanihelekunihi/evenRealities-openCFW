# Independent review 2307

**Result:** PASS_SCOPED.

Isolated replay regenerated all 576 fixtures. Source, body [0x6384,0x6462), and candidate file hashes match. The original checker runs 623C/6220 and 6262 with no interception; zero config/parameter threshold inputs make 6220(0)=1 and the caller’s threshold zero, so 623C returns 10. The checker’s cached original flags still govern the controlled 6352/6294 branches. Exact calls, parameter writes, immediate 2048 failures and R4-R11/SP assertions pass.

**Limits:** Only 6352 and 6294 are controlled children, and the original 623C input is the zero-field fixture; broader leaf inputs are separate evidence. Aliasing, helper mutation and physical field meaning remain unresolved. No canonical admission.
