# Independent review 2835 — current-restore typed contract candidate

**Result: REVISE_METADATA.** The candidate and receipt hashes verify; its target hash matches campaign identity, the 82-byte body range and 31 instructions are correct, and all four input/review pins resolve and match. The isolated candidate replay passes. I also independently executed the original body with three target-word patterns and verified R0–R12, LR, SP, PRIMASK, and NZCV. The pseudocode’s final flag account is accurate: LSRS #21 supplies C from original bit 20; final MOVS zero sets N=0 and Z=1 while C and V remain unchanged.

The register-level sequence matches the original instruction ordering and preserves the repeated fresh reads. The proposed record still needs fields before it can serve as the G2 function record described by `g2/workflow/CONTRACTS.md`: explicit file-offset-to-loaded mapping, prototype/calling convention, structured data/reference contracts, and a repository-relative source path. Evidence is transitively pinned through receipts, but direct evidence-file references would make this record self-contained.

This review does not establish every alias/fault case, physical peripheral meaning, or whole-image ownership/denominator. `accepted` remains false.
