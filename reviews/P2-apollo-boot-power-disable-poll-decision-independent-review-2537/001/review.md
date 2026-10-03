# Independent review 2537

**Result: PASS_SCOPED.**

The exact candidate `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-disable-poll-decision-2536/001` binds to the pinned source and table. The body hash, extra group-mask literal, receipt and artifact hashes match. I reran the verifier from an isolated output directory; all 608 original-instruction cases pass.

The cases independently vary first and second observations for all recognized groups and exercise invalid indices. The decoded path returns 1 for lookup failure, unrecognized group, or a recognized group with no group bit in the first read. If the first read intersects, it rereads the same register and returns 1 when the individual mask intersects, otherwise 0. The read hook models these separate observations; fixtures confirm 0/1/2 reads, no writes, returns and register/frame preservation. The extra literal at `0x41CB00` is `0x30000001`, part of the recognized group set.

This establishes the bounded decision helper behavior with modeled register reads. It does not establish physical power-domain semantics, feasibility of concurrent changes, alias behavior, or enclosing caller ownership. Private evidence only; accepted:false and no canonical admission.
