# Scheduler pending-ready and delayed-task checks

Actual stock and selected C scheduler resume, tick, list and critical routines
agree in 216 seeded cases (432 executions), without function stubs. This extends
[the scheduler-lock integration](task-scheduler-locks-c-review.md) through
pending-ready draining and delayed-task wakeup branches.

[The receipt](scheduler-unblock-c-review.json) binds source/object hashes,
probe and results. Cases combine pending-ready versus delayed wakeup, blocked
priorities 0/5/55, zero/one/three pending ticks, tick starts zero/0xffffffff,
wakeup distances one/three, and three critical contexts. Full task, heap,
scheduler, ready/delayed and external event-list snapshots compare, along with
returns, critical observations, barriers and PendSV writes. Independent checks
verify removal from the event list, destination ready-list membership, tick
replay counts, final tick/pended counters, nesting and BASEPRI.

A deliberately late deadline comparison (`>` instead of `>=`) is rejected.

The fixture seeds one current and one blocked task with valid list links.
Placement is fixed only in the probe. Asynchronous ISR delivery, multiple
simultaneously blocked tasks, full exception state, private frames,
caller-clobbered words/flags and physical context switching remain unverified.
No firmware C, manifest or canonical source-plan bytes changed. The existing
573-unit report remains current for the checked sources, with 179 application
and 34 bootloader imports. This is bounded source-execution evidence, not byte
qualification, complete source linking or hardware proof. No G2 gate advances.
