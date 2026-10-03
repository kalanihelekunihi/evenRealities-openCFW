# Independent review 2437

**Result:** PASS_SCOPED.

Receipt SHA-256 b640f2ee7dea87c40925b7e0f57c2dde9dc57f2250c3d4b8a284f5ce2da2a7a0; source hash 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pin. Seven body ranges (dispatcher, measurement, budget, poll, scaler, start helper, and register loader) match all listed hashes; evidence-file hashes match.

Independent isolated replay passes all 64 cases and matches pinned replays.json. Original dispatcher, measurement, budget, poll, scaler/divider, 6928 start helper and 9178 loader execute; only 6AC0 and 685C remain controlled.

For normal and type7 sequence addresses containing distinct words, original 6928 sets control bit31, performs ordered control/command writes and readbacks, calls 9178(base,6,sequence), then applies OR6, OR1 and writes 1 to offset3800. The loader writes six words in order to offsets3020–3034. Polling and final control clear follow. Fixture write/call/division/poll ledgers, status, item effects and R4-R11/SP pass.

**Limits:** Peripheral reads and samples are modeled; no physical start or timing behavior is inferred. Readback variation is not exercised. Two helpers remain controlled; literal pools and excluded seams retain their separate ownership limits. Private bounded evidence only; accepted:false.
