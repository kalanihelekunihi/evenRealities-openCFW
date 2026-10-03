# Independent review 2425

**Result:** PASS_SCOPED.

Receipt SHA-256 50c5f349f01e02b7cd25332c7a6671a0f4d0f0681a313fc2e47f0ae6e94c21ca; source hash 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pinned value. Original body [0x752E,0x757E) matches its hash and all candidate artifact hashes validate.

Independent isolated replay passes 162 cases and its output hash matches pinned replays.json. The fixture replaces ctx.word12 during the first controlled 72F8 call, changes the original row's count and seeds distinct bounds/type in the replacement row; a memory-read ledger checks which address supplies later bounds.

Original instructions load ctx.word12 once before the loop and retain the computed row address. Later halfword 128/130 reads come from that original row even after ctx.word12 replacement; the caller passes the original ctx argument to the child. Exact later child arguments, count/status and R4-R11/SP pass. This does not constrain what the controlled child itself would do with the changed context.

**Limits:** Only the tested changes during the first child call and bounded slot/count cases are covered; arbitrary pointer/count mutation and aliases are unresolved. 72F8 is controlled; no physical measurement behavior or general child pointer contract is inferred. Private evidence only; accepted:false.
