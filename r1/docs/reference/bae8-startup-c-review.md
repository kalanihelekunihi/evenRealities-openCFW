# R1 BAE8 transport startup in C

`r1/src/application/board/native_bae8_startup.c` implements stock application
`0x4e66c`, `r1_bae8_transport_provider_configuration` (120 code bytes). It
passes the event-route callback to the C service initializer and creates both
transport semaphores through `osSemaphoreNew(4,4,NULL)`. The semaphore array
and service retain their existing shared C owners.

On service failure the error provider is called; startup continues if it
returns. Both allocations occur. The first handle is stored before the second
allocation, then reloaded afterward. Failure depends on that fresh first slot
and the second returned handle. Log-mode query order, messages and severity
match stock, followed by error 4. Partial state is retained without cleanup.

## Frame and validation

A C11 `_Alignas(8)` declaration keeps the four-byte callback configuration at
caller SP minus 16 in the manifest's current Clang compilation. Every direct
provider entry retains the stock 16-byte frame. The unaligned probe changed
the escaping pointer and was not adopted. The source contains no inline
assembly. These frame properties require replay if compiler flags change.

The production object passes 2,240 paired stock/C cases covering service
statuses, null and full-word semaphore handles, initial slot values, basic
and varying full-word log modes, both PRIMASK states and provider mutations.
Bounded hooks compare service and semaphore access order, widths and values.
Arguments, logs, state, restored SP/callee registers and interrupt masks match.
Guards and the adjacent storage descriptor survive.

Another 584 paired cases execute the actual C startup caller and service
initializer together with their shared owners. All service failure stages
and semaphore allocation combinations are exercised. Nested UUID/characteristic
provider entries retain an 88-byte frame relative to startup's caller. The
installed callback matches the stock Thumb binding `0x5d5e1`. Five negative
controls reject a wrong configuration slot, initial count zero, aborting after
service failure, ignoring the first handle and skipping the second allocation.

Service initialization, returning error/log providers and semaphore allocation
are modeled in the larger replay. In the combined replay the service body
executes, while SVC98/SVC168 and the full `characteristic_add` body remain
modeled. Private constructor frames, SVC exception frames and return PC/LR,
internal nonargument registers, APSR, private spills and timing are excluded.
The callback address is verified metadata; its body is not executed. Real
controller initialization, complete SDK characteristic creation, live RTOS
semantics, higher boot callers and physical BLE remain unvalidated.

## Build and remaining dependency

`build/sources-goal-r1-bae8-startup-c/report.json` compiles all 596 units
(522 application, 74 bootloader). Both relocatable compositions pass without
failures or duplicate strong symbols. The other 595 objects are unchanged;
the manifest adds one unit. The previously hidden callback is now the explicit
import `r1_bae8_event_route` at `0x5d5e0`, with no accepted body or stub at
this startup-only stage. The subsequent [router review](bae8-route-c-review.md)
supplies a C behavior candidate, retaining its native/C frame counterexample.
Application imports rise from 154 to 155; bootloader imports remain 34.
`make sources-check` passes with 400 R1 source files.

Qualification compiled the unit but selected no exact regions. The canonical
source plan is unchanged. The fresh hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. Complete C firmware, byte-identical source reconstruction and physical
transport startup remain unproven.

REA's root/literal/string window agrees with the locked image. The
[receipt](bae8-startup-c-review.json) records current identity, provenance,
both replays, negative controls, qualification and audits. Reproducible probes
are under ignored `build/goal-r1-bae8-startup-c/`.
