# R1 BAE8 raw BLE observer in C

`r1/src/application/board/native_bae8_observer.c` implements the product
observer at stock application `0x52b20`. Its code ends at `0x52b96` (118
bytes); the semaphore-array literal is at `0x52b98`. REA's 124-byte read agrees
with the locked application. The normal manifest contains one implementation.

The actual priority-2 table continues to supply the shared service context.
Null event or context returns immediately. Other event handling is:

| Event ID | Stock behavior preserved |
| --- | --- |
| 16 | Tail-dispatch service and event to the connection handler |
| 17 | Select the link semaphore and drain it; if absent, drain both global semaphore slots in order |
| 80 | Tail-dispatch service and event to the write handler |
| 87 | Read the count's low byte before selecting the link; return that many credits to the selected semaphore or both global slots |

Each fallback reads the second global semaphore after the first flush returns.
Neither the second semaphore nor the event count is incorrectly cached across
the boundary that precedes its stock read. The final flush and both event
delegates are tail calls. This C unit contains no inline assembly.

## Validation

The actual production object, priority-2 table and shared service owner were
linked for 3,968 paired stock/C observer cases. Bounded memory hooks compare
event and semaphore access order, widths and values. Cases cover all four
handled IDs, null inputs, zero/nonzero selectors, zero semaphore slots, high
count bytes, both PRIMASK states, and mutations of the event and semaphore
array during modeled calls. Non-tail provider entries retain a 16-byte
observer frame. Tail entries restore caller SP, LR and every callee-saved
register. Every other 16-bit event ID (65,532 per implementation) also passes
an exhaustive return check.

A further 5,184 paired credit sequences execute the actual C selector,
drain and bounded-flush implementations and their semaphore-array owner,
against the corresponding stock code. Glass/phone getters and CMSIS semaphore
APIs are modeled. Cases include unknown connections, null/aliased semaphore
slots, initial counts below/at/above four, low-byte count boundaries and a
second-slot mutation during release. External call arguments, results, queue
counts, event data and semaphore slots match. CMSIS provider depths match in
this fixture; getter depths are 32 native versus 24 C. These deeper frames
are recorded rather than equated.

Five negative controls reject a widened count, ignored null context, omitted
second drain, omitted second credit return and a retained final-call frame.
Private spills, nonargument caller-clobbered values, live non-tail callee
registers, APSR and timing are excluded. No connect/write handler bodies,
physical BLE delivery, interrupt scheduling or live RTOS semaphores were
validated by these replays.

## Build and remaining dependencies

`build/sources-goal-r1-bae8-observer-c/report.json` compiles all 592 units
(518 application, 74 bootloader); both relocatable compositions pass without
failures or duplicate strong symbols. The previous 591 objects are unchanged.
`make sources-check` passes with 396 R1 source files.

The raw-observer import is resolved, while its previously hidden connection
and write callees are now explicit imports:

- `r1_bae8_connection_event_plan_build` at `0x7ccb4`;
- `r1_bae8_write_event_plan_build` at `0x7cf4c`.

Application imports therefore rise from 155 to 156; bootloader imports remain
34. At this observer-only stage these handlers are dependencies, not stubs or
accepted implementations. The subsequent [write review](bae8-write-c-review.md)
supplies the write adapter. The later [connection review](bae8-connect-c-review.md)
supplies the other direct handler dependency.
The write-handler frontier retains its unresolved status and Nordic skeleton
attribution while gaining the concrete import name.

Qualification compiled the unit and selected no exact region. The canonical
source plan is unchanged. A fresh hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. Full C source completeness, byte-identical source reconstruction and
physical hardware support remain unproven.

The [receipt](bae8-observer-c-review.json) records current object identity,
REA provenance, both replays, negative controls, qualification and build
audits. Reproducible probes are under ignored
`build/goal-r1-bae8-observer-c/`.
