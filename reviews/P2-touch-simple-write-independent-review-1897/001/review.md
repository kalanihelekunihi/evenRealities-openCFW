# Independent review 1897 — simple write

**Result: PASS_SCOPED.** Candidate `touch-simple-write-85d4-1890/001`; receipt SHA-256 `52f0cc68997c5931757b893ff8eaddbfc15de8d1ec7cea9e27b89b0da9cd6d7a`.

Candidate binds to the pinned source image and exact body [0x85D4,0x867C), 168 bytes/80 instructions; receipt, disassembly and fixture hashes agree. An isolated run passes all 60 fixtures and produces byte-identical replay JSON.

The recovered ordering is consistent with instructions: compute offset remainder and iteration count, derive initial destination, then for each chunk invoke provider+20 before patch-copy and 8554. Read callback return is ignored; modeled callback writes fill scratch. The writer’s nonzero return exits immediately. On success, context+24 is updated, remaining-size/input/destination/counter state advances with fresh width loads and low-two-bit destination stride masking. The width-128 positive-size fixture scope supports the stated chunk behavior and failure stops.

All positive-size fixtures use width 128; zero-width/wrapped-count behavior, mutable context or callback mutations, physical storage, and concurrency are not covered. Provider read and 8554 are controlled; helper side effects are synthetic. The 8554 fourth register is captured but not independently asserted. No canonical admission.
