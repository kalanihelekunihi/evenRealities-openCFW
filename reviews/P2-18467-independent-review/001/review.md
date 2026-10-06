# Independent review P2-18467

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay of the pinned image yields the exact 92-byte span `0x46018E..0x4601EA`; instruction and PC-reference manifests match the candidate. The wrapper first loads the global via the word at `0x46061C`. If initially zero, it calls `0x43D0CE`, tests bit 1, and performs the described ordered stack/literal argument setup and `0x43D574` call on that path. The other flag tests use separate fresh `0x43D0CE` calls, with bit 0 checked first and bit 2 checked only on the bit-0-clear route. The `0x43CE9E` route receives the stated arguments; the bit-2-clear branch reaches the epilogue without resetting R0.

For an initially nonzero global, the code separately reloads through retained R2 without retesting null, sets R1 to `0xFFFFFFFF`, and calls `0x4497B6`; its result is discarded. POP restores saved R5/R6/R7 into R0/R1/R2 and returns through saved LR. The saved slots can be overwritten by the diagnostic path (including R0=77); therefore this wrapper does not explicitly return a child status or boolean. Fresh flag reads and mask branches were checked.

Child contracts and broader global ownership remain unresolved. No source, gate, or admission changes.
