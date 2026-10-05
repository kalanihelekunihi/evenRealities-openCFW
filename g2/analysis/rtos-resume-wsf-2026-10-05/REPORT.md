# Pending-ready drain and nested scheduler resume

The linked radio/WSF simulator now executes real source-defined suspend/resume instead of those fixtures. This closes the previously deferred transfer from pending-ready to ready lists. It does not supply physical task selection or context switching.

## Original code, callers and source

Stock `vTaskSuspendAll` at 0x454d7c is 12 bytes; `xTaskResumeAll` at 0x454dcc is 306 bytes. The static original packet authenticates seven bodies and records 11 direct callers apiece for suspend/resume, including the selected EventGroup path. It resolves suspended count 0x20074a58, task count 0x20074a30, pending-ready 0x20073d24, ready array 0x2006a49c, current TCB 0x20074a20, top ready priority 0x20074a38, yield-pending 0x20074a44 and pended ticks 0x20074a40. The prior accessed TCB offsets and 20-byte list ABI are reused; this is not a full allocated TCB/kernel ABI reconstruction.

`tasks_resume.c` retains unchanged MIT-licensed `vTaskSuspendAll`, `xTaskResumeAll` and private reset-helper texts from pinned FreeRTOS V10.5.1. The compatibility layer supplies recovered configuration/global macros. `yield_request.c` reconstructs stock 0x4420bc: write PendSVSET (0x10000000) to SCB ICSR, then DSB/ISB. It requests a switch; it does not execute a PendSV handler. The original helper's instructions were already represented in prior cumulative evidence.

## Proven bounded contract

| Stage/condition | State/ownership effect | Yield/tick behavior |
| --- | --- | --- |
| Suspend | Increment nested suspended count, no interrupt mask change | Counter overflow preserves stock wrap behavior |
| Inner resume | Decrement under task critical; leave lists unchanged | Deferred ticks/yield remain unchanged; return zero |
| Outermost resume, task count zero | Skip pending drain and tick replay | Pending items/tick count remain; return zero |
| Outermost resume with tasks | Remove pending event items; remove blocked state items; insert states into ready lists | Equal or higher priority sets yield-pending; recalculate next-unblock if anything moved |
| Deferred ticks | Copy pended count, call tick helper that many times, clear count | Any nonzero helper result sets yield-pending |
| Yield pending | Request PendSV while task critical is held | Return 1 under verified preemption build; flag is not cleared here |

List insertion is before the current index, preserving round-robin index semantics. Nested resume enters/exits the task critical provider even when it does not drain; outer critical exit clears BASEPRI to zero, while an existing task critical nesting depth leaves BASEPRI 0x30. Suspend itself does not create that critical section. Next-unblock values are ticks, not inferred milliseconds.

The actual `xTaskIncrementTick` at 0x45504c is statically authenticated. It checks suspension, accumulates deferred ticks when suspended, otherwise advances tick count and processes delayed tasks. Here its entry is intercepted with synthetic return values. Therefore the comparison proves replay count, deferred-count preservation/clear order and yield propagation, not actual tick advancement, expiry, overflow-list switching or time-slice selection.

## Fresh verification

`comparison-final.json`: PASS 267 stock/source cases, 2,106 unique original instruction bytes across the linked path. The independent graph model processes observed call entries against explicit initial conditions, independently checks every list edge/count/head/tail/index/owner/container/membership and insertion order, calculates ready priority/yield/next-unblock, checks deferred tick calls/clear, resume return values, PendSV-request counts and TCB guards. Cases include nested suspension 1/2/3, multiple pending tasks, existing ready/pending nodes with altered indices, priority below/equal/above current, deferred ticks 0/1/3 and mixed tick results, task-count-zero skip paths, existing critical nesting, suspension counter wrap, borrowed blocked-list alternatives, and radio ISR → pending → explicit resume → daemon callback → WSF dispatch. Invalid resume zero stops at assert-provider entry before the stock fault store/loop.

An initial build failed because a compatibility macro renamed an earlier non-const queue declaration; ordering the existing daemon declaration before that macro fixed the ABI collision without editing prior source. The first model execution failed from a Python local named `next` shadowing the builtin; renaming the local corrected the model. Neither failure produced counted coverage. Intermediate results and logs are retained; final verifier/result hashes are freshly bound. The ready batch's executable translation-cache invalidation policy is used identically on stock/source, with no firmware instruction substitution.

New disjoint evidence: 308 bytes (suspend 12/12; resume 296/306). Stock fault-tail instructions are excluded. Cumulative deduplicated evidence becomes 3,838 bytes (touch 234; Apollo 3,604). Static tick-helper bytes are excluded from execution totals. Compiler byte equality and complete firmware source coverage are separate and unproven.

Fresh affected suite: 56 tests pass. Full aggregate: 40 modules, 212 method tests run, 206 passing methods, zero failures/errors, six skipped methods, and one class/module setup skip. The seven total skip records include that setup skip, which is not an additional executed method: **212 = 206 + 6**, with the setup skip reported separately. Runner records both categories and each reason. Bounded npm retry/timeout settings preserve unchanged font tests' existing offline-skip policy.

## Practical effect and boundary

The source simulator now models the missing pending-to-ready transfer in the radio deferred-event path and distinguishes an inner resume from the outer drain. Equal-priority pending tasks can trigger a yield request even if ordered removal itself did not report a higher-priority wake. This helps app/CFW scheduling expectations; it does not make a borrowed object safe to delete.

EventGroup unordered unblock, scheduler-state/context/wait/timer/app callbacks, tick behavior, physical interrupts and context switching remain explicit external/synthetic boundaries. Synthetic accessed TCB/list graphs are coherent, but selected counter/task-count probes are not complete boot snapshots. Queued command bytes remain queue/receiver-owned; the EventGroup pointer remains borrowed through callback completion. No lifecycle/drain-to-destruction, cancellation or whole-system liveness guarantee is supplied. No firmware patch, flashing, deployment, commit or source-built byte-identical bundle is claimed.

Independent review (`review/report.md`, `review/review.json`) found no blocker and rechecked final firmware/ELF/source hashes. Build uses the existing Cortex-M4-compatible Thumb2 subset for Unicorn, while the locked target remains Cortex-M55; no compiled byte-match claim is made. Protected firmware/manifest/workflow/tool identities remain unchanged. `build-provenance.json` binds current inputs, compiler flags, ELF, final comparison, aggregate, original evidence and review.
