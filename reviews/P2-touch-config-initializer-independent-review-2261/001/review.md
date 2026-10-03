# Independent review 2261

**Result:** PASS_SCOPED.

The source, body `[0x5378,0x5518)`, literal pool `[0x5518,0x5528)`, and candidate artifact hashes match the receipt. The 416-byte Thumb/M-class decode agrees with the described default initialization and ordered repeated writes. The special word 8 fallbacks (halfword 68 zero gives `0x100`; halfword 66 zero gives `1`), root-byte masks, packed words 12/24/32/44, and word-68 decrement/mask are consistent with the instructions and literal masks.

An isolated replay regenerated all 27 fixtures. Original initializer and `A9D4` execute; only `52BC` and `50E4` are controlled zero-return boundaries. The full ordered destination ledger and 256-byte output, child order/arguments, and R4–R11/SP are asserted.

**Limits:** Configuration and root bytes use uniform patterns 0, 1, or 255, so many source fields are correlated; the halfword 66/68 fallback values are varied independently, but other field interactions are not. Child effects are no-op modeled returns; stack scratch postconditions, aliasing, pointer mutation, and physical field meaning remain unresolved. No canonical admission is made.
