# Independent review 6339

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet and locked-source body hashes match for 0x42D890–0x42D8F0. GNU Thumb decoding confirms a 28-byte push plus 20 local bytes (48-byte frame), captures the two incoming pointers in R5/R6, and initializes SP16. It reads the descriptor word, clears its top byte, subtracts 8 with 32-bit wrap, then calls 0x42D84C with 1. The returned selected address is passed as the second argument to 0x4153A4, with the literal-loaded first argument in R0; that result is written through the output pointer in R5.

A fresh output-word read selects the paths. If zero, the routine places the literal and constants in stack argument slots, loads three further literal arguments, calls 0x4176CE, ignores its result, sets R0 to zero, and branches to cleanup at 0x42D9EA. If nonzero, it freshly reloads the output word and calls 0x4154D2 with arguments (word, 8, 0), ignores that result, clears R7, and branches to the continuation loop at 0x42D93E. No null checks precede the input-pointer dereferences.

The packet stops before either continuation completes; child purposes and later behavior remain unresolved. No filesystem-purpose, hardware/runtime, C-equivalence, or admission claim is made. No canonical files or gates changed.
