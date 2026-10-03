# Independent review P2-5075

**Status:** PASS_SCOPED  
**Accepted:** false

Receipt pins the locked image and alignment-map 5068 inputs; local artifact hashes match. Independent isolated replay passes all 270 cases.

Three original alignment entries were exercised across the stated boundary values and masks, with only the assertion target controlled. Arguments, return/frame checks, and preserved registers match the packet scope.

## Limits

Only the enumerated mapped entries and modeled assertions are covered; this is private scoped evidence, not hardware behavior or global completeness. accepted:false.
