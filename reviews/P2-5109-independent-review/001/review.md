# Independent review P2-5109

**Status:** PASS_SCOPED  
**Accepted:** false

Receipt pins the original registration/allocation maps and their dependencies. Isolated replay passes all 96 cases with no controlled callees. The full 8,704-byte oracle checks allocation entry paths for zero, success and exhaustion, split/no-split and reinsertion, plus terminal flags and R0/R1/SP/PC.

## Limits

Only the enumerated valid modeled-RAM inputs are covered. Assertions, faults, volatile/hardware behavior and broader allocation completeness are excluded. Private scoped evidence; accepted:false.
