# Independent review P2-5143

**Status:** PASS_SCOPED  
**Accepted:** false

Receipt pins the locked source and service-record map 5136; isolated replay passes all three original executions without child redirection. The full 256-byte state oracle verifies writes to bytes 49 through 213 and untouched neighbors, along with R0=5, saved registers, SP and PC.

## Limits

The 41560C helper executes as original code, but its separate semantic map is not pinned here; no helper semantic closure or hardware claim is made. Private scoped evidence; accepted:false.
