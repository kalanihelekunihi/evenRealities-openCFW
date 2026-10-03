# Independent review P2-csky-recovery-5073

**Status:** PASS_SCOPED  
**Accepted:** false

Independent scoped verifier passes: contract pins, live explicit owner extents, exact 120-byte body and 39-instruction tiling, decoder replay, one direct caller, helper bytes, and caller setup.

The conditional XIP body at 0x10205768..0x102057E0 has the stated seven branch/call pairs with helper selector values 0,4,8,12,13,14,16, then restores R4/R5/LR. Caller evidence at 0x1020597A uses selector 0x6F; the subsequent call reloads R0, so the return is not consumed in that observed sequence. Shift counts here are all below 32.

## Limits

The XIP mapping is conditional. Physical memory/bit meaning, volatility/MMIO, faults, runtime effects and indirect callers remain unresolved. Inherited dynamic-owner failures for dependencies 4382 and 4536 remain failures; dependency status is scoped static only, not full PASS. Private partial evidence; accepted:false.
