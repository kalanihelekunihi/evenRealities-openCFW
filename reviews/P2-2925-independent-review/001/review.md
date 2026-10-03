# Independent review 2925

**PASS_SCOPED**; `accepted` remains false.

The authenticated flash and ITCM images match inventory; three declared flash body hashes and output artifact hashes match. Isolated original-instruction replay passed all 2,880 fixtures (equal old/new indices crossed with category/comparison equal or different, categories, modes, low-field boundaries, two patterns and PRIMASK states). No function interception: unequal category comparisons take the original trim helper and delay/ITCM path; equal comparison skips those writes/delays. Assertions verify the target write ledger for the exercised path, the two delay(20) calls/1,250 ITCM loop entries when taken, incoming R3 returned through R0, R4–R11/SP/PRIMASK. R12 is not asserted preserved. Non-equal indices and other transition branches are not covered; synthetic stable profile/MMIO state, physical effects and volatile aliasing remain unresolved.

Candidate receipt SHA-256: `f6c42943d0e04b6a583e18cda3b7461db54b35a59bd798f92805b4810a916f72`.
