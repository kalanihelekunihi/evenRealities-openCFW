# UART callbacks through native planning and PCM2.2 apply routing

**116 original/source comparisons PASS:77 complete and39 stop before a real apply/transition/voltage child.** Both existing native PCM2.1/PCM2.2 planners execute. PCM2.2 additionally executes its reused native apply/selector routing through the authenticated initialized27-entry transition table. PCM2.1 stops before actual apply0x5A0FC4. Nontrivial PCM2.2 children and voltage0x5A423C stop at their actual entry; three real no-op transition entries may complete. No child return is fabricated. [Results](results.json), [exact receipt](reproduction-receipt.json), [successor ledger](INDEX.md).

For supplied active-buck/valid-signature UART enable fixtures, temperatures0/1/2/3 and CPU0 yield profiles7/6/5/4 withTON6; CPU1 yields15/14/13/12 withTON7. These are profile/TON selector values, not measured voltage/frequency or live temperature. Both families match for this bounded input set. The shared1E00device mask is the group metadata handed to planning, not the individual UART enable bit.

Malformed temperature255 yields planner error5; callback returns without apply, but UART wrapper ignores that error, sets the per-device command and can return0 under supplied ready status. Wrapper success therefore does not prove a power profile was applied. Gate/invalid-signature and last-device/sibling/status behavior retain previously established limits.

Reused source bodies/headers and actual ELF are hash-pinned. Existing startup-evidence helper is imported read-only to retrieve authenticated transition DATA; existing original decompressor and initialized-ITCM proof are reused, not rerun/reinvented. StartupFFFFFFFF is an uncached trim sentinel, not live chip revision. No authentic INFO/device calibration or actual callback-family choice is inferred.

This successor corrects **unexercised dependency aliases** in the earlier before-planner ELF: PCM2.1 classifier entry is5A0A70, PCM2.2 apply entry5A453C. Earlier fixtures never reached those aliases; their bounded before-planner results remain unchanged. Current executed paths do not exercise classifier because action3 is used. Complete source closure is not claimed for remaining original dependencies.

MMIO read/write sequence, callback metadata, saved mask, relevant cached profiles and child-entry arguments match. Stack scratch/profiling RAM reads are not compared; table pointers are authenticated DATA, not retained opcode arrays. Real power-register semantics, physical settling, timer execution, full scheduler and delivered exceptions remain outside scope.

Next bounded source work is native PCM2.1 apply/TON/timer composition, PCM2.2 selected transition/voltage children, codec deadline/command receive, and ISR exit/resume handling after notifier's yield-pending flag. Existing sources should be reused wherever validated. No global source-exhaustion or missing-tool claim; no Git mutations, production/device/shared-state edits.
