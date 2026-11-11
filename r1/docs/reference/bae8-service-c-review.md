# R1 BAE8 service configuration in C

`r1/src/application/board/native_bae8_service.c` implements stock application
`0x529bc`, `r1_bae8_service_configuration` (350 code bytes). It stores the
configured callback, registers the 16-byte vendor UUID and primary service
UUID 1, then adds these characteristics through the pinned SDK provider:

| UUID | Properties | Service-relative output handles |
| --- | --- | --- |
| 0x10 | BC write without response | +14 |
| 0x11 | BC notification | +6 |
| 0x12 | EUS write without response | +30 |
| 0x13 | EUS notification | +22 |

All four parameter records use variable length, maximum 244, initial length 1,
and open read/write access. Notification CCCDs use open write access. Each
record is rebuilt from zero. UUID type and service handle are reloaded after
provider calls, preserving mutations. Failure returns immediately with the
full status word and retains partial callback, type and handle writes.

The source uses pinned SDK types, `characteristic_add`, and the SDK's
architectural SVC98/SVC168 wrappers. It introduces no handwritten assembly.
The base UUID is protocol data, matching the native bytes at `0x991a0`.

## Layout and validation

The initial loop and unrolled C probes changed the provider frame. The accepted
version uses explicit byte initialization for the UUID and a private C parameter
constructor. Its current Clang compilation preserves the stock 72-byte frame:
characteristic parameters are at caller SP minus 72, the base UUID at minus 40,
and the service UUID at minus 24. The private constructor clears and fills the
32-byte SDK structure using C; its internal frame is outside this contract.

In 1,424 paired stock/C executions, both SVC argument records and all four
32-byte characteristic parameter records match. Tests cover null service or
configuration, a configuration alias into the service callback slot, every
failure stage, full-word statuses, initial service patterns, both PRIMASK
states, and provider mutations of UUID type, handle, callback and configuration.
Providers write handles even on errors to verify partial-state preservation.
Bounded hooks compare service/configuration access order, widths and values.
Return status, state, restored SP/callee registers and interrupt masks match.

Five negative controls reject a wrong base UUID, continued processing after
failure, wrong maximum length, wrong first handle offset and larger frame.
REA reads of the root/literal window and base UUID agree with the locked image.

SVC98/SVC168 controller responses and the entire `characteristic_add` body are
modeled. Native private zero-fill is modeled as a pure local clear; C private
construction executes its actual loops. Private constructor frames, SVC
exception frames and return PC/LR differences, internal nonargument register
state, APSR and timing are excluded. SDK characteristic creation, the startup
caller, interrupt scheduling and physical BLE initialization remain unvalidated.
The verified frame is a property of this compilation, not arbitrary compilers.

## Build and remaining work

`build/sources-goal-r1-bae8-service-c/report.json` compiles all 595 units
(521 application, 74 bootloader). Both relocatable compositions pass without
failures or duplicate strong symbols. All previous 594 objects are unchanged.
The manifest adds one unit; imports remain 154 application and 34 bootloader,
with none added. This function was previously a frontier dependency, not an
import from the current source startup path. Its transport startup caller
at `0x4e66c` was pending at this stage; the subsequent
[startup review](bae8-startup-c-review.md) supplies it and exposes the remaining
event-route dependency. `make sources-check` passes with
399 R1 source files.

Qualification compiled the unit but selected no exact regions. The canonical
source plan is unchanged. A fresh hybrid application retains SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`
and totals of 4,269 source-built, 641,891 binary-pull-through and 248 resource
bytes. Complete C firmware and byte-identical source reconstruction remain
unproven; this result does not establish physical service registration.

The [receipt](bae8-service-c-review.json) records source/object identity, REA
provenance, replay, negative controls, qualification and audits. Reproducible
probes are under ignored `build/goal-r1-bae8-service-c/`.
