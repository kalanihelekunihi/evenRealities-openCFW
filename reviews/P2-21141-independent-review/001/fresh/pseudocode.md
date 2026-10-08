# Low-byte dispatch and first two word modes

Partial/unaccepted;110 instruction bytes4809C4..480A32. PUSH R3,R4,R5,LR16;R4=entryR1 pointer;R0=UXTB(entryR0). Exact dispatch:0→4809E8,1→480A1C,2→480A32,3→480AD4,4→480B66,5→480BC2,6→480C2E,7..255→480C52. Other branches unresolved here.

Mode0: R0=pointer from literal480EB0; fresh word[R0] stored SP0 (overwriting saved entryR3). ReloadSP0 and clear low5bits via logical right5 then left5; storeSP0. If R4nonnull, read byte[R4]; if byte exactly1, reloadSP0 OR5 and storeSP0; otherwise (including null) reloadSP0 OR25 decimal and storeSP0. ReloadSP0 then store word[R0]. ReturnR0=0 at480A18;POP R1,R4,R5,PC releases16, R1 receives final scratchSP0 value, not entryR3. Only one initial source word read; no late reread before write. Preserve scratch loads/stores for aliasing with passed pointer and memory.

Mode1: load same literal pointer, fresh word storedSP0, reload and clear low2bits via logical right2 then left2, storeSP0; reloadSP0 and write sourceword. Branch480A18 returns0 with same POP/R1 scratch behavior. R4 not dereferenced. No helpercalls, nullguard for word pointer, physical semantics, C/freeze/fullcoverage/equality claim. Remaining dispatch arms require recovery.
