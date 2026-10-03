# Independent review 6549

Disposition: **PASS_SCOPED**; `accepted:false`.

The 166-byte source span 0x415CFE..0x415DA4 and packet hashes match. GNU decoding confirms the character case consumes one argument word, optionally writes its low byte, advances output only when nonnull, increments the count, and rejoins at 0x415F98. The string case consumes a pointer word and calls 415A7C for length. Nonnegative precision is compared unsigned against that length and clamps it when smaller. Pre-padding uses the original clamped length against positive width; source copying checks a fresh source byte for NUL and decrements the remaining R4 count per consumed byte. For negative width, the later padding calculation compares absolute width to the *remaining* R4, then requests the difference from 415A94. Thus after fully consuming the string R4 is zero and the post-pad can request the full absolute width, as the packet states. Output-pointer null checks suppress writes and pointer advances while helper return lengths still contribute to the output count.

Helper behavior, arbitrary pointer validity, and the continuation at 0x415F98 are outside this map. No canonical files or gates changed.
