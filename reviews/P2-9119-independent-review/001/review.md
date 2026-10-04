# P2-9119 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 100 instructions in 0x52B5A2..0x52B606 match the locked image.
- The 0x2019 builder requests 28 payload bytes, stores the first low16 field at +3/+4, copies eight source bytes to +5, stores the second low16 field at +13/+14, then copies 16 bytes to +15 before dispatch.
- Null allocation skips source reads and writes; success returns saved entry R3 (source16 pointer) in R0, not child status. Sequential calls preserve aliasing effects.

Limitations:

- Source pointers and allocation/dispatch contracts are unchecked or unresolved. No independent snapshot, concurrency, physical, or full-firmware claim.
