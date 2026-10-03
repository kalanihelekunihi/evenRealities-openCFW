# Independent review 2835 — corrected current-restore contract metadata

**Result: PASS_SCOPED.** This append-only review binds to candidate 2834/002. Its repository-relative source path resolves; source/body and pseudocode hashes match; every input pin resolves; candidate artifact hashes match; and the stated image-load mapping is arithmetically consistent (`0x429DA4 − 0x410000 = 0x19DA4`, 105,892). The campaign target hash matches identity. The stable component/image/address-space/entry/ISA tuple is explicit, and the correction adds a prototype, calling convention, and structured RAM/MMIO references.

The isolated record verifier passes. Separately, I executed the original 31 instructions for three profile-word patterns and confirmed the register, stack, PRIMASK, ordered effect, and NZCV claims; the final C bit comes from original profile bit 20 and final MOVS sets N/Z while preserving C/V.

This remains a private scoped contract candidate. Whole-image denominator, physical peripheral semantics, exhaustive alias/fault behavior, and canonical admission are not established. `accepted` remains false.
