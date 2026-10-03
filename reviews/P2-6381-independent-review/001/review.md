# Independent review 6381

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet and source hashes match for 0x42E1EC–0x42E220. GNU Thumb decoding confirms an eight-byte register-save frame and the described loop. Inputs are retained as R3 (byte pointer), R1 (length), and R2 (optional state pointer). Null state initializes R0 to 0xFFFFFFFF; nonnull state initializes R0 to the complement of a fresh state word. R4 starts at zero. While unsigned R4 is below length, the routine freshly loads the literal table base, loads input byte `[R3+R4]`, XORs it with the current state and masks to 8 bits, reads a word at `table_base + index*4`, then updates state as `table_word XOR (state >> 8)`. R4 increments with 32-bit wrap. On exit it complements R0, pops R4/R5, and returns.

The optional state pointer is never written. With zero length, the return is zero when state is absent, or the initially loaded state word when present. The table contents and algorithm purpose are not interpreted here; no CRC claim, C equivalence, or admission is made. No canonical files or gates changed.
