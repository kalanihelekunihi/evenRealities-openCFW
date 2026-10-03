# Independent review P2-5111

**Status:** PASS_SCOPED  
**Accepted:** false

Receipt pins the allocation/release chain dependencies. Isolated replay passes all 96 cases with no controlled callees. The 8,704-byte oracle covers null release, split/no-split, next-block coalescing, metadata reinsertion and residual internal node bytes, along with R0 saved-R3 alias and SP/PC.

## Limits

Previous-block coalescing, assertions/faults, volatile/hardware behavior and unlisted paths are excluded. Private scoped evidence; accepted:false.
