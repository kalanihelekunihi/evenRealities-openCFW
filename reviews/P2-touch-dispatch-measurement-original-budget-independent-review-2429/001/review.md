# Independent review 2429

**Result:** PASS_SCOPED.

This review binds to actual candidate touch-dispatch-original-measurement-2426/001 (not the separate 2428 budget/divider candidate). Receipt SHA-256 bda7d8ba517c8303f6e0027d1aae7cc166b43ee2203897c153a06df85faca82c; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pin. Body ranges [0x752E,0x757E) and [0x72F8,0x73F6) match their hashes; candidate evidence-file hashes match.

Independent isolated replay passes all 64 cases, with output hash matching pinned replays.json. The original dispatcher and measurement bodies execute without interception; five deeper helpers (6AC0, 685C, 6928, 7288, 6980) are controlled.

The dispatcher retains its initial row/kind/start and completes its original count after the controlled first mode call changes ctx.word12. The original measurement independently uses the replacement row for its validity/sample destination, while the sample comes from the original cached peripheral. Every child argument, ordered configuration/item/peripheral write, status OR, unchanged old item buffer and R4-R11/SP assertion passes.

**Limits:** This candidate does not include original budget helper 7288 or unsigned division A6C0; those remain controlled boundaries in its replay. Candidate 2428 is the distinct later budget/divider composition. The five deeper helper behaviors and physical measurement are not established; fixtures are bounded to listed indices, kinds, starts and patterns. Private evidence only; accepted:false.
