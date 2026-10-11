# CASE scheduler/list provider pass

The fixed CASE image is `g2-2.2.6.10/firmware_box.bin`, SHA-256
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `case_remove_waiter` occupies `0x0800cba0..0x0800cbfe`, with three
literal words through `0x0800cc0c`. The retained original disassembly and
FreeRTOS list source agree on list item next/previous/container and list
count/index/sentinel offsets. The original reads a TCB owner from the head
event item, removes that item, and either moves its state item to the ready
list or moves its event item to the pending-ready list according to scheduler
suspension. It updates top ready priority and requests a yield only on the
observed priority comparison. A null owner disables IRQs and loops forever.

`waiter.c` defines that full bounded body and its two list operations from
source. It compiles for ARMv6-M Cortex-M0+ with warnings as errors.
`verify_waiter.py` executes stock and compiled source over 216 coherent
synthetic list/TCB states: suspended depth 0/1/2, task priority 0/1/3/4,
current priority 0/1/3, top ready priority seed 0/2/4, and yield seed 0/1.
Return value, scheduler state, all involved list windows, both TCBs, and
PRIMASK match exactly in all 216 cases. The null-owner path is separately
bounded for 100 instructions; both versions mask IRQs and remain nonreturning.
`waiter_results.json` records hashes and domain.

At round 13 the main CASE builder included `waiter.c`. Its deterministic archive
rebuild and whole-archive relocatable link pass with **24 objects, 44 provided
symbols, and 11 unresolved provider names**. The refreshed provider census
matches the linker: `case_remove_waiter` is defined once and
`case_resume_scheduler` remains unresolved. This does not close kernel task
lifetime or prove production scheduler state. The prior 12-name direct provider
census therefore advances by **one** bounded body, leaving **11**. The
remaining names include scheduler resume,
waiter unblock, disinherit, queue send, command handlers, UART callbacks,
DMA boundary and IRQ behavior. These are eleven contracts, not an hour
estimate; several contain larger state machines. `case_resume_scheduler`
next requires coherent pending-ready list, tick increment and next-unblock
providers, plus nested critical/yield state across its branches.

## Scheduler resume, round 14

`resume.c` source-defines original `0x0800cc0c..0x0800ccb4` and the lower
`case_reset_next_unblock` body at original `0x0800b260`. It uses the shared
source list helpers, source critical-section and PendSV-request providers,
and leaves `case_increment_tick` at original `0x0800ca78` as an explicit
lower import. The comparison linker binds that one import to the authenticated
stock Thumb entry; the production source archive does not carry that binding.

`verify_resume.py` passes **2,304** coherent stock/source comparisons for
both an isolated `-Og` build and the actual `-Os` objects from the main CASE
archive. Fixtures cover scheduler suspension 1/2, task counts 0..4 consistent
with live list members, pending-ready list sizes 0/1/2, pending ticks 0/1/2,
existing yield flag 0/1, task/current priorities, nested critical depth 0/1,
and an optional unrelated delayed task. The original and source match return
value, scheduler globals, critical depth, pending/delayed/ready lists, TCBs,
ICSR and PRIMASK. The original lower tick executes in both sides; stock
branch hooks record tick, next-unblock and yield paths. Zero suspension is
separately bounded: both versions disable IRQs and remain nonreturning after
100 instructions. This does not prove actual task lifetime or scheduling.

The deterministic main archive and whole-archive relocatable link pass with
**25 objects, 48 provided symbols, and 11 unresolved names**. The direct
12-name census now has **2 bounded bodies addressed here, 10 direct bodies
remaining**. The symbol count remains 11 because `case_resume_scheduler`
is replaced by the distinct `case_increment_tick` lower import. Tick wrap,
delayed-list wake and ready/yield effects need their own source closure before
whole-kernel composition. Full CASE executable/link and hardware remain open.

## Tick increment, round 15

`tick.c` source-defines stock `case_increment_tick` at
`0x0800ca78..0x0800cb38`. It handles suspended pending ticks, running tick
advance, wrap and delayed-list swap, due-task transfer to ready lists, event
item removal, next-unblock update, and return-yield conditions. It calls the
previously evidenced `case_reset_next_unblock` lower body. The fatal wrap
with a nonempty active delayed list uses explicit ARM `cpsid i` and a
nonreturning loop.

`verify_tick.py` passes **352** original/source cases with isolated `-Og`
objects and the actual archive `-Os` objects. Fixtures cover suspended ticks,
ordinary and not-yet-due delayed tasks, priority/yield branches, wrap,
overflow-list swap, event-linked tasks, and ready-list counts. Return value,
scheduler words, list and TCB windows, ICSR, and PRIMASK match. Invalid wrap
is separately bounded at 100 instructions; both versions mask IRQs and remain
nonreturning. Receipts: `tick_results.json`, `tick_archive_results.json`.
Synthetic state does not establish production task lifetime, tick cadence,
or interrupt behavior.

The deterministic archive rebuild and whole-archive relocatable link pass
with **26 objects, 49 provided symbols, and 10 unresolved names**. Archive
SHA-256: `f266c84065db02b4238ef912374fe1f51a13439b05f1c6518ddb6f3b3171f63a`.
This closes the lower tick import; the direct 12-name provider census remains
**2 bounded bodies complete, 10 direct bodies open**. The ten unresolved
archive symbols cover waiter unblock/disinherit, queue send, product commands
and transport, UART callbacks, and DMA/IRQ behavior. They are a symbol count,
not ten independent implementations or a time estimate. Full CASE startup,
linker composition, and integrated behavior proof remain open.

## Mutex disinherit, round 16

`disinherit.c` source-defines original `0x0800cb38..0x0800cb98` for the
current mutex holder. It returns zero for a null holder, decrements the
holder's mutex count, and when the last mutex is released restores base
priority, event item sort value, ready-list placement, and top-ready priority.
The wrong-holder and zero-held-count guards explicitly mask IRQs and remain
nonreturning. The caller must provide a live, coherently linked TCB.

`verify_disinherit.py` passes **576** original/source cases each for isolated
`-Og` and main archive `-Os` objects: null/current holder, effective and base
priorities, held counts 1..3, top-ready seeds, and event sort seeds. Return,
scheduler words, ready lists, TCB, and PRIMASK match. Both fatal guards have
100-instruction bounded comparisons. Receipts are `disinherit_results.json`
and `disinherit_archive_results.json`.

The deterministic archive and whole-archive relocatable link now pass with
**27 objects, 50 provided symbols, and 9 unresolved imports**. Archive
SHA-256: `759b4024e5ba2e71a4490d8630d7beefc02d87eab9d6ce7fe7fd4df361a80a95`.
Of the original 12-name direct census, **3 bounded bodies are complete and 9
remain**. The remaining archive names cover waiter unblock, product commands
and transport, UART callbacks, DMA boundary, and IRQ behavior. This is a
symbol-level estimate; full CASE image/link and hardware validation remain.

## Event waiter unblock, round 17

`unblock.c` source-defines original `0x0800c1cc..0x0800c228` for a linked
event item with a live owning TCB. It requires a suspended scheduler, stores
the event snapshot with the unblocked bit, removes event and delayed-state
items, inserts the task into its ready list, and updates top-ready priority
and pending yield when the task outranks the current task. Unsuspended and
null-owner inputs follow the original IRQ-masked nonreturning guards.

`verify_unblock.py` passes **576** coherent original/source cases with both
isolated `-Og` and main archive `-Os` objects. The matrix covers task/current
priorities, top-ready and yield seeds, suspend depth 1/2, and four event-bit
values. It compares scheduler, event, delayed and ready lists, TCB, and
PRIMASK; each fatal guard is separately bounded at 100 instructions.
Receipts are `unblock_results.json` and `unblock_archive_results.json`.

The deterministic archive rebuild and whole-archive relocatable link pass
with **28 objects, 51 provided symbols, and 8 unresolved imports**. Archive
SHA-256: `8ab3620ec354e5120967ed46812e8fb6974986aa8cd4ca9b4bcaf31ffad2e683`.
The original 12-name direct census is **4 bounded bodies complete, 8 open**.
The remaining imports are two UART callbacks, four product command/transport
handlers, and two UART DMA/IRQ contracts. This is a symbol-level work count;
CASE startup, absolute image link, integrated scheduling, and hardware
behavior remain unverified.
