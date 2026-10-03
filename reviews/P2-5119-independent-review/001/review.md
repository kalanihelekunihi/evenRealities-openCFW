# Independent review P2-5119

**Status:** PASS_SCOPED  
**Accepted:** false

Source-pinned isolated replay passes. The fallback body saves R7/LR, loads the literal into R2 once, then repeatedly sets R1=R2 and R0=24, executes BKPT 171, and branches back if execution resumes. There is no ordinary software return or stack unwind in the loop. The literal consumer is confirmed.

## Limits

Behavior after BKPT is external and unresolved; no physical trap, return, halt or fault policy is inferred. Literal pool bytes are outside the body. Private scoped evidence; accepted:false.
