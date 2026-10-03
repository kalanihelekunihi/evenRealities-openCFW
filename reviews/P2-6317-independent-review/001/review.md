# Independent review 6317

Disposition: **PASS_SCOPED**. `accepted:false`; this is a source-bound static review only.

I verified the packet and input hashes against the locked image. The claimed 0x42D3BC–0x42D43C extent is 128 bytes, and its body hash matches the pinned source. GNU Thumb disassembly agrees with the packet's instruction boundaries and control flow. The opening push saves R4–R8 and LR (24 bytes). A fresh global-word read extracts bits 4–5; value 3 branches to the adjustment path, while the other path restores low six bits and bits 10–13 from separate freshly loaded globals before branching to 0x42D55C.

On the value-3 path, the routine takes a fresh low-10-bit field read, adds 12, and branches on unsigned `>= 1024`. The saturated branch computes `1023 -` a second fresh low-10-bit read; otherwise it uses 12. It then makes a third fresh word read and stores the merged result with upper bits preserved and the low ten bits formed by wrapped addition and truncation. Next it freshly reads the six-bit destination word, inserts 5 into bits 0–5, stores it, and calls 0x41D1C0 with argument 5; the child result is not consumed in this extent. The PC-relative references and destinations match the packet.

The packet stops at the call, so continuation and return behavior remain unresolved. It establishes no hardware meaning, runtime result, C equivalence, or corpus-admission claim. No canonical artifacts or gates were changed.
