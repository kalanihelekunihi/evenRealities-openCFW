# Independent review 2375

**Result:** PASS_SCOPED.

Receipt hash 1193d28f77067cfc62d836427be4ab3e2563e12c1c5a26f927b8a1084160410b; source hash 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pinned source. Root body [0x4AF4,0x4BA0), cleanup body ranges [0x4DB8,0x4DC4), [0x4DC4,0x4DEC), [0x4DEC,0x4E1C), [0x4E1C,0x4E36), and additional [0x4E36,0x4F6E) match the recorded hashes; included evidence files match their receipt.

Independent isolated replay passes 972 fixtures. Original 4AF4 and both cleanup chains execute; only 6AC0 and 4ABE are controlled. Supplied activation returns 1, 2048, or 0xFFFFFFFF take the common cleanup path. The root sets descriptor word 8 bit 15 and clears cfg byte 118 before the controlled calls; after cleanup it freshly reloads descriptor and clears bit 15, returning the activation status. The 6AC0 result is ignored.

The ordered write oracle and complete modeled memory, helper order/arguments, descriptor/cfg state, status, R4-R11 and SP assertions pass. Replay output hash matches candidate replays.json.

**Limits:** Flags byte 0x81 and distinct stable row/source/destination buffers only; aliases, mutations and other flag combinations remain untested. Only the supplied non-success activation statuses are covered. The success path, physical hardware effects and broader activation integration remain unresolved. Private bounded evidence only; accepted:false.
