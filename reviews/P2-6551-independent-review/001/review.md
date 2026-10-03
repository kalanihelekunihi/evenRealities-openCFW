# Independent review 6551

Disposition: **PASS_SCOPED**; `accepted:false`.

The source span 0x415DA4..0x415E72 and packet hashes match. GNU decoding confirms uppercase X sets the case byte while lowercase x enters the same formatter without resetting that byte. For both cases, the low-byte long-long flag selects either an aligned two-word argument load or a single word with zero high word, and R7 advances by the corresponding aligned amount. With nonzero width the wrapper calls 415936 for digit length, subtracts that result from width, and calls 415A94 for padding without an explicit negative-width guard in this body. It then calls 415A08 with low/high value, output, and the fresh case byte. The unsigned path at 0x415E10 similarly selects one or two words, uses 415900 for length/padding when width is nonzero, then calls 4159A0. Child return lengths update output/count only under the shown output-pointer conditions; precision is unused in these spans.

Child arithmetic, formatting semantics, and the common continuation are outside scope. No canonical files or gates changed.
