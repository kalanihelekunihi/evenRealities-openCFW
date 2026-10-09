# Independent review 29939

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-signed-second-index-stack1192-resource-selection-frame3408-middle-30338-map/001`. The candidate receipt and all five receipt-listed file hashes match. Independent reassembly from the pinned image covers `[0x4EAA0A,0x4EAA92)` exactly: 136 locked bytes, 47 contiguous decoded instructions, no gaps or mismatches.

The signed `CMP R7,R0` followed by `BGE` is correctly modeled as an exit when signed R7 is greater than or equal to the actual helper-returned R0. On the continuing path, both `MOVS` operations set N/Z as described, then `UXTH` retains the low 16 bits for the opaque helper call. Its actual R0 zero result branches to the external exit. The selector path independently reloads `[SP+1500]` for each comparison and selects literal-backed calls for values 1 and 2, with the third call for all remaining values. The three literal references at `0x4EB494`, `0x4EB498`, and `0x4EB49C` match the locked words. The subsequent calls receive the fresh current `[R4+28]`, `[R4+32]`, and `[R4+36]` words and the stated constants or current-SP-derived pointers. No helper result or register preservation is inferred.

This is bounded partial evidence only. The continuation and external/helper behavior remain unresolved; there is no whole-firmware completeness or byte-equality claim.
