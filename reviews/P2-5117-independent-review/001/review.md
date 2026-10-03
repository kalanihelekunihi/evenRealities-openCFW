# Independent review P2-5117

**Status:** PASS_SCOPED  
**Accepted:** false

Corrected 002 pins the assertion map and locked image; isolated replay passes all 12 cases. Original code reaches a hook immediately before BKPT, then the harness explicitly resumes at 0x5746; the controlled 0x41B298 child returns as modeled. Stack arguments, conditional call, tail LR, R0, SP and PC checks match.

## Limits

The BKPT itself is not executed; this does not establish any real debug/fault/monitor behavior or trap resume policy. Child behavior is controlled. Failed 001 is preserved. Private scoped evidence; accepted:false.
