# Independent review 2949/001

**PASS_SCOPED**; `accepted` remains false.

The source and body hashes match the locked flash image. All 368 decoded instructions tile `[0x42BA00, 0x42BD8C)` exactly (908 bytes), each recorded instruction encoding agrees with its original source bytes, and every extracted PC-relative literal value matches the image. Isolated static replay regenerated the listing. I checked the prose control-flow summary against the instructions for early gate/magic returns, operation/option dispatch, current-state shortcut/deferred transition, decoder publication gate, and the final PRIMASK/frame restoration.

This is a static map, not dynamic validation of the complete caller. Changing or aliased inputs, external helper semantics, physical hardware behavior, and global ownership remain unresolved.

Candidate receipt SHA-256: `ce0a259d164e9e8e4ec38dd42c2ef185c93343527a6268571b7de4404f55cf81`.
