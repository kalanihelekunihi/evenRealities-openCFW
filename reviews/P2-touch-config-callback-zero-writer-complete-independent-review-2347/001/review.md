# Independent review 2347

**Result:** PASS_SCOPED.

Receipt 6b920233168e04aa348610b71502fc1f203a32d67c4b5dcea69945364b8cce24 pins the expected source and body [0x4C7C,0x4DA8); all evidence hashes recompute. Isolated replay passes all 192 fixtures.

Decoded instructions confirm the initializer clears cfg.word20 exactly at 0x4CBC, then proceeds through config and parameter setup to original 6AC0(0,ctx). For old modes 0/1/2/5/6/7, helper status zero reaches controlled 4C72; modes 3 and 255 return 1 without reaching it. Across cases the word20 write is exactly one zero store and final word20 remains zero, parameter byte35 updates reflect the halfword4/6 branches, and call/status assertions pass.

R4-R7 and SP restoration, return status, stop at the caller sentinel, and body extent checks pass. The literal load at 4CB6 targets 4DA8; the complete packet excludes that literal from its body span.

**Limits:** Final helper 4C72 is controlled and has no effects in this replay; its real behavior is unresolved. These fixtures only show no later local initializer write changes cfg.word20 in the tested distinct-memory cases. They do not prove persistence under real helper effects, intervening callers, or aliases, nor do they establish that 71C8 always sees a null callback. No physical behavior or canonical admission is claimed; accepted:false.
