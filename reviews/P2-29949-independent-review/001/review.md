# Independent review 29949

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-frame3408-return-bound-helper-global-transfer-leaf-30348-map/001`. Its receipt and all five listed file hashes match. Independent reassembly confirms all 40 locked bytes decode contiguously as 13 instructions over `[0x4EAC28,0x4EAC50)`.

The first sequence passes the actual incoming R6/R4 values through MOVS to opaque `4ED058`, then writes byte one using the current post-call R4 base. SP advances by 3328 and then 56 before `LDMIA.W SP!,{R4-R8,PC}` reads six fresh words and advances another 24 bytes. The candidate correctly keeps the restored slots mutable and makes no caller-completeness claim.

At the separate entry, `PUSH {R7,LR}` creates an 8-byte frame; `4E9FD6` returns actual R0, which is stored at the freshly literal-loaded address plus 288. `POP {R0,PC}` loads the saved R7 slot into R0 and the return address into PC, so the helper's R0 is not presumed to be the routine's returned value. The literal word and the data it points to are kept distinct.

The review is limited to these two bounded sequences. The continuation is excluded, and there is no helper/global ownership or firmware-completeness claim.
