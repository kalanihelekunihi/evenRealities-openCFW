# Source-defined tick expiry in the native resume/radio path

The linked source target now executes actual tick bookkeeping, timeout expiry and delayed-list rollover in place of resume's tick-return fixture. Pending-ready drain, actual timeout release and deferred tick catch-up can now be exercised together. Task selection, physical context switching and runtime startup remain external.

## Why this provider

Tick expiry was the narrow missing provider directly called by the completed resume module. Its 338-byte stock body and upstream identity were already established, and a previous partial fixture exercised 168 one-due-task cases. We reuse those addresses/contracts rather than rediscovering them. The new deliverable is a compiled source provider plus multiple-due, rollover and linked-resume comparisons. Boot/memory/allocation and untouched drivers still matter, but they have broader unresolved contracts; this is the strongest bounded integration step available from current evidence. It does not imply this one function is the largest remaining whole-firmware gap.

The static packet in `original/` references the earlier due-task fixture `apollo-main-rtos-tick-original-due-task-fixture-12028/001` and tick-drain map `10726/002`, preserving their partial/not-accepted status and hashes. Those historical stock observations are not claimed as newly discovered code or reused as passing source comparisons.

## Authenticated behavior and source

Stock `xTaskIncrementTick` at 0x45504c has 338 bytes, SHA256 `438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050`. `tasks_tick.c` copies its pinned FreeRTOS V10.5.1 text and private reset helper unchanged, retaining the MIT notice. Configuration macros reproduce the observed preemption, time-slicing check and absence of a tick-hook call; complete original configuration headers are unavailable.

Authenticated globals include tick count 0x20074a34, suspended count 0x20074a58, pended ticks 0x20074a40, active/overflow delayed pointer cells 0x20074a24/28, signed overflow counter 0x20074a48, next-unblock 0x20074a50, ready-array 0x2006a49c, current TCB 0x20074a20, top-ready priority 0x20074a38 and yield-pending 0x20074a44. TCB accessed prefix offsets and 20-byte list ABI are reused; no full allocated TCB/kernel ABI is asserted.

| Condition | Clock/list effect | Switch result |
| --- | --- | --- |
| Scheduler suspended | Increment pended ticks with stock wrap behavior; leave clock/lists unchanged | Return false |
| Normal tick, before next deadline | Advance tick; leave blocked lists unchanged | True for existing yield-pending or equal-priority ready count >1 |
| Due tasks | Remove each due state item and linked event item; insert state into priority ready list | True if any released priority exceeds current, or time-slicing/yield condition applies |
| Clock wraps to zero | Require old active list empty; swap active/overflow pointers; increment overflow counter; refresh next deadline | Process newly active due tasks at tick zero |
| Native resume catch-up | Call this actual provider per deferred tick; clear deferred count afterward | Propagate true results to yield-pending and PendSV request |

Expiry does not consume a queue message or free an event-group object. It removes a timed-out task's intrusive event item when linked. Tick returns a switch-needed result; it does not itself set yield-pending merely because a higher-priority task expired. Equal-priority time slicing is based on current-priority ready-list count, independently of whether a timeout expired. Units remain ticks; neither frequency nor milliseconds are inferred.

Vector slot 15 at 0x43803c statically targets stock SysTick wrapper 0x442114. That wrapper masks, calls the tick helper and requests PendSV on a true return. Native resume is another actual caller. This target executes the helper under explicit synthetic exclusion or native resume; it does not execute a physical SysTick exception, vector startup or PendSV handler.

## Fresh comparisons and compiler boundary

Authoritative `comparison-verified.json`: PASS **271** stock/source cases, **2,404** distinct original instruction bytes across the linked path. Every executed instruction is checked against loaded bytes. Stack and R4–R11 preservation are checked at returning top-level calls. Independent expectations check tick/deferred/overflow counters, pointer swaps, every list edge/value/count/head/tail/index/owner/container, priority-ordered event fixtures, index-relative insertion, ready memberships, top priority, next deadline, switch returns, resume yield propagation and PendSV requests.

Cases include multiple same-deadline and staggered expiries, lower/equal/higher and mixed task priorities, optional event membership, removed-list indices and existing ready indices, future deadlines, suspended counter deferral/wrap, delayed-list rollover with due-at-zero/future tasks, expiry at 0xffffffff followed by rollover, overflow-counter wrap, actual suspend → ticks → resume, nested resume catch-up, and radio ISR → pending → resume with real tick expiry → daemon callback → WSF dispatch. Invalid nonempty active list on rollover stops at assert-provider entry before the stock fault store/loop.

Optimized simulator runs exposed skipped compiled helper loads and a deferred-count clearing divergence in Unicorn. Explicit Cortex-M4 selection did not resolve the optimized case. A pause/cache/restart experiment was discarded from the final verifier. The passing target uses unchanged C texts compiled at O0 for tick/resume/list/new-provider objects, with the same Thumb2 soft-float freestanding ABI and fwrapv; other prior objects retain their profile. Both stock/source invalidate executable translation caches only before synthetic top-level calls. No instruction bytes, registers or firmware algorithm are substituted. This profile establishes bounded semantic agreement, not correctness of the optimized simulator profile, intended production build configuration or byte equivalence; the emulator root cause is unresolved.

Failed logs and the discarded verifier experiment are retained under the ignored build `diagnostics/` directory. A separate O2 diagnostic ELF was reconstructed from unchanged source/flags and reproduces divergence (`optimized-replica.json`); it is accurately labeled a replica, not falsely described as a saved copy with an earlier authenticated ELF hash. No failed/diagnostic run contributes passing coverage. Intermediate comparison files remain separate; only `comparison-verified.json` is authoritative for this batch.

The result's `source_manifest` covers the new tick component only. `build-provenance.json` separately binds all linked source inputs, including the newly recompiled resume/list sources, Makefile, effective per-profile flags/compiler version, ELF, final comparison, build log, aggregate, static original evidence and review.

## Evidence accounting and limits

This batch adds **328/338** tick-body bytes to the disjoint foundation source-comparison ledger; the stock fault tail is excluded. Cumulative foundation evidence becomes **4,166 bytes** (touch 234; Apollo 3,932). This is new to that ledger, not a claim those stock bytes were previously unknown across the whole corpus. Shared prior providers count once; static-only SysTick wrapper bytes are excluded.

Affected foundation suite: **59 passing tests**. Aggregate: **41 modules; 215 executed method tests = 209 passing + 6 skipped methods; zero failures/errors**. One additional class/module setup skip is recorded separately, yielding seven skip records without treating setup as an executed method. The runner records each reason/category; bounded npm retries/timeouts retain the unchanged font tests' documented offline-skip behavior.

Synthetic inputs establish accessed task/list/global state, not a recovered full boot snapshot. Application handlers, EventGroup unordered unblock, scheduler-state/context/wait and WSF timer handling remain fixtures. Tick ISR/startup/frequency, ready-task selection, physical context switch, allocation/deletion/full scheduler lifecycle, borrowed EventGroup lifetime and hardware remain unverified. Actual task release is now modeled, but no task has necessarily run and no object is proven safe to destroy. No commits, firmware changes, flashing, deployment, complete source build or byte-identical bundle are claimed.
