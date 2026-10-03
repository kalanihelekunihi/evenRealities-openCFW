# Independent review 2929

**PASS_SCOPED**; `accepted` remains false.

The source image and body [42B294,42B69C) hashes match; candidate output hashes match. Isolated replay passed all 216 cases. Original transition instructions run without function interception. Fixtures cover unequal ascending rank pairs with active word set, current index at its default zero and lower than the old rank, non-special indices, equal category/comparison 3, three profile patterns, two target patterns, flag values 0/1/255 and PRIMASK 0/1. Assertions verify the capped delta path, ordered stores (including saved high fields when flag is clear), absence of child calls, incoming R3 returned in R0, and R4–R11/SP/PRIMASK. Other current ranks, rank relationships, special-index/callback cases, dynamic aliases/flags, full caller clobbers and physical MMIO are unresolved.

Candidate receipt SHA-256: `1979bd9a340eca9ccf452fc61e20eb6cc9258a584ac90954fa45e0eec91667f4`.
