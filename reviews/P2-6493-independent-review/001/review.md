# Independent review 6493

Disposition: **PASS_SCOPED**; `accepted:false`.

Both source spans and packet-file hashes match the locked image. GNU Thumb decoding confirms the first leaf sign-extends R0's low halfword into R1 and branches on its sign. The negative path returns with original R0 and performs no store. Otherwise it masks the original input to five bits, forms `1 << index`, derives the word index from the signed-low-halfword value shifted right five, stores the whole mask word through the literal base, and returns that index.

The second leaf tests the signed low halfword. It shifts R1 left four with 32-bit wrap semantics, then on the nonnegative path stores the low byte at the literal base plus sign-extended index and returns that index. On the negative path it masks the signed index to four bits, adds the negative-offset literal to form an address, stores through `[R0,#-4]`, and returns the computed pre-minus-four address. No bounds or status normalization appears in these spans.

This confirms only the two leaf instruction sequences; it does not establish hardware purpose or safety of arbitrary indices.

No canonical files or gates changed.
