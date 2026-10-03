# Independent review 2369

**Result:** PASS_SCOPED.

Receipt d3ef301e2d2496b622829a78c82581026ddf6df115f7c6c4b72c00fff2606351 pins the source, dispatcher body [0x4F54,0x4F6E), and separate child body [0x4E6C,0x4F54); both hashes and evidence-file pins match. Isolated replay passes all 576 fixtures.

The now-pinned root disassembly decodes 4F54 as a descending dispatcher that invokes child 4E6C with 2,1,0 and ctx. The root body hash matches source bytes; replay executes from this root entry. The child body is separately identified/hash-pinned, and original 4E6C plus 4E36/4E58/4E60 execute without interception.

All 576 fixture cases match the independent ordered byte oracle: three distinct rotated rows, combined child call order, writes, full supplied memory and R4-R11/SP. Within-row overlap behavior is exercised by strides; no cross-row alias is introduced.

The prior 001 receipt pinned only the child span despite replay entering 4F54. This 002 explicitly repairs that metadata gap with the dispatcher body and separate child hash.

**Limits:** Cross-row aliasing, mutable counts/flags, physical effects and incidental R0 semantics remain unresolved. Fixture pointers are distinct and bounded; this does not establish arbitrary alias or concurrency behavior. Private evidence only; accepted:false, no canonical admission.
