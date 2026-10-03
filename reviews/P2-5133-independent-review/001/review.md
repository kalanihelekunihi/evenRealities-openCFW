# Independent review P2-5133

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay passes. Both 8-byte-frame entries read state byte +242; nonzero paths call their distinct children and ignore returned status, then write byte +244, while zero paths write byte +243. R0 is the constant 1 or 0 respectively; saved R4/frame behavior and literal consumers match.

## Limits

Child effects and hardware/service meaning are not established. Private partial map; accepted:false.
