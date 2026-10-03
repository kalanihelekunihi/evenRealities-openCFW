# Independent review 2957/001

**PASS_SCOPED**; `accepted` remains false.

I reran all 768 fixtures in a fresh directory. Source/body hashes match the locked image, and candidate/replay output hashes match their receipts. The original operation-1 path reads the condition byte from the supplied pointer into the decoder record. The independent expectation varies that byte over 0–3 together with type, choice, low-bit flag, clock state, and PRIMASK. Ordered state publication, save→decoder call order, status zero, PRIMASK restoration, checked high registers, and SP pass.

Other operations and snapshots, transition branches, aliasing/volatile changes, physical effects, and broader caller behavior remain outside this fixture scope.

Candidate receipt SHA-256: `202b0a9d095eb40d203a9890e0c28c792bd12afa7e4f540aba1796f0190f2cef`.
