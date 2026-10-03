# Independent review P2-5147

**Status:** PASS_SCOPED  
**Accepted:** false

The two bounded compare/length bodies pass source-pinned isolated replay and exact instruction/reference checks. Compare performs second-string then first-string loads; equality triggers a fresh first-byte reload before NUL handling. Length scans bytes to alignment, then uses word marker/REV/CLZ logic and returns the terminator-relative length.

## Limits

Aligned word reads can include bytes after a terminator, as explicitly noted; no null/bounds/volatile or memory-safety guarantee is established. Private partial map; accepted:false.
