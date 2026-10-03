# Independent review 6069

**Result:** PASS_SCOPED.

The source range [0x429624, 0x42962c) contains the two reported words, and the locked-image hash plus all referenced-ledger hashes match. Each of the 16 consumer observations is present in its cited latest map ledger; independent GNU Thumb disassembly confirms each PC-relative effective address reaches the corresponding word. Both words have consumer evidence.

The 16 entries are observations, including repeated sites across overlapping maps, not 16 unique consumers.

**Limits:** Local consumer-backed data classification only. No pointer-purpose, broader code/data-boundary, reachability, canonical admission, or freeze/C claim is made. Private evidence remains `accepted:false`.
