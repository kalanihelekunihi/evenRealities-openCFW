# Independent review 2311

**Result:** PASS_SCOPED.

Isolated replay regenerated all 2,916 fixtures. Source, body [0x6294,0x632A), literal 65535 [0x632C,0x6330), and candidate artifact hashes match. Decode confirms saturated sum, raw parameter byte 56 masked by 0x7F, configuration shift byte 78, mode row byte 136, percentage row byte 135, and validity-dependent deduction 8 or 4. Child order is 6220→6262→6270→61F0, with the saturated sum supplied as the fifth stack argument; result is ORed with 4. All tested calls/results and R4-R11/SP checks pass.

**Limits:** Fixtures exercise modes 0,1,2 (not mode3) and selected field combinations. Child arguments are decoded but not individually captured/asserted in this candidate; broad component evidence is separate. Aliasing, faults and physical field meaning remain unresolved. No canonical admission.
