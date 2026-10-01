# Independent review 2009

**Result:** PASS_SCOPED.

- The immutable source pin and all receipt file hashes match.
- Isolated replay reproduced all 384 fixture rows exactly across both indices, six wide aliases, all skip masks and four callback-return placements.
- Results show the low-byte validation accepts these aliases, while later full-word mode comparisons send them to reverse traversal. Callback R1 and skip matching use the full 32-bit alias; sentinel returns do not trigger exact-mode-1 stopping. Last-invoked and per-index failure globals remain unchanged, and argument-copy/stack assertions pass.

**Limits:** The result applies to the six fixture aliases and supplied acyclic lists only. Null heads, assertion continuation, cycles and arbitrary callback effects remain unresolved. No canonical admission is made.
