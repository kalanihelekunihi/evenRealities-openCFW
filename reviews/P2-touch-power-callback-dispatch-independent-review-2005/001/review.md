# Independent review 2005

**Result:** PASS_SCOPED.

- The immutable source hash and all receipt artifact hashes match. Directly extracted bytes [0xA444,0xA516) are exactly 210 bytes with the recorded SHA; the literal words at 0xA518/0xA51C/0xA520/0xA524 are 0x20000F34/0x004200FF/0x20000F24/0x20000F28, outside body ownership.
- Isolated execution reproduced all 256 fixture rows exactly. The fixtures cover two indices, four valid modes, all three-node skip masks and the sentinel at each node or absent. Callback argument copies, callback order, retained result, last-invoked global and mode-1 failure pointer match the recorded model.
- Fixture outcomes support forward traversal for modes 1/4, reverse predecessor traversal for mode 2, and tail-then-predecessor traversal for mode 8; mode 1 stops when a callback yields the sentinel.

**Limits:** Callbacks are controlled, so callback semantics and arbitrary topology mutation are not established. Null head in mode 8, cycles, invalid indices/modes, and wide mode aliases remain unresolved. No canonical admission is made.
