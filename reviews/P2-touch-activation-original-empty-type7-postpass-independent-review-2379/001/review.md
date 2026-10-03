# Independent review 2379

**Result:** PASS_SCOPED.

Receipt SHA-256 e7d6caa0cbf275ca40a25e1dd18e4f7649e08b9802ae8972df6a3f7ba335f2e9; source hash 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87. Root [0x4AF4,0x4BA0), cleanup bodies [0x4DB8,0x4DC4), [0x4DC4,0x4DEC), [0x4DEC,0x4E1C), [0x4E1C,0x4E36), and additional span [0x4E36,0x4F6E) match the pinned hashes. Candidate evidence files match their receipt.

Independent replay passes all 2,592 cases, and replay output hash matches the pinned replays.json. Original 4AF4/readiness/scaling and both cleanup chains execute with no function interception; 7BB8 and 7B6A are also original. The harness controls 4ABE and the stated later mode/row helpers.

For the exercised root byte 36 equal to zero, 7B6A skips type-seven traversal and 7984, clears freshly loaded cfg byte 115, reloads the context descriptor, clears descriptor word 8 bits 4/5, and returns zero. The resulting stores precede cfg byte 118 set to one. The full-memory and ordered-write oracle, outer call order, cleanup dispatch/item order, status, R4-R11, and SP assertions pass.

**Limits:** Only root byte 36 equal to zero is covered; type-seven traversal and nonzero root-count behavior are not established. Flags 0x81, stable pointers and distinct row buffers are fixture conditions. Activation 4ABE and other post helpers remain controlled; null context, aliases, mutations and full caller closure are unresolved. RAM and readiness conditions are modeled; no physical-hardware or canonical-admission claim is made.
