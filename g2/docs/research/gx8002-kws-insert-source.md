# Keyword activation insertion candidate

The source adaptation uses NationalChip/lvp_kws commit
`8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5` and the exact activation-entry type
extracted from its authenticated `kws_strategy.h`. The list has eight 20-byte
entries after its four-byte count. The recovered C implements matching by
keyword value and index, updating only a larger score, otherwise appending
all five fields and incrementing the count. A full list logs overflow.

The first native macOS compilation emitted 148 bytes, exceeding the original
144-byte interval. Disabling shrink wrapping and using GCC's priority register
allocator fits 144 bytes with the original four-byte saved-link frame. The
append pointer and count store are volatile to preserve the observed store
order: index, value, score, score index, private pointer, total. This candidate
has not been admitted into the firmware image.

Stock and candidate use `fcmplts fr1,fr0` for the score comparison and store the
original score register bits on update. The available C-SKY instruction manual
(printed pages 451–453) specifies setting C for less-than and clearing C
otherwise, with no listed exception. Continuous decoded comparison still needs
to cover finite scores, signed zeros, infinities/NaNs and ABI preservation;
matching the opcode alone is not sufficient qualification of the function.

The stock code scans entries using a signed loop bound before checking the
count with an unsigned capacity comparison. Negative counts therefore skip
the scan and reach overflow logging, while a corrupted positive count above
eight can access beyond the defined list. The candidate preserves that order.
Do not quietly clamp the count or present the positive out-of-bounds domain
as safe. Qualification should cover the valid 0..8 list invariant and explicitly
separate corrupted-count behavior from valid storage guarantees.

Next: decode all memory accesses, arithmetic, branch and FP instructions in
both functions, compare ordered traces and resulting list contents, exercise
duplicate entries/first-match behavior and overflow, check caller/callee ABI,
and add regression mutations before source admission and package rebuilding.
The last integrated firmware remains the 129-function /305-test candidate.

Continuous stock/source comparisons now pass 26,048 cases, including partial
matches and negative-count logging. Another 578 cases force both floating
condition outcomes with identical raw operands, covering first-match behavior
without claiming particular hardware NaN/denormal control settings. Nine
regression checks exercise incorrect FP operands/store source, private pointer,
frame and invalid positive-count accesses. The integrated verifier records the
manual hash and keeps hardware qualification false.

Integration completed with 314 passing tests and a rebuilt, verified macOS
package. Codec ownership is now 8,874 C bytes, 120 assembly, 2,280 source data,
80 metadata, 336 fill and 314,402 retained bytes. The source-only goal remains
active; this function's admission does not qualify the entire decoder.
