# Independent review 6509

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and 43014E..4301D6 body span match the locked image. GNU decoding confirms the two initial `[SP+8]` child calls, then a fresh sample load from SP+36. The code multiplies by 1190 modulo 2^32, shifts right 12, converts the resulting unsigned integer to S0 as float, and compares against two PC-relative float literals. `BLT` after the first compare and `BPL` after the second each branch to 43011A; their exact APSR behavior, including unordered flags, is preserved by the listed flag-transfer instructions.

If both tests pass, it writes byte 1 and halfword 1 to the literal-backed record at offsets 0 and 2, converts S0 to signed integer and stores its low halfword at offset 4, widens S0 to double in R2/R3, and calls 415FAE with the fresh SP+36 sample in R1. The code increments R4, truncates it to u8, and loops while that value is signed-less-than 3. After the loop it calls 42F020 with (fresh `[SP+8]`, 2, 0), then 42EA32 with fresh `[SP+8]`; both results are ignored. Finally it loads a word through the literal at 430238 and calls 41D92C with (16, loaded word), then discards 72 bytes and restores R4/PC.

No successful-read assumption, diagnostic-format claim, or purpose inference is made. Child and VFP edge behavior outside the decoded operations remain unverified.

No canonical files or gates changed.
