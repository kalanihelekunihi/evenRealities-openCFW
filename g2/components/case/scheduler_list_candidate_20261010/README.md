# CASE waiter removal candidate

`waiter.c` source-defines original `case_remove_waiter` at `0x0800cba0`,
including its list removal/insertion operations. It uses the authenticated
20-byte FreeRTOS list and TCB item/priority offsets, fixed scheduler globals,
and a nonreturning null-owner fatal path. The caller must provide a nonempty,
coherently linked event list and live TCB; these are kernel ownership
requirements. Bounded comparisons and archive-link evidence are in
`g2/analysis/case-scheduler-list-candidate-20261010`.

`resume.c` source-defines original `case_resume_scheduler` at `0x0800cc0c`
and the lower next-unblock recalculation body. It imports
`case_increment_tick` as a distinct, unresolved kernel contract. The source
archive includes both units, but still needs a source-owned tick provider
before a complete kernel link.

`tick.c` now source-defines that lower provider from original
`0x0800ca78..0x0800cb38`. The isolated and archive-compiled objects each
pass 352 coherent original/source comparisons, including delayed wake and
wraparound; the fatal wrap is checked as a bounded nonreturning path. The
archive no longer imports `case_increment_tick`. These fixtures do not prove
production task ownership or tick interrupt cadence.

`disinherit.c` source-defines original mutex priority disinherit at
`0x0800cb38`. It passes 576 coherent original/source cases in isolated and
archive builds; wrong-holder and zero-held-count guards are bounded fatal
checks. The caller owns the mutex and live TCB/list state.

`unblock.c` source-defines original event waiter unblock at `0x0800c1cc`.
Both builds pass 576 coherent stock/source states; unsuspended and null-owner
guards are bounded fatal checks. The caller supplies a linked event item and
live owning TCB.
