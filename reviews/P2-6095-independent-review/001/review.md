# Independent review 6095

**Result:** PASS_SCOPED.

Source/dependency/artifact hashes match; every recorded instruction byte matches the locked image and the body tiles exactly [0x429a30, 0x429aac) (124 bytes, 42 instructions). GNU Thumb decoding independently agrees with the ledger.

The 40-byte frame saves R3-R11/LR. R5 is index, R4 is incoming R2, R6 is row base; first/second row pointers derive from R5/R1 and metadata from base+100. Four fresh masked metadata fields overwrite saved R3 at SP0..SP3. First-row high/low seven-bit values remain R7/R8; second-row high is overwritten by rereading the first row. Metadata selected by second and first index remain separately in R9/R10. A fresh bit-0 test branches clear to 0x429ad0 and set to 0x429aac. No bounds check or return is claimed.

**Limits:** Static review only; no execution rerun. These local register/control-flow observations do not establish channel semantics, child behavior, hardware effects, global completeness, canonical admission, or freeze/C gates. Private evidence remains `accepted:false`.
