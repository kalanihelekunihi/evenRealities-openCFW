# Independent review 2299

**Result:** PASS_SCOPED.

Isolated replay regenerated all 512 fixtures. Source, body [0x71C8,0x7284), literal 0x6781 at [0x7284,0x7288), and candidate file pins match. Decode and replay agree on cached root versus reloaded configuration pointers, root-byte copies to config offsets 116/117/76, parameter-byte clear, ignored 5378/56A4/callback returns, stored 5D70 result, and conditional callback. Status from 6384/5378 is ORed; mode 1 and mode 2 short-circuit in order; 7064 replaces status only when prior status is zero. Rows 0–2 are always tested and predicate/cap results are ORed. Ordered writes, call args/order, final status and R4-R6/SP assertions pass.

**Limits:** All children and callback are controlled in these fixtures; their original effects and the cumulative original composition remain separate. Only selected statuses/predicates/pointer values are covered; aliasing, pointer changes and hardware behavior remain open. No canonical admission.
