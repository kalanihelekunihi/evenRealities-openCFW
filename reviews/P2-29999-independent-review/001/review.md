# Independent review 29999

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-nonnull-input-actual-value-equality-event839-frame120-middle-30398-map/001`. Candidate hashes and locked image hash match the receipt. Independent reassembly verifies the exact 92-byte span `[0x4EB212,0x4EB26E)` as 33 contiguous Thumb instructions.

The fresh `4EB740` word is used as a pointer for the byte-292 zero store. Incoming R4 is passed to `44E498`; its actual return R0 is copied into R8 with nonflag MOV, then compared with actual R7. Only equality enters the diagnostic path and sets R5=10. The bit1 query gates event839, with current R5 and fresh literal/global loads staged into the indicated SP slots. Separate bit0 and bit2 calls gate `43CE9E`. `MOVS.W R0,#0x10400000` yields N=Z=C=0 and preserves V. These helper calls may mutate R5, so the initial value ten is not claimed to remain in R5 at later uses. The six PC-relative references match the locked image.

This is bounded partial evidence only. The external exits and following code are excluded; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.
