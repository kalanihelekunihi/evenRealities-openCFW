# Independent review 2287

**Result:** PASS_SCOPED.

Isolated replay regenerated all 324 fixtures. Source, body [0x7288,0x72F8), and candidate file hashes match. Decode confirms 144-byte row selection and parameter/config pointers; the mode-2 branch uses halfwords 62+66, others 64+68. It adds the shifted-count product and count-times-(byte77+parameter halfword44) product with 32-bit wrap, doubles mode2, multiplies by row byte132, calls original A6C0 with divisor46, and multiplies quotient by five. Exact division inputs/result and R3-R7/SP preservation assertions pass; R1 is not used.

**Limits:** Fixtures cover row indices 0/2, mode bytes 0/2/255, selected counts, multipliers and data patterns; mode byte1 and other high-bit patterns are not directly exercised. Division is original but limited inputs; physical units, aliasing and pointer faults remain unresolved. No canonical admission.
