# Independent review 2035

**Result:** PASS_SCOPED.

- Candidate receipt SHA-256 is 92f9928e8f742bc7345c5bf8d8bf6e0e3e96e04c843e00ce8a55134d7bc73bc8; source/image SHA-256 is 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87. All declared file pins match.
- Isolated replay reproduced all 24 fixtures. The two original spans implement flag-gated busy-byte updates followed by ordered masked 32-bit peripheral writes; literals, exact write order, R0 and SP match the model.
- Isolated replay was run from a copy writing only to /tmp/codex-review-2035; it completed with PASS and 24 fixtures.

**Limits:** Modeled memory does not establish physical clock effects, atomicity, concurrency or all indirect writers. No canonical admission is made.
