# Independent review P2-csky-recovery-5141

**Status:** PASS_SCOPED  
**Accepted:** false

Independent scoped verifier passes current contract extents, exact 40-byte body tiling, decoder replay, caller and helper checks.

The routine tests only selector bits 0x10 and 0x20, issuing helper calls at base+8 with indexes 13 and 14. Caller at 0x10205CCA sets R0/R1 from the stated sources and separately loads R3, which the callee does not use; return consumption is not inferred.

## Limits

Conditional XIP mapping and physical/device meaning, volatility/order/fault behavior, indirect callers and runtime effects remain unresolved. Inherited dynamic ownership failures for 4382/4536 and partial helper 4606 remain as-is; no full dependency PASS. accepted:false.
