# Touch chunked delay A2F0

Body A2F0..A318 is 40 instruction bytes, excluding three literal words. Retain input in R4. While unsigned remaining exceeds 32768, freshly load chunk-delay word at literal address A318, call original 4480 with that value, and add literal FFFF8000 to remaining (subtract 32768 modulo 2^32). Then freshly load scale word at literal address A320, multiply remaining modulo 2^32, call original 4480 once more, restore frame and return its zero result.

Eighteen original-instruction fixtures observe every delay-call argument without modifying execution. They cover zero, one, exact threshold, one above threshold and the next chunk boundary, with three scale values. RAM-derived delays are explicitly supplied small fixture values. Loop count, arguments, zero result and SP agree with the separate model; physical elapsed time and asynchronous changes remain unresolved. No canonical admission or C implementation.
