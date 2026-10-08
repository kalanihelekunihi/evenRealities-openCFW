# Startup ITM/debug release source closure

This batch replaces the selected linker's two numeric startup teardown entries423d20/423dd0 with native source and closes their complete local dependency cluster. Existing historical symbols and raw Ghidra extracts already describe stage-one/stage-two/debug-disable bodies; this is current source integration and original-instruction validation, not a claim that those addresses were previously undiscovered. The historical symbol manifests are no longer present in the current tree. No removed overlay or retained opcode body was restored.

Locked bootloader SHA-256 **f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5**, little-endian Thumb, load0x410000. Independent reconstructed [C](../../../../components/bootloader/initializer_callbacks/startup_shutdown.c) and [helper interfaces](../../../../components/bootloader/initializer_callbacks/startup_shutdown.h). Candidate5539579c6fe6821387b10bef54f82b50138973806889f909d37b955e5ecdf31b. Existing power selector28, query descriptors, critical-save and equality-wait source are reused; no new numeric dependency is introduced.

## Functions and data

| Original range, exclusive end | Source helper | Body bytes visited |
|---|---|---:|
|423d20..423d58|startup_shutdown_first|56/56|
|423d58..423d7a|shutdown_prepare|34/34|
|423d7a..423d9a|shutdown_wait_clear|32/32|
|423da0..423dc4|shutdown_wait_slot|36/36|
|423dc4..423dce|shutdown_wait_zero|10/10|
|423dd0..423e0c|startup_shutdown_second|60/60|
|422468..4224b2|shutdown_clock_release|74/74|
|4224b2..42252e|shutdown_resource|124/124|
|42252e..422574|shutdown_debug_release|70/70|

Total9 bodies496/496 observed bytes in903 direct comparisons. Each original trace instruction is checked against locked bytes. Literal pools/padding are excluded from body counts, not claimed as source completeness.

| Address | Recovered role |
|---|---|
|200271a1|8-bit local clock reference count|
|200271a2|8-bit power28 reference count; increment wraps255→0|
|200271a3|8-bit trace/debug reference count|
|200271a4|power ownership:0 inactive,1 enabled here,3 previously active; other nonzero values preserved until final release|
|200271c2|stage-two enabled/cache byte, cleared on final local release|
|200271c3|8-bit stage-two reference count|
|e0000000+4*slot|ITM stimulus-port register; wait(mask3,value1)|
|e0000e80|ITM TCR:SWOENA bit4,ITMENA bit0,BUSY bit23|
|e000edfc|CoreDebug DEMCR:TRCENA bit24|
|40020250|local debug clock control:clear bit0, then bits1..3|
|40021004/40021008 mask04000000|native power descriptor28 command/status|

The register identification is independently corroborated by the already pinned CMSIS5.9.0 `core_cm55.h` at1136,1171,1186,1198,3193,3591 in `upstream-worker/ambiqhal-apollo510/cmsis-5-590`. Its Apache-2.0 acquisition/provenance remains unchanged. The pinned Ambiq SDK5.1.0 header `am_hal_itm.h:127` declares `am_hal_itm_disable`; matching API context is not proof of the stock producing source revision. No upstream implementation body was copied; this source is independently reconstructed from firmware instructions. Historical raw `00422468.c` expresses decompiler `undefined8` returns and privilege pseudocode; original instructions establish the usedR0 status and directPRIMASK restoration.

## Behavior and call flow

`startup_conditional(41fa98)` calls first then second when flag20027198 is1; its existing orchestration spins on a nonzero result before subsequent external-mode and power-update calls. These nine helpers themselves do not spin indefinitely in the tested finite wait profile.

First calls prepare and **ignores its result**. Prepare checks stimulus slot0 masked value1 and then ITM busy-clear; either failure returns4, otherwise delay argument500. First still clears SWOENA then ITMENA using separate volatile reads/writes. Its subsequent wait has mask0/expected0, so the native equality helper immediately succeeds. It then calls shared debug clock release and translates returned3 to0. A failed preparation can therefore still produce successful first-stage return after register changes. This is not a successful output flush guarantee.

Shared clock release savesPRIMASK, decrements nonzero clock count, clears clock fields only at count0, calls trace/debug release **regardless of remaining clock references**, discards that result, then calls power resource disable0 and returns only the power resource's result. Nested saves restore the pre-existing interrupt mask. Trace/debug release decrements count; remaining references return3. At0 it clears DEMCR TRCENA and native-waits(mask01000000,value0,count10), returning wait status. The caller ignores that status.

Resource enable accepts any nonzero low byte. It increments its byte count, and if ownership0 stores1 before native-querying power28. Already-powered sets ownership3; otherwise native power enter28 is called. Query/enter statuses are ignored. Disable decrements if nonzero; remaining references return3. At0, ownership exactly1 calls native power leave28, ignoring its status; all ownership values then clear to0. Ownership3 avoids disabling a previously enabled shared power domain. Counter wrapping and ignored errors are retained, not repaired speculatively.

Second savesPRIMASK and decrements its local count. Remaining local references return3, so the orchestration can spin on this result. At0 it clears200271c2, calls shared debug clock release, translates3 to0, and restoresPRIMASK. Thus the same numeric3 has differing caller behavior depending on which reference layer produced it.

## Validation and practical limits

[903 original-instruction comparisons](comparison.json) cover counts0/1/2/255, ownership0/1/2/3, both interrupt masks, callbacks absent/present, power28 already active/inactive, synthetic acknowledgement success/failure, low-byte truncation, count wrap, independent stage-two/resource counts, wait timeout and readiness transitions at delay1/1000/1001. Both machines execute native critical/query/power28/equality-wait bodies. Only elapsed delay and registered callback bodies are controlled. Ordered MMIO stores, returned status, all six state bytes,PRIMASK and resulting registers compare. MMIO hooks record only system/peripheral addresses; no SRAM-write hook or native-copy answer model.

`negative-control.failure.json` rejects a temporary source returning preparation failure: stalled slot/busy fixture stock returns0 and writes disable registers while bad source returns4. Production source is unchanged. The failed-run log is preserved; this proves sensitivity to that policy, not physical timing.

Interoperability/CFW implication: teardown here is **ITM/debug release**, not a UART RX/TX cancel, scheduler stop, task drain or general hardware shutdown. A0 return cannot be used to certify final trace delivery, zero references, successful power acknowledgement, buffer release or safe deletion. Existing UART borrowed-pointer/error semantics remain intact. No allocations/free operations exist in these nine bodies.

Integrated candidate reconciliation is separate: all seven normal/malformed/synthetic-interruption cases and affected startup/clock/UART/logger/kernel/native-copy regressions must pass on the exact frozen ELF before promotion. Integration startup/logger provider models remain; native903 direct comparisons supply the evidence for these new bodies. Physical CoreSight access semantics, callback reentrancy/live concurrency, elapsed time, full task restoration, whole-source completeness and byte equality remain outside this proof.

Run native comparisons with `/Users/kalani/.local/share/opencfw/venv/bin/python g2/analysis/bootloader-completion-2026-10-06/inventory-worker/startup-shutdown/verify.py --elf <candidate.elf> --output <receipt.json>`. Compile/link integration is included in `g2/components/bootloader/thread_creation/Makefile` and `startup_source_image.ld`. This Mac requires the approved offline execution context for Unicorn; the native tool crashes under the restricted sandbox.

## Promotion

Checkpoint5539579c6fe6821387b10bef54f82b50138973806889f909d37b955e5ecdf31b promoted after all7 cases PASS,25 direct/regression receipts PASS,667 files/171 objects unchanged with exact frozen copies authenticated,491 mappings PASS and zero manifest mismatches. Prior64e52504/4edd remain preserved. Selected OTA entries15→13, same address-based scope; no new aliases. Seven-case observed instruction footprint remains38764/148599, not source-completeness or native integration coverage for these modeled startup bodies.
