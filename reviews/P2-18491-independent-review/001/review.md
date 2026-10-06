# Independent review P2-18491

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 84-byte prefix `0x460580..0x4605D4`; instructions and PC-reference manifests match. It pushes R2/R3/R4/LR in a 16-byte frame and loads the global pointer from `0x460FB0`. Only an exact full-word value of 1 proceeds into the helper calls; all other values branch to external `0x460618`.

On the exact-one route, the first `0x43D0CE` result controls bit 1. The set path stores the literal at `0x461034` to SP4 and 344 to SP0 (aliases of saved incoming R3/R2), then calls `0x43D574` with the listed live arguments. After the bit-1-clear route, bit 0 and, conditionally, bit 2 are tested using separate fresh `0x43D0CE` calls. The bit-2 path calls `0x43CE9E`. Otherwise, `0x49292E` is called with R0-R3 live after diagnostics, without resetting arguments. Full zero branches to external `0x460614`; a nonzero result continues outside the mapped span.

The first guard bypasses all child calls and the external clear route. The remaining diagnostic/epilogue is not mapped, and child contracts are unresolved. Partial/unaccepted only.
