# Timer wake and restricted-wait provider source closure

**1217 PASS comparisons on one final ELF** `fcbca083d04257e4a95496d36041f601795a9a18351a1e42b0be7bcd43c8113a`:819 wake/unlock,74 port helpers,180 list providers,48 reused delete integration and96 reused restricted-wait integration. Reused integration fixtures do not add distinct whole-image coverage. [C/interface](../../components/audio/timer_wake_providers_offline/README.md), [pseudocode/layout](pseudocode.md), [exact final-build validation](exact-build-validation.json), [addresses/hashes](function-bindings.json).

## New executable understanding

Stock0x455370 removes the highest-priority queue waiter. With suspension0 it removes blocked state and inserts ready state; with suspension1/2 it inserts the event item into pending-ready and preserves blocked state. Return/yield flag uses **strictly greater** priority than current task. Equal-priority resume behavior in other providers is a different rule; this helper alone does not establish immediate context handover.

Stock unlock0x441F88 services TX deferred wakes of receivers first, then RX deferred wakes of senders, each under its own critical section. It uses signed-byte lock counts, stops when the waiting list is empty, and publishes both locks-1. It records a missed yield for each higher-priority wake; pending-list ownership remains until scheduler resume. Direct fixtures vary lock-1/0/1/2/127 and0/1/2 senders/receivers, priority46/47/54. Event fixtures cover suspension0/1/2, delayed/suspended state, mutable event/ready/pending indices and existing tasks. Deferred counters and accessed queue fields are constructed; a full producer history/queue-capacity state is not reconstructed by the direct unlock fixtures. The integration fixtures separately use real static queue initialization/copy. No ISR concurrency or physical IRQ delivery is inferred.

Public FreeRTOS ready/list bodies are compiled unchanged from the preserved pin. The selected queue-unlock body retains its MIT license and is exported with stock queue-sets-disabled macros. Five port helpers and sorted insertion are recovered source, not claimed pristine upstream matches. Nine selected original providers are compared including the already preserved public remove body; this is not a new nine-function whole-firmware coverage claim.

**All819 wake/unlock and96 restricted-wait source executions remain within native0x100000..0x110000.** Restricted wait now links native critical,unlock,wake,remove and sorted-insert providers. Its reached code no longer falls back to original executable providers. The combined ELF still has explicit original bindings for unused fatal paths and other auxiliary/delete functions; it is not an entirely source-only firmware.

Delete integration compiles sealed CMSIS delete source unchanged, executes real stock queue-copy/CMSIS/allocator peers, and redirects the stock event-unblock entry to real compiled native code with arguments/LR preserved. This is offline provider routing, not a patched firmware image or a fabricated return. Higher-priority receiver54 versus sender47 stops before port-yield; dynamic auxiliary is still allocated there. Equal/lower/no waiter paths can finish and free it. No context handover is modeled.

## Corrections and remaining boundary

[Yield successor](../audio-timer-yield-boundary-successor-2026-10-08/REPORT.md) corrects the passive-NVIC continuation in the earlier sealed daemon-order tests. [Actual watchdog callback](../audio-watchdog-callback-closure-2026-10-09/REPORT.md) additionally proves that the stock callback ignores its argument and publishes type6. A reused argument reaching this function is therefore not evidence that it is read; callback pointer/auxiliary ownership and physical scheduling remain separate.

Live task47/54 PC/frame state, ready/waiting/pending lists, queue occupancy, timer expiry/status/ID, allocator reuse and PendSV/tick delivery are still needed to establish the claimed runtime interleaving. A daemon already blocked resumes toward command drain; a direct due-entry fixture is a different continuation. No firmware patch safety or observed hardware fault is claimed.

Pinned queue generic-send/receive and broader scheduler/callback providers remain useful source leads; [current bounded lead ledger](source-lead-ledger.json) also distinguishes already closed tick/PCM2.1/I2S paths from available PCM0.7/2.0,touch and case/storage work. Search is not globally exhausted. No commits, production changes or device writes.
