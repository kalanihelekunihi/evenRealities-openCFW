# Independent review 6321

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes match the pinned image and its 0x42D4B6–0x42D562 extent. GNU Thumb decoding agrees with the map. In the nonzero-flag path, the code reads a low-seven-bit field, compares it with 16, and, when at least 16, performs a second fresh read and subtracts 15; otherwise it uses zero. A separate low-seven-bit field is similarly compared with 10 and, if at least 10, freshly reread and reduced by 9. Each result is inserted into a fresh word and stored. It then freshly loads the captured global value into bits 10–13 of the current R7 word and clears bit 8 in another fresh word.

At the shared path, the low ten bits of the current R7 word are reduced by R6 with truncation to ten bits, preserving upper bits. A fresh flag byte selects either setting the low six bits to 1 or clearing them. Four separate fresh read/clear/store operations clear control bits 29, 28, 31, and 30. The routine returns zero and restores R4–R8 and PC from its 24-byte frame. The initial gate-not-3 route bypasses the alternate cleanup and reaches that epilogue after its two restores.

This is static source evidence only; it makes no hardware, runtime, or C-equivalence claim, and changes no canonical artifact or gate.
