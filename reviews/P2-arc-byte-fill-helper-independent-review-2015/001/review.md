# Independent review 2015

**Result:** PASS_STATIC_SCOPED.

- The frozen verifier passes, validating the exact 36-byte body, 15 decoded ARC instructions, mappings, source/caller pins and installed decoder replay.
- Manual-backed LP semantics and the byte-loop arithmetic support 16 ascending stores at base+0..15; subsequent masked writes produce 0x47 at +7 and 0x88 at +8. The caller BL.D delay slot supplies the pointer, and caller control flow does not consume the helper return.
- The candidate’s synthetic-memory fixtures and explicit no-concurrent-writer assumption are retained; they do not establish physical memory effects.

**Limits:** The input pointer’s meaning, caller’s enclosing function boundary, hardware execution and whole-image closure remain unproven; neighboring callee targets remain unresolved. No canonical admission is made.
