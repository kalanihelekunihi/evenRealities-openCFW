# G2 bootloader SRAM-word setter source closure

The authenticated eight-byte entry at `[0x0041583C,0x00415844)` loads the
single literal `0x200270CC`, stores its `r0` argument as one complete 32-bit
word, and returns. Its sole whole-image direct caller is `0x0041FABA`, which
passes zero during a bootloader initialization path. No semantic name is
assigned to the cell without stronger evidence.

`runtime_store_200270cc.c` preserves the complete word-store contract. The
host fixture redirects the target macro to ordinary storage and covers zero,
one, all-one, and mixed-bit values. Both reviewed compilers emit the same
relocation-free 12-byte leaf at `0x004348C4`; the final four bytes are the
authenticated SRAM address literal. The complete stock entry is replaced by a
reviewed non-linking `B.W` plus two NOPs.

The canonical 1,338-byte overlay hashes to
`bd4d3fcb1c8fab3361e6d1a9dfdc5aff920d876589c8de37ecf7ac71dbf0f7ce`.
The 149,938-byte provider hashes to
`0e9b156ce6e251af4d15f7411ba09fcc509d9802281aeb4a5267f64f8e77f1a8`
and accounts for 1,331 compiled-source bytes, 1,800 generated redirect bytes,
eight alignment bytes, and 146,799 retained authenticated bytes. The Linux
provider hashes to
`0f7bdec78f08770a42a37f8b1049022ec1dd1c6b4bd2ca53771ca63a0e2f214e`.

The unsigned canonical package is 4,731,516 bytes with SHA-256
`95221a53071e8d5cec05ba5b3b58e291ceb5a9db4e0ba193be0b59a5d7e4190a`;
its 4,322,480-byte flash plan hashes to
`a372e19791d80acaf92d1390e11367b09a560f3246ac4f792e8e33fcd9c0ba61`
and contains 6,226 placed, two unresolved, five container-only, and six
protected regions. The Linux package is 4,507,526 bytes with SHA-256
`2db03bb1ae912db40231b9b19a33e9966f6d1695990b53777b0a9d72c0e754db`
and contains 3,308 placed regions. No package was signed, transmitted, or
flashed.

Software closure is complete for this setter. Live SRAM and boot-progression
evidence remains explicitly blocked because no authorized responsive G2 right
temple is available; the left temple remains on stock firmware.
