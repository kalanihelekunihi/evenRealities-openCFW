# Bootloader thread creation and scheduler bootstrap

Independent C reconstruction from locked product bootloader SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`,
loaded at `0x410000`. No SDK binary or vendor source copied into these modules.

## Recovered call chain

`43297c → scatter records → 41b862 → published callback42e39d →
416058 → 4160fe → 417c7c → 417d94 → 41b46e → 417e58 →
4160b0 → 418148 → idle417c7c`.

- `thread_creation.c` / `4160fe`: attribute validation and static/dynamic routing.
  Defaults: priority24, stack256 words, unnamed. Static path needs CB pointer,
  CB size≥112, stack pointer and nonzero stack bytes. Dynamic path needs all
  CB pointer/CB size/stack pointer zero. Other mixtures return zero. Stack bytes
  are shifted right2; dynamic word count additionally truncates to uint16.
  Attribute bit0 disallows creation. Attribute priority0 selects default24.
- `kernel_static.c` / `417c7c,417d94,41b46e`: clear112-byte CB, mark byte6d=2,
  fill stack with A5, truncate name to31 characters+NUL, build initial18-word
  frame, register. Outer wrapper permits priority 56; initializer rejects≥56
  through mask-interrupts + observed invalid store0@FFFFFFFF. Manager48 and
  DFU46 avoid that path. This is observed behavior, not a recommended API.
- `thread_register.c` / `417e58`: task count/current selection, creation serial,
  maximum ready priority, circular ready-list insertion, and PendSV request
  when running and new priority exceeds current. Equal priority can replace
  current only before running. Lists are56 rows×20 bytes at20024870.
- `kernel_runtime.c`: guard41602a reads IPSR then runtime state; before kernel
  running, mode1 permits masked thread context, while other modes reject
  PRIMASK/BASEPRI. Critical enter/exit41b3e4/41b3fc update200004c4 and BASEPRI.
  Mask helper41b2f8 sets BASEPRI30; it is not a generic panic implementation.
  Ready-list init418a44/41b53c initializes56 ready lists plus5 additional lists.
  Reschedule41b3d0 writes10000000 to ICSR; exception delivery is not modeled.
- `lifecycle.c` / `416058,416088,4160b0`: wrapper state200270d4 goes0→1→2;
  forbidden context returns-6, invalid state returns-1. Lower scheduler-start
  return is ignored. Runtime state maps wrapper results0/1/2/3; these labels
  are standard-compatible, not a verified specific CMSIS release identity.
- `scheduler_bootstrap.c` / `418148,41b5d0`: idle CB20026970, stack200250d0,
  256words, priority0, entry4189ad, name43412c. Calls timer startup419240,
  then sets next-unblock20027164=FFFFFFFF, running20027150=1, tick20027148=0,
  and calls port startup41b4f6. Return loads200004c8, ignored by wrapper.

The initial frame stores xPSR01000000, entry, task-return41b391, patterned
register values, argument, EXC_RETURNFFFFFFFD, and stack base. It does not
establish correct hardware MPU/FPU/security context. Address41b391 remains
an external return-path reference in this bounded reconstruction.

Stock expanded initialization data sets critical nesting200004c4=AAAAAAAA.
Before actual port start resets it, critical enter+exit preserves this sentinel
and leaves BASEPRI30. The integrated comparison checks this actual stock state;
assuming a zero initial nesting value was incorrect.

## Validation and limits

Build/test targets in Makefile use separate Cortex-M4 compatibility ELFs for
Unicorn, and Cortex-M55 source compilation. Source completeness, stock IAR
build flags/layout, byte identity and hardware bootability are separate and
unproven. Differential counts overlap and must not be summed.

- Wrapper:324 cases/200 original bytes, guard/kernel allocation synthetic.
- Static creator+initializer+frame:36 cases/552 bytes; registration synthetic;
  full CB and stack compared for priorities1/24/48/55, stack128/257/4096 words,
  short/empty/long names.
- Registration:32 cases/730 bytes with critical/list/reschedule providers.
- Runtime:32 cases/1022 bytes with actual guard, list initialization, BASEPRI
  critical nesting and PendSV request; no interrupt delivery.
- Lifecycle:216 cases/224 bytes using synthetic IPSR/PRIMASK/BASEPRI initial
  values; actual guard/runtime query executes; lower scheduler-start synthetic.
- Bootstrap:6 cases/894 bytes, actual idle creation/registration, timer status
  fixtures0/1/2 and port return boundary. Fatal timer statusFFFFFFFF untested.
- Startup/runtime integrated:2 cases/1288 bytes; actual published callback,
  manager CB/stack/ready arrays/globals; setup/start wrappers synthetic in that
  intermediate profile. Latest bootstrap-integrated profile extends that chain.

Original fill helper41560c is intercepted as a byte-fill oracle; compiled
source loops execute. Dynamic kernel allocation417d16, timer service419240,
port startup41b4f6 and actual SVC/PendSV task transfer remain next recovery
work. Port timer configuration uses MMIO/HAL, not demonstrated physical time.
Three compressed startup spans totaling695 bytes remain authenticated fixtures.
No firmware patch, flash, staging, commit, license authentication or shared
workflow-state change is part of this work.

## Continued recovery and strongest current profiles

The current startup-port integration executes from43297c through scatter/main,
actual manager creation, lifecycle start, static idle/timer creation, static
50×16-byte timer command queue, ready-list registration and port transfer:
**2 cases/1958 original bytes**, stopping at SVC2. See
`g2/build/bootloader-completion/thread-port-startup-compatible/comparison-first.json`.
Timer hardware configure41b6fa remains synthetic. The first vector SP word4B
plus695B compressed startup data are authenticated fixtures. No exception
handler/task unstacking is inferred from this profile.

- `timer_service.c`: timer task entry419445, CB200269e0, stack200254d0/256 words,
  priority54 and name43413c. Queue CB20026da0, buffer20025cd0,50×16B. Fresh
  queue constructor/reset is specialized to startup; reuse/wakeup paths remain
  outside this helper. Standalone startup4 cases/1280 bytes.
- `thread_select.c`: selector418570/history20026500,64×8B, outgoing/incoming
  serial words; pending selection while suspended, highest ready priority,
  circular cursor/sentinel skip.24 cases/180 bytes, intact A5 stack guards.
- `port_start.c`/`first_task_transfer.S`: priority ORs atE000ED20, critical
  nesting reset, VTOR→MSP, CPSIE I/F, SVC2. Stops before exception dispatch;
  standalone1 case/1328 bytes.
- `exception_entry.S`: independent M55 assembly for SVC selection/dispatch,
  first restore, PendSV and FPU access/FPCCR writes. First restore2 cases/36
  original bytes verifies PSPLIM/CONTROL/PSP/BASEPRI using M33-compatible
  Unicorn, stopping before BX EXC_RETURN. Non-FP PendSV2 cases/236 bytes
  executes save→actual selector→restore with coherent synthetic task frames.
  FPU extended context and real exception unstacking/entry remain unverified.
- `kernel_dynamic.c`: stack first,112B CB second; second failure frees stack,
  first failure allocates no CB.18 cases/962 bytes with heap providers cover
  both failures, dynamic word-count truncation, name-null/name31B truncation.
- `rtos_heap.c`: separate81,920B RTOS heap at2000055c, aligned20000560,
  end20014550, initial free81904. Header8B, allocated flag80000000, strictly
  >16B split threshold and sorted coalescing.159 operations/496 bytes compare
  full arena after every operation. Suspension/resume synthetic in this
  standalone profile. Stock malloc-failed hook41b5f6 logs and loops; test stops
  at that boundary. Creator failure-return tests with a synthetic returning
  allocator do not prove those returns are reachable under stock OOM.
- `scheduler_resume.c`: suspend4181d8, resume418228, next-unblock418b28.
  Pending-ready event/state items removed, cursors repaired, ready insertion,
  next-unblock refresh, deferred tick replay and PendSV request.96 cases/424
  bytes; tick418408 synthetic, coherent lists and manual status registers.
  Dynamic creator+real heap+suspend/resume3 cases/1392 bytes, without pending
  tasks/deferred ticks in that linked profile.
- Executed priority 56 fatal-store comparison1 case/398 bytes closes the earlier
  static-failure coverage gap. HardFault dispatch remains outside the model.

All figures are per-profile, overlap, and are not additive coverage. Scripts
bind source hashes and the locked image; historical receipts may predate later
source/test additions. Use matching current profiles and source bindings, not
an old PASS label alone. Hardware timer/exception timing requires an actual
trace or a simulator implementing the corresponding Cortex-M55 peripheral and
exception model; source recovery itself continues independently of that input.

`scheduler_tick.c` now recovers418408: suspended ticks accumulate at20027154;
active ticks increment20027148, swap the two delayed lists on32-bit wrap (old
list must be empty), move due tasks and optional event items to ready lists,
refresh next-unblock, and request equal-priority timeslicing through the return
flag when current ready count≥2.288 cases/348 original bytes. Units are raw
ticks; no milliseconds or tick rate are claimed. Resume linked to this actual
tick body passes96 cases/502 bytes. Dynamic creation linked to actual RTOS
heap and suspend/resume/tick module passes3 cases/1392 bytes (tick not reached
in its no-deferred-ticks initial state).

The FP PendSV variant also passes2 cases/244 bytes: S16–S31 save/restore on
manually seeded extended software/hardware frames, M33-compatible Unicorn,
stopped before BX EXC_RETURN. Actual lazy FP stacking and exception return
remain unverified. Thus “extended frames untested” in the earlier non-FP
profile means that profile only; it is superseded by the separate FP receipt.

Current external validation boundaries: physical STIMER clock/interrupt/MMIO
behavior; automatic Cortex-M55 exception stacking/unstacking and lazy FP
behavior; exact original toolchain/linker/compression/layout and byte equality.
Those do not block recovery of remaining in-image services. IAR authentication
remains a separate user step; no licensed compiler activation occurred here.

## Further startup integration (2026-10-06)

The allocator integration executes actual TLSF initialization as well as the
thread startup chain through SVC2: 2 cases / 2742 original instruction bytes.
The timer integration replaces the 41b6fa provider with reconstructed timer
configuration and helper bodies: 2 / 3178. The NOR integration also executes
420476 orchestration, 42059e JEDEC-ID helper and 4205f4 status transfer:
6 / 3592, including initializer and ID-read failures. Main proceeds to SVC2
despite these NOR failures; it ignores this provider's return.

Receipts are under `g2/build/bootloader-completion/thread-{allocator,timer,nor}-startup-compatible/`.
Each has its own explicit provider/MMIO/input limits; counts overlap and must
not be added. Timer counters are synthetic register RAM, clock requests/releases
are currently intercepted, and the NOR HAL/reset/XIP/flag/power/transfer calls
remain synthetic. Raw timer interval32 does not imply a frequency.

`verify_svc.py` against the pendsv-compatible ELF separately passes 10 / 132.
It supplies explicit frames, checks both MSP/PSP LR-bit branches, enables FPU
and restores the first task for SVC2, and observes the invalid-store fatal path
for immediate0/1/3/255. It stops before architectural exception return; automatic
stacking/unstacking and hardware scheduling remain unverified.

The separate `../manager_task/` component reconstructs the manager's OTA
selection and bounded flag-wait loop. It is not yet automatic SVC-to-task
integration; its MRAM flag, setup and scheduler/event inputs are fixtures.

The linked clock-dispatch startup profile now passes 6 / 3634 with the actual
private dispatcher. Timer request ID7 returns6, which timer configure ignores;
no other clock class is entered in that fixture. Source classes 0/1/3 now exist
in `../clock_manager`; classes 2/4/5/6 remain dependency providers.

`thread_priority.c` reconstructs current getter4161c6/418b4e and setter4161ce/
41806e. Its standalone profile passes 247 cases /462 original bytes with no
provider cuts: priority rise/fall/equality, inherited effective priority versus
base, ready and delayed noncurrent tasks, circular-list cursor repair, protected
event-value high bit, normal/sentinel critical nesting, rejected arguments and
priority 56 fatal store. The wrapper accepts 56 but the lower setter faults at 56,
just as the creation wrapper/initializer boundary does. This is recovered stock
behavior, not a proposed fix. These tests compare list/TCB/global/register state,
not actual preemption or priority-inheritance acquisition/release.

The latest MSPI-linked startup profile passes **10 cases / 4206 original
instruction bytes**. It replaces the 420254 cut with actual initializer and
424a5a handle constructor source, compares the full module 1 state record
(8d0 bytes), device/handle outputs and slot record, then continues through
NOR/manager/idle/timer creation to SVC2. HAL power/config/device/enable failures
and JEDEC transfer failure are included. Physical MSPI HAL, IRQ, reset/XIP,
identification scan, flags and transfer behavior remain synthetic.
