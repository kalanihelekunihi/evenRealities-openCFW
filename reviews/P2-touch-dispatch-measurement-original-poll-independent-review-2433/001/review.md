# Independent review 2433

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 e0a12f1292fbe4f4ade3792efd3a6c8511e7682259b36e431e560759ba6ab803; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches. Five owned ranges [0x752E,0x757E), [0x72F8,0x73F6), [0x7288,0x72F8), [0x6980,0x69BA), [0x5FA4,0x5FBA) match their hashes; candidate evidence files match.

Independent isolated replay passes all 64 fixtures and output hash matches pinned replays.json. Original dispatcher, measurement, budget, poll, scaler, and unsigned divider execute. Only 6AC0, 685C and 6928 are controlled.

The replay checks the computed budget passed into poll, original scaling/division arguments, bounded modeled status-read transition, countdown values, completion behavior, exact ordered writes and item destinations. Zero remaining count replaces measurement status with 256 and suppresses sample stores; positive remainder preserves mode status. Dispatcher OR results and R4-R11/SP checks pass.

**Limits:** Status transitions are synthetic and only immediate/second-read plus zero-count paths are covered; physical timing and long timeout behavior are not established. Three deeper helpers remain controlled; their effects and general pointer behavior are unresolved. Poll literal/seam ownership remains limited to the separately pinned evidence. Private bounded evidence only; accepted:false.
