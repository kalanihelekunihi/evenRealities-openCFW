# Independent review 29989

**Result:** PASS_SCOPED; `accepted: false`.

Candidate: `/Users/kalani/Repo/evenRealities-openCFW/g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-main-diagnostic-fixed-library-signed-decrement-loop-fresh-resource-index-frame48-middle-30388-map/001`. All candidate-file hashes and the locked image hash match the receipt. Independent reassembly confirms 100 contiguous bytes and 37 Thumb instructions over `[0x4EB11C,0x4EB180)`.

The first fresh word through the `4EBDD4` literal is passed to `44DDEA`; its actual R0 result becomes R5 and is decremented with SUBS flags before the signed loop test. The loop uses fresh current-R4 words for `44DCE2`, tests its actual return, conditionally calls `44D7B8`, then decrements R5 and repeats while nonnegative. No termination or helper-preservation claim is made. Following calls preserve their actual postcall state. The later index path calls `5000CC`, freshly reads the current R4 word, and uses unsigned `>=6` (B.CS) to exit. For an index below six, the code independently reloads the current index, computes `literal + index*8` with nonflag-setting ADD.W, and reads the word at offset four. If nonzero, it repeats those reads before calling `44D878`; it then freshly loads current R4 for `4EC2DC`. Thus the earlier unsigned bound is not projected onto the later independent reads. All three literal references match the locked image.

This remains bounded partial evidence. The branch to `0x4EB1AE` is excluded; no array bounds, pointer stability, helper behavior, global coverage, source completeness, freeze, or byte equality is established.
