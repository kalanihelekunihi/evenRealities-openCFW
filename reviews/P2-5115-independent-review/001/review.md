# Independent review P2-5115

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay passes. The mapped routine saves LR and allocates 12 bytes, stores R1/R2/R0 to SP+0/+4/+8, then executes BKPT 171 with the expected call arguments. The separate 0x7C28 tail branch loads R0=1 and branches to 0x41B298. Conditional post-BKPT flow is described only under the explicit resume assumption.

## Limits

Whether the breakpoint/fault handler returns, resumes, or transfers elsewhere is unresolved. No handler semantics, trap liveness, hardware behavior, or admission claim is made; accepted:false.
