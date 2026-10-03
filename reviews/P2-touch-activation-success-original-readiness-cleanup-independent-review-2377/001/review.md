# Independent review 2377

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 6ad5beb39f599b5ba07f6729be1eeff2e45bafec16a45416baa73a50a59d4fdd; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pinned 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87. Root body [0x4AF4,0x4BA0), cleanup bodies [0x4DB8,0x4DC4), [0x4DC4,0x4DEC), [0x4DEC,0x4E1C), [0x4E1C,0x4E36), and additional span [0x4E36,0x4F6E) match receipt hashes; candidate artifact hashes match.

Isolated replay passes all 2,592 combinations: kinds 0–8, counts 0/1/3, four halfword values, three byte fills, four post-helper status values, and readiness busy clear/set. Original 4AF4, 5C8E, arithmetic 5FA4/A6C0 and both cleanup chains execute without function interception. Activation 4ABE and the mode/row helpers are controlled as stated.

With supplied root clock zero, the original scaler yields a zero poll budget. Readiness bit 7 clear preserves the accumulated status; bit 7 set replaces it with 4. Both paths set context byte 118, invoke mode 1 and row helpers 0/1/2, then run the original copy/finalization cleanup and clear descriptor bit 15. Combined ordered writes, full fixture memory, helper order/arguments, final status/descriptor assertions, R4–R11 and SP pass. The replay output matches the candidate replays.json hash.

**Limits:** The fixtures use flags byte 0x81, stable pointers and distinct row buffers; positive-budget polling, aliases, concurrency and dynamic post-helper effects are not established. Activation 4ABE and post-readiness mode/row helper results are controlled; no broader activation behavior is inferred. The modeled clock/status memory and CPU execution do not establish physical hardware behavior. Evidence remains private and accepted:false.
