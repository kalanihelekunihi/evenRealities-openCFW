# Independent review 1995

**Result:** PASS_STATIC_SCOPED.

- The candidate verifier passes, independently checking the authenticated stage2 source image, body extent, split code slices, literal pools, unowned BKPT gaps, both dispatch tables, incoming callers, target boundaries, and installed-tool disassembly pins.
- The pseudocode matches its checked 24 static fixtures, including unsigned table bounds, the two computed dispatches, helper call argument setup, and the locally observable return/output paths.
- The conditional child-to-runtime coordinate is consistently recorded as 0x10023400 + child offset; the evidence does not authenticate a physical load at that address.

**Limits:** The runtime mapping is conditional, helper callees remain unresolved, caller ownership/semantics are bounded, and full-image closure and physical behavior are not established. No canonical admission is made.
