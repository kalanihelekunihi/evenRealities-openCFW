# Independent review 2653: secondary field apply

**Result: PASS_SCOPED.** `accepted` remains false.

The candidate and source pins match. I reran the replay into a fresh isolated directory; all 90 original-instruction fixtures pass without interception. The literal-derived profile, runtime, and target pointers match the source.

The `R1 == 8` override selects category 7; otherwise full R0 selects the category, with other values following the default branch. Field source offsets and five-bit extraction match the original instructions. Two fresh read-modify-write operations insert the first field into target0 bits 25–29 and the second into target1 bits 8–12 while preserving other bits. R0 returns target1’s address; R1, R2, R3, and SP match the asserted values.

The fixture memory is stable and separately allocated. Aliasing, mutation between byte/word reads, concurrency, ownership, and physical meaning remain unresolved. This is private scoped evidence, not canonical admission.
