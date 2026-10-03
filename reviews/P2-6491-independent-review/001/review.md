# Independent review 6491

Disposition: **PASS_SCOPED**; `accepted:false`.

The input table hash and survey file hashes match. I recomputed the type-byte histogram from all 97 source-verified records: type 3 occurs 39 times, type 4 occurs 41 times, type 2 occurs 6 times, and type 1 occurs 11 times. Applying the stated static type-2 branch predicate (byte 6 nonzero and word 8 nonzero) finds no records, matching the empty result list.

Consequently, under this immutable table snapshot none of the type-2 records reaches the later bitset construction based on word0>>5. This is only a static query of the supplied records. It does not prove dynamic unreachability, safety under mutation or aliasing, child behavior, or bounds generally.

No canonical files or gates changed.
