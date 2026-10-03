# Independent review P2-5087

**Status:** PASS_SCOPED  
**Accepted:** false

Corrected map 002 independently decodes and replays. It preserves independent next/previous reads and ordered link stores, bitmap removal/publication order, and the corrected D5C return: metadata + (class << 2), not the final STR address. Literal consumers and source pins match.

## Limits

Assertions and child helper effects remain modeled/possibly returning; no allocator/hardware/C or admission claim. The superseded 001 remains preserved; review is of 002 only.
