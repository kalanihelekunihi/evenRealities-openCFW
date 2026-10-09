# Independent review 29979

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-global-byte-reset-three-helper-gates-frame48-prefix-30378-map/001`. Its listed file hashes and input image hash match the receipt. Independent reassembly confirms the exact interval `[0x4EAF76,0x4EAFD8)` contains 98 contiguous bytes and 35 Thumb instructions.

The code saves six registers and reserves another 24 bytes, then loads the fresh literal pointer and clears its byte at offset 292. The three calls preserve actual postcall state; the `ADDS R0,#1` between the second and third call updates NZCV from the actual second-call R0. Subsequent gates independently reload the literal pointers and pointee words at R5 and R6; none are treated as stable across calls. Both `43C0E4` calls set R1=10 and R2=0 and pass the current `SP+12` address through R0. The final `509E14` call uses R2=5, current `SP+12` as R1, and a freshly loaded word through current R5 as R0. The three literal references match the locked image.

This is bounded partial evidence. The external exit `0x4EB1AE` and continuation at `0x4EAFD8` are excluded; no helper behavior, global coverage, source completeness, freeze, or byte equality is established.
