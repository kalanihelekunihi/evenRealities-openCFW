# CASE source candidate, 2026-10-10 round 2

Run `python3 g2/components/case/source_candidate_20261010/build.py` from the repository root (or invoke its absolute path from another directory). The script compiles eleven previously bounded CASE reconstruction modules plus twelve original-evidenced provider files for ARM Cortex-M0+ Thumb, soft float, and creates an archive under the ignored `build/` directory. It writes exact source hashes, commands, compiler version, archive hash, and unresolved symbols to `../../../analysis/case-source-candidate-round2-20261010/receipt.json`. The complete symbol listing is `nm.txt` there.

This is a source-only composition artifact. The builder performs a whole-archive relocatable link to catch duplicate strong definitions and records its hash. It has no reset vector, image linker script, complete HAL/RTOS provider set, firmware image, or hardware execution claim. Each member retains its earlier limited input contract; archive creation does not expand them. The earlier `uart_error_offline` member is deliberately excluded in favor of the corrected `uart_error_atomic_offline` version.

Round 3 added the clear wrapper and three explicit kernel imports; see [round 3 audit](../../../analysis/case-source-candidate-round2-20261010/ROUND3.md). The current archive has twenty-five objects and 11 unresolved provider names after later rounds.

Round 4 adds two register-control wrappers and their shared MMIO leaf, from original CASE addresses 0x08006b80, 0x08006b98 and 0x08004e9e. The separate `case-control-source-candidate-20261010` verifier checks 24 original/source MMIO scenarios. Peripheral electrical behavior and callers beyond these bounded entries are unverified.

Round 5 adds the 24-byte acknowledgement sender wrapper. Its separate source/original comparison covers 260 command values, with the actual transport kept as an explicit child boundary. See `g2/analysis/case-ack-source-candidate-20261010/REPORT.md`.

Round 6 adds two interrupt-mask helpers whose compiled Cortex-M0+ code sections match all 14 authenticated original bytes. See `g2/analysis/case-mask-source-candidate-20261010/REPORT.md`.

Round 6 also adds the bounded CASE scheduler-state getter, with nine original/source execution comparisons. See `g2/analysis/case-scheduler-state-20261010/REPORT.md`.

Round 6 also adds the PendSV request provider. Its bounded six-case original/source register comparison includes the original R0 value and does not assert physical task switching. See `g2/analysis/case-yield-request-20261010/REPORT.md`.

Round 7 adds the CASE task critical-section helpers. Fourteen returning original/source nest and mask comparisons pass; the invalid zero-nesting exit is nonreturning and unqualified. See `g2/analysis/case-critical-source-candidate-20261010/REPORT.md`.

Round 7 also adds the scheduler-suspend counter, ten original/source wrap/PRIMASK cases. See `g2/analysis/case-suspend-scheduler-20261010/REPORT.md`.

Round 8 adds the event-group ISR bits getter, verified with the actual source-defined CASE mask helpers in ten original/source comparisons. See `g2/analysis/case-event-get-isr-20261010/REPORT.md`.

Round 9 adds the ISR deferred-clear wrapper. Its 24 original/source call-contract comparisons pass; two lower timer/callback providers are now explicit unresolved names. See `g2/analysis/case-event-clear-isr-20261010/REPORT.md`.

Round 9 also adds the eight-byte deferred clear callback. Twenty-four original/source child-call comparisons pass; task-context clear remains a provider boundary. See `g2/analysis/case-event-clear-callback-20261010/REPORT.md`.

Round 10 adds the task-context event-clear body. Its 72 valid original/source state comparisons pass with the source-owned critical helpers; four invalid cases validate only the nonreturning prefix. See `g2/analysis/case-event-clear-task-20261010/REPORT.md`.

Round 11 compiles the previously verified event-set waiter body under its stock export name without changing that source. This closes one archive symbol while leaving its lower scheduler/list providers explicit. See `g2/analysis/case-event-set-export-20261010/REPORT.md`.

Round 12 compiles the previously verified deferred timer-command producer under its stock export name without changing that source. See `g2/analysis/case-timer-pend-export-20261010/REPORT.md`.

Round 13 adds the source-defined CASE waiter-removal/list body at
`0x0800cba0`. Its separate verifier passes 216 coherent original/source
states and a bounded nonreturning null-owner path. The archive rebuild has
44 provided symbols and 11 unresolved providers; see
`g2/analysis/case-scheduler-list-candidate-20261010/REPORT.md`.

Round 14 adds scheduler resume and source-owned next-unblock recalculation.
Both isolated and archive-compiled source pass 2,304 coherent original/source
state comparisons; zero-suspension fatal behavior has a bounded assertion.
The stock tick increment remains an explicit unresolved lower provider.
The archive has 25 objects, 48 provided symbols, and 11 unresolved names;
see `g2/analysis/case-scheduler-list-candidate-20261010/REPORT.md`.

Round 15 adds source-defined tick increment. Both isolated and archive-compiled
objects pass 352 original/source state cases, including delayed-list wake and
tick wrap; the fatal wrap is bounded separately. The current deterministic
archive has **26 objects, 49 provided symbols, and 10 unresolved names**.
The original 12-name direct provider census remains 2 bounded bodies complete
and 10 open because tick was a lower import. See the scheduler/list report.

Round 16 adds source-defined mutex priority disinherit. Both isolated and
archive-compiled objects pass 576 coherent original/source comparisons, with
two fatal guards checked as bounded nonreturning paths. The current archive
has **27 objects, 50 provided symbols, and 9 unresolved imports**; the direct
12-name census is **3 complete, 9 open**. Synthetic TCB state does not prove
live mutex ownership.

Round 17 adds source-defined event waiter unblock. Isolated and archive
objects each pass 576 coherent original/source comparisons; unsuspended and
null-owner fatal guards have bounded assertions. The archive has **28 objects,
51 provided symbols, and 8 unresolved imports**. The direct 12-name census
is **4 complete, 8 open**. Synthetic list state does not establish live task
ownership or physical scheduling.

Round 18 adds source-defined framed `case_send` with explicit lower UART
write and diagnostic logger imports. The parent body passes 28 original/source
argument and byte-stream comparisons in isolated and archive builds. The
archive has **29 objects, 52 provided symbols, and 10 unresolved imports**;
the direct 12-name tally is **5 complete, 7 open**. Three new lower imports
explain the symbol-count increase. UART state and physical delivery remain
unverified; see `g2/analysis/case-send-candidate-20261010/REPORT.md`.

Round 19 adds the lower hex-dump logger body at `0x080067c8`. Isolated and
archive objects each pass 42 original/source call-contract cases, including
the logger-disable flag changing between child calls. The archive now has
**30 objects, 53 provided symbols, and 9 unresolved imports**. The direct
12-name tally remains **5 complete, 7 open**; of the three lower imports
exposed by send, one is complete and two remain. See
`g2/analysis/case-hex-log-candidate-20261010/REPORT.md`.

Round 20 adds the ARM variadic diagnostic wrapper and one-byte output
callback. Both builds pass 27 original/source comparisons at the formatter
and UART writer boundaries. The archive has **31 objects, 55 provided
symbols, and 9 unresolved imports**. Direct providers remain **5 complete,
7 open**; two lower contracts remain: formatter and timed UART writer. See
`g2/analysis/case-log-wrapper-candidate-20261010/REPORT.md`.

Round 21 adds the timed UART writer and its separate HAL tick getter.
Writer comparisons pass 720 cases in isolated and archive builds; a further
720 archive cases execute source tick alongside source writer. The tick
getter alone passes seven original/source values. The archive has **33
objects, 57 provided symbols, and 9 unresolved imports**. Direct bodies
remain **5 complete, 7 open**; lower formatter and UART flag wait remain.
The wait child, peripheral timing and hardware delivery are unverified;
see `g2/analysis/case-uart-write-candidate-20261010/REPORT.md`.

Round 22 adds source-defined UART flag wait and timeout cleanup. Isolated and
archive objects each pass 5,040 original/source synthetic HAL cases. Source
writer, tick and wait also compose for 16 ready-ISR stock/source cases with
no child hooks. The archive has **34 objects, 58 provided symbols, and 8
unresolved imports**: seven direct and one lower formatter. Physical UART
timing and delivery remain unverified; see
`g2/analysis/case-uart-wait-candidate-20261010/REPORT.md`.

Round 23 adds source-defined blocking UART receive (`case_bulk_receive`).
Both builds pass 1,440 original/source HAL-state cases, and source read,
tick and wait compose for 32 ready-ISR cases without child hooks. The archive
has **35 objects, 59 provided symbols, and 7 unresolved imports**. The
direct original 12-name tally is **6 complete, 6 open**; formatter is the
one additional lower import. Incoming traffic, buffer lifetime and physical
UART behavior remain unverified; see
`g2/analysis/case-uart-read-candidate-20261010/REPORT.md`.

Round 24 binds the stock-selected TOIDLE receive-event callback to the exact
`0x08005e6a` `bx lr` body. Isolated and archive builds each pass 32
original/source register, RAM and PRIMASK cases. The archive has **36
objects, 60 provided symbols, and 6 unresolved imports**. Direct providers
are **7 complete, 5 open**; the lower formatter remains. The separate RX
completion parser still needs complete suffix validation; see
`g2/analysis/case-uart-event-callback-candidate-20261010/REPORT.md`.

Round 25 binds standard RX completion to the source frame parser and checks
the parser suffix with source bulk read, tick, wait and rearm providers
executing. Isolated and archive objects each pass 4,192 coherent
original/source cases with event posting as an explicit child boundary.
The archive has **37 objects, 61 provided symbols, and 5 unresolved
imports**. Direct providers are **8 complete, 4 open**; formatter remains
the one lower import. Malformed requests beyond frame storage, event-group
effects and physical UART remain unverified; see
`g2/analysis/case-uart-rx-complete-candidate-20261010/REPORT.md`.

The subsequent command-control audit decodes all 16 entries of the legacy
handler's Thumb-1 byte-offset table, resolving ten distinct targets; see
`g2/analysis/case-command-switch-frontier-20261010/REPORT.md`. This closes
target enumeration only. Command child effects and complete binary routing
still need coherent whole-entry comparisons, so the archive and direct/lower
counts remain **37 objects, 61 symbols, four direct and one lower unresolved**.

The lower formatter frontier is inventoried in
`g2/analysis/case-vformat-frontier-20261010/REPORT.md`. Stock `0x08009210`
parses flags, width, precision, length modifiers and integer/string/character
conversions, including `%n` writes. The 27-case wrapper proof stops at this
entry. A source subset for selected literals would not resolve the full
`case_vformat` import; the archive and counts remain unchanged.

The complete stock UART IRQ branch inventory is in
`g2/analysis/case-uart-full-irq-frontier-20261010/REPORT.md`. The two
remaining UART direct imports are candidate split names within one stock
handler. The retained STM32G0 HAL source explains DMA, TOIDLE, wakeup and TX
paths, but these paths lack a coherent whole-entry original/source comparator.
No full handler is integrated; the counts above remain unchanged.
An isolated non-DMA TOIDLE branch candidate passes 256 public-entry
original/source fixtures with complete handle/MMIO and atomic-mask comparison;
see `g2/analysis/case-uart-toidle-branch-20261010/REPORT.md`. Error-triggered
DMA abort and TX paths are still outside that bounded source; archive counts remain
unchanged.
The companion isolated TOIDLE/DMA branch passes 1,280 more public-entry
original/source fixtures with a shared compiled DMA-abort fixture provider.
Stock circular full-count behavior differs from the retained HAL source;
the corrected stock branch and remaining error/TX/FIFO frontier are recorded
in the same analysis report. Neither selected branch resolves an IRQ import.
The selected ORE/DMAR error abort branch adds 64 public-entry comparisons,
including installed callback identity and both immediate abort outcomes. It
also remains isolated; delayed/null DMA, wakeup and TX/FIFO branches keep
the full handler open.
An expanded all-enabled error matrix now passes 2,976 public-entry
comparisons for every nonempty PE/FE/NE/ORE/RTO mask, optional RX callback
mutation of `ErrorCode`, and both DMA abort outcomes. Selective interrupt
enables, live-register mutation, null/delayed DMA and wakeup/TX/FIFO paths
remain. The full handler is still outside the archive.

A subsequent isolated 7,168-case public-entry matrix passes selective
CR1/CR3 enables, live CR3.DMAR mutation by the RX callback, and mixed
error/IDLE/TXE flags within an initial-DMAR, nonnull-DMA domain. Prior
comparators still pass. Null/delayed DMA, wakeup, TX-ready, transmit-complete,
FIFO callbacks and precedence outside the selected error gate remain. The
full IRQ handler is still outside the 37-object archive; direct coverage is
8/12 and the five unresolved imports are unchanged.

An isolated 64-case null-DMA/deferred-callback comparison now passes as well:
the stock and source public IRQ entries are compared before the installed
abort callback is invoked later in the same emulator. This verifies callback
state changes under the fixture, not DMA hardware timing. Five IRQ branch
areas remain (wakeup, TX-ready, TX-complete, FIFO and precedence outside the
selected error gate). Archive counts and direct coverage remain unchanged.

A further isolated 40-case public-entry comparison passes WUF/WUFIE wakeup
gating, ICR.WUCF writes and the fixed-image weak callback in a quiet IRQ
continuation. TX-ready, TX-complete, FIFO and mixed precedence remain; the
full handler is still outside the archive.

The isolated TX-ready branch now passes 48 public-entry stock/source fixtures
with a shared compiled `TxISR` callback and null-pointer cases. Its callback
ABI and handle mutation match in this bounded domain. TX-complete, FIFO and
mixed precedence remain before a full-handler source claim; archive counts
are unchanged.

The isolated TX-complete finalization passes 48 public-entry comparisons,
including an atomic TCIE clear and a shared compiled lower completion provider.
The stock lower provider body is not source-owned by this fixture. FIFO
callbacks and mixed precedence remain; archive counts are unchanged.

The isolated FIFO continuation passes 40 public-entry comparisons for
TXFE/RXFF enable gating and simultaneous priority. Mixed precedence across
the earlier IRQ branches remains. No partial IRQ candidate is in the archive.

The isolated mixed-family analysis now passes 2,048 public-entry tail
precedence/callback-mutation cases and 896 enabled-error cases with later
flags set. A coherent full handler still needs no-error RX callback mutation,
disabled-error fall-through and TOIDLE mixed-family comparisons in one
compiled source body. The two synthetic IRQ imports remain unresolved.

The isolated RX-ready/disabled-error fall-through composition now passes
1,024 public-entry comparisons, including RX callback mutation of live
registers and its handle pointer. Simultaneous TOIDLE/later-family flags and
one unified compiled full-entry body remain. The archive is unchanged.

The isolated TOIDLE mixed-flag comparators pass 288 DMA and 72 no-DMA cases.
A unified compiled public IRQ entry passes 1,264 combined original/source
fixtures across the evidenced error, RX, IDLE and tail domains. It is not in
this archive: the two synthetic IRQ continuation imports still lack a proven
call-site ABI mapping to the stock's single public entry, and lower DMA/TX
completion semantics remain explicit fixture boundaries. Direct coverage
remains 8/12.

The two synthetic IRQ imports are now source-defined as distinct continuations
of `case_uart_error_irq`: `case_uart_other_irq` handles the later RX/IDLE/tail
families, and `case_uart_dma_boundary` starts after `case_uart_end_rx` without
replaying its effects. The archive-compiled prefix and continuation sources
pass 1,264 stock public-entry comparisons; the independent unified-entry
candidate also passes 1,264. Deterministic whole-archive linking gives **41
objects, 67 provided symbols and six unresolved imports**. Direct CASE
coverage is **10/12**. Remaining imports are two command handlers and four
lower providers (`case_dma_abort`, `case_dma_abort_it`,
`case_tx_complete_provider`, `case_vformat`). The lower DMA/TX completion
bodies and hardware timing are outside the IRQ fixture proof.

Both lower DMA abort imports are now source-defined from the complete fixed
stock bodies. The archive-compiled provider passes 194 sync/IT original/source
fixtures, and the whole UART IRQ comparison passes 1,264 cases with native
stock abort bodies on the original side and source aborts on the candidate
side. Busy `HAL_DMA_Abort_IT` invokes its installed callback before returning
in this image. The deterministic archive now has **42 objects, 69 provided
symbols and four unresolved imports**: two direct command handlers and lower
`case_tx_complete_provider` and `case_vformat`. Direct CASE coverage remains
10/12. See `g2/analysis/case-dma-abort-20261010/REPORT.md`.

The lower TX-completion provider is now source-owned as the stock's exact
two-byte `bx lr` no-op. The 1,264-case whole-IRQ comparator now runs native
stock and source TX completion along with native/source DMA abort bodies.
The deterministic archive has **43 objects, 70 provided symbols and three
unresolved imports** (`case_legacy_command`, `case_binary_command`,
`case_vformat`). Direct CASE coverage remains 10/12; see
`g2/analysis/case-tx-complete-provider-20261010/REPORT.md`.

The two remaining direct command handlers cannot be narrowed to the selected
source subsets by the frame dispatcher: valid outer frames pass arbitrary
payload opcodes. The legacy 16-entry table is decoded, but high-opcode cases
and lower child effects remain; the binary handler also calls legacy for two
commands. No partial command provider was added. The finite branch/child
frontier and current three-import archive status are recorded in
`g2/analysis/case-command-integration-frontier-20261010/REPORT.md`.
