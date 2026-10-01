# Independent review 2177: weighted sample filter

**Result: PASS_SCOPED.** Candidate `analysis/touch-weighted-sample-filter-5054-2174/001` remains unaccepted.

The 76-byte body gates fractional handling on `(flags & 0x300) == 0x200`. That path passes scaled sample, scaled group plus auxiliary fraction, and the full word weight to original 4FDE, then writes the returned high halfword to group, low byte to auxiliary, and the same result halfword to sample. The other paths pass unscaled halfwords and do not access auxiliary. The original leaf wraps its multiply/add arithmetic before shifting.

All 768 isolated fixtures passed and matched frozen JSON; source/body/artifact pins and independent decode passed. Coverage is finite, buffers are separate, and physical meaning, aliasing, and concurrency remain open. No canonical records changed.
