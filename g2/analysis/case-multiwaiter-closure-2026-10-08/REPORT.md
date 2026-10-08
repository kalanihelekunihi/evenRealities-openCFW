# Multiwaiter ownership and priority behavior; bounded case lifetime trace

**3,456 fresh PASS original/reconstructed comparisons**, not reruns of prior384 waiter or1936 queue suites. Reuses sealed independent waiters.c and executes actual original task-unblock/list remove/ready insert/scheduler resume providers. No child result substitution. [Results](results.json), [reproduction receipt](reproduction-receipt.json), [ARM32 interfaces](../../components/case/event_waiter_interfaces/event_abi.h).

## Multiple waiter semantics

Two/three allocated blocked TCBs, a current TCB linked in its ready list, coherent event/delayed lists and per-priority ready lists0/1/2. Requests8/40/48, existing bits0/8, set bits8/40/48, wait-any/all, clear-on-exit on none/all/first/last, priority profiles equal0 or mixed0/1 or1/2, current priority0/1/2 and critical depth0/1.

Every satisfied waiter receives **the same pre-clear event snapshot**, even when an earlier waiter requests clearing those bits. Clear masks are accumulated over satisfied waiters and applied after traversal. Unsatisfied waiters remain linked to event/delayed lists. Matched event item container becomesNULL; matched state item container becomes the correct priority ready-list base. Callback order, all affected bytes, ready/list counts, ownership pointers and restored critical depth/mask compare. This establishes stable next-pointer traversal through actual unlink operations under coherent fixture state; not real simultaneous wait/IRQ execution.

A matched task with priority greater than current task sets yield pending; actual resume requests PendSV by writing10000000 toE000ED04. That write is checked with PRIMASK1. Equal/lower priority does not request PendSV here. **Exception delivery/context switching is not emulated.** No pending ticks, pending-ready tasks, timer expiry, deletion or runtime scheduler trace. A PendSV request is not proof that a task ran.

## Creator/global and lifetime findings

Static app initializer08006968 calls event-create0800a836 at08006a06 with attributes0800d35c (attribute table0800d26c+F0). Locked words are name0800d930, attribute bits0, cb_mem0, cb_size0. Thus selected wrapper uses dynamic constructor0800c48c, which requests32 bytes and initializes the allocation marker0. Result is stored at app base200000b8+38 = **200000f0**. This grounds the borrowed pointer's creator/heap classification without executing allocator or proving allocation success.

Exact global literal references identify command paths08000928/08000e1c, hall handler08003c2c, USB handler08003d24 and frame callback08006544. Candidate containing-base windows and hashes are in event-global-static-xrefs.json. Hall/USB decompilation posts flags2/1000, USB also200; these are static call-path leads, not new executed product behavior. Registered app consumer08006e1c reads flags using osEventFlagsGet, selectively clears them using osEventFlagsClear and acts on flag8 by dispatching frame parsing. A policy path08007214 also has Get/Clear calls. **This is polling evidence, not evidence that this particular event object has the synthetic blocked waiters used in these tests.** Waiter tests establish kernel capability only.

No actual stock event-delete/close binding or quiesce/drain-before-release path was established in the bounded registered-function/literal/caller review. Prior direct free-call screen found known timer/thread cleanup, not a bound event delete. The initializer returningNULL is a possible allocation-error boundary; its assignment itself shows no checked recovery, but no real heap exhaustion was exercised. No proof that deletion is absent globally, that object lives forever or that queue references are safe on shutdown.

## What remains

Owned inline queue bytes are proven separately; borrowed event handles and embedded waiter TCBs still require lifetime protection until their respective queue/list references end. Exact missing lifetime input is a **bound stock event close/delete/reset call path or runtime producer-stop/daemon-drain ordering trace**. Whole-system shutdown cannot be inferred from public delete semantics or this static caller search. No firmware patch/safety claim.

Actionable next source work includes actual Get/Clear polling wrappers and frame-consumer ordering, positive timer/delete paths, or additional kernel configuration/source comparison. This batch does not exhaust broader dependencies. All831 prior seals,110 audit inputs and4 checkpoints preserved. No index/commit/production/device changes.
