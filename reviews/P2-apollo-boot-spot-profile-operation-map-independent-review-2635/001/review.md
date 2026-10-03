# Independent review 2635: spot-profile operation map

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate receipt and artifact pins match the authenticated image. The body `[0x42A878, 0x42AB6E)` contains 309 contiguous instructions; all recorded instruction bytes and 27 PC-relative literal values match the source. The isolated static verifier passes. Independent objdump decoding agrees with the mode and dispatch guards, critical-section flow, operation routing, classifier branch and bounds writes, recomputation path, and final status/epilogue.

The class flag comparison is correctly described: `LDRB` zero-extends its byte result, so the signed `BGE` after `CMP r0,#3` treats all values 3 through 255 as at least 3. The global flag is set only below 3.

This is static mapping evidence only. The five child routines and dynamic operation behavior remain unresolved. The packet does not establish caller ownership or physical register meaning, and it remains private and unaccepted.
