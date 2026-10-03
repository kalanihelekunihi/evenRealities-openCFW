# Independent review 2283

**Result:** PASS_SCOPED.

Isolated replay regenerated all 196 fixtures. Source, body [0x5D70,0x5D8A), literal [0x5D8C,0x5D90), and listed files match their pins. Decode confirms the product wraps to 32 bits before logical shift by 14; a zero shifted result returns zero, otherwise the helper subtracts one and saturates at 65535. R1, R2 and SP preservation assertions pass.

**Limits:** The grid contains fourteen selected values per factor, not every 32-bit pair. No child calls occur. Pointer faults/aliasing and physical meaning of the scale remain unresolved; no canonical admission.
