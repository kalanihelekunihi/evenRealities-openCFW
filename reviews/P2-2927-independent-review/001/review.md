# Independent review 2927

**PASS_SCOPED**; `accepted` remains false.

The source image and body [42B294,42B69C) hashes match; candidate output hashes match. Isolated replay passed all 360 cases. Original transition instructions run with no call interception. The fixtures use ten unequal ordered pairs with new rank greater than old rank, inactive word zero, equal category/comparison 3, and non-special indices; therefore the observed branch has exactly four ordered target writes, no child calls, and returns incoming R3 in R0. R4–R11, SP, PRIMASK and stop state are checked. Profile words are identical across indices in each fixture, so this does not test distinct profile payloads, alternate current ranks, active/descending paths, special indices, volatility/aliasing, flags, full register effects, or hardware semantics.

Candidate receipt SHA-256: `c68a77ad5270fcc8a58b9798081d3f0936747cb7c25365df73fa933d013ab0bc`.
