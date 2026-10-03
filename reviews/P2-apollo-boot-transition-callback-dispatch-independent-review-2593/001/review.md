# Independent review 2593: transition callback operation dispatch

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate artifact hashes and source image pin match. The body digest for `[0x42D562, 0x42D5C2)` matches the mapped flash bytes. An isolated copy of the replay, redirected to a fresh output directory, passes all 126 cases.

The cases cross operation values 0–7 and 256–259, pointed-byte values 0/2/255, three controlled child returns, and null pointers only for operation 0. The branch model and captured call arguments agree: operation 0 conditionally calls `0x42CFE0` with R0=2 and discards its result; operation 1 selects `0x42D3BC` for byte 0 or `0x42D104` otherwise and returns that child's R0; operation 2 passes the raw pointer to `0x42CED8` and returns its R0. Other covered operations return zero. High-register and stack preservation checks pass.

All four child implementations are controlled, so their effects are outside this result. Null operation-1/2 pointers are not exercised, and operation 1's unconditional dereference is not a null-safety guarantee. Enclosing ownership, physical behavior, and arbitrary aliasing remain unresolved. No canonical admission is claimed.
