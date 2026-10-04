# P2-9027 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The disjoint dispatcher and codec instruction ranges match the pinned image byte-for-byte; the dispatcher literal reference resolves to the recorded global.
- Dispatch index zero calls the external zero-index route; nonzero reads callback global+84, tests it, then reloads the slot for BLX. It returns saved entry R3 regardless of child status.
- The pair encoder computes low16(3*low8(a)+low8(b)); decoder uses signed division by 3 on low16 input, writes remainder byte before quotient byte, and returns the full quotient. Aliased outputs therefore retain the quotient byte.

Limitations:

- External zero-index route and callback contracts are unresolved. The byte codec is not shown to be a universal inverse for unrestricted inputs; output pointers are unchecked.
