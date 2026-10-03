# Independent review 2427

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 b544a55776aa0feaea91948ad2bf9ec6fc0875dcde7893b97b6317cccaeb7daf; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches. Original 72F8 body is 254 bytes/121 instructions and hashes to 87c5919c3bfead1e933bd9dec614fda0e7f7d339b7f464684e6c37816f4ca4d2; evidence files match receipt hashes.

Independent isolated replay passes all 576 cases and exactly matches pinned replays.json. Controlled mode helper 6AC0 replaces context pointers and the selected mapping entry; memory-read and write ledgers distinguish cached parent values from later fresh loads.

The original parent keeps its pre-call configuration, peripheral, sequence and mapped row/item indices for the subsequent 685C/6928/7288 arguments and sample access. On the completion/nonzero-status path, it freshly reloads ctx.word12 and the replacement row's item pointer, while using the cached row/item indices. Final peripheral control read/write still uses the original cached peripheral. Ordered helper args, reads/writes, untouched old/replacement memory, completion return, R4-R11/SP pass.

**Limits:** All five helpers are controlled; their own pointer behavior and mutation effects are not evidence of actual helper behavior. Fixtures cover the supplied modes, indices and completion/status branches; no physical measurement or general pointer-lifetime behavior outside this body is inferred. Private bounded evidence only; accepted:false.
