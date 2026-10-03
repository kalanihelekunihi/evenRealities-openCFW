# Independent review 2431

**Result:** PASS_SCOPED.

Candidate 2428/001 receipt SHA-256 9574bdb3e5a5b7a95cbcef5a19cf5c2b4c377b3e970d912ba2900594000f6274; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches its pin. The three owned bodies [0x752E,0x757E), [0x72F8,0x73F6), [0x7288,0x72F8) match the recorded hashes and candidate artifacts match.

Independent replay passes 64 fixtures; output hash matches the candidate replays.json. Original dispatcher, measurement, budget helper and A6C0 division execute. Four deeper calls (6AC0, 685C, 6928, 6980) are controlled, with exact arguments/status effects recorded.

The dispatcher retains the original row bounds/kind while the budget helper reads the replacement mapped row and parameters after the controlled mode call. Budget formula, wrapped arithmetic, mode-dependent count pair, multiplier, A6C0 numerator/divisor and poll budget are asserted; sample destinations and ordered parent writes/status/R4-R11/SP also pass.

**Limits:** Fixtures are a paired bounded selection of modes/counts/multipliers, not a Cartesian or exhaustive budget domain. The four deeper helpers are controlled; physical polling, helper effects and general measurement behavior remain unverified. Private evidence only; accepted:false.
