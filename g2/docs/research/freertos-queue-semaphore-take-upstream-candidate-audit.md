# FreeRTOS `xQueueSemaphoreTake` upstream candidate audit

Status: exact, reviewed, production-promoted source replacement for official
G2 package `2.2.6.10`

Scope: Apollo-main source qualification and atomic production integration.
No signing, flashing, or hardware state was changed.

## Result

The complete official routine at `[0x00441C44,0x00441DA6)` is unequivocally
FreeRTOS-Kernel V10.5.1 `xQueueSemaphoreTake()`. The candidate in
`components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.c`
is a separately named, freestanding adaptation of the pristine released
operation. It retains the upstream MIT notice and is now the production target
for the authenticated stock entry replacement.

The timeout-disinherit path is source-closed with the already-qualified
`open_cfw_freertos_queue_get_disinherit_priority_after_timeout()` candidate.
The semaphore-take target object has exactly one undefined executable symbol:
that helper. The helper target object defines it, imports nothing, and has no
text relocation. Other calls remain explicit fixed-address stock seams, so
this qualification does not imply that the scheduler, port, or remaining
private queue routines have been independently promoted here.

## Authenticated upstream and admitted boundary

The comparator is the retained FreeRTOS-Kernel V10.5.1 snapshot:

| Property | Value |
|---|---|
| Tag | `V10.5.1` |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `queue.c` bytes | 125,614 |
| `queue.c` SHA-256 | `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` |
| License | MIT |

`third_party/freertos-kernel/verify_snapshot.py` authenticates the annotated
tag, peeled commit, tree, retained Git objects, and license before the focused
test accepts the oracle.

The new admitted files are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.c` | 5,867 | `7bc1adb794188c36fe0693ef4dcf0e45b83cb32ba523142ecb72e703d65979e2` |
| `components/shared/freertos/runtime_freertos_queue_semaphore_take_upstream_candidate.h` | 10,052 | `e570c374e46115987810cd958773292bc80a8ef98b5cb9503a51327ef15328fd` |
| `tests/fixtures/runtime_freertos_queue_semaphore_take_upstream_candidate_host.c` | 12,124 | `f9d965e6a5a41f80ccfc68e447fb11d280244ee909d6034e0ee9afce7fc4ee1d` |
| `tests/fixtures/runtime_freertos_queue_semaphore_take_upstream_oracle_host.c` | 10,734 | `a8cffb7a592b07ebe6e6aa931dd7e28dfc5497a5a6362450fcf254bed160a3ac` |

The existing qualified dependency remains pinned at:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.c` | 2,620 | `37a4ea5a258befb3b607bf5b0c3e6f28b60ed11279b98e13910e0a125519db3a` |
| `components/shared/freertos/runtime_freertos_queue_get_disinherit_priority_after_timeout.h` | 4,456 | `cd97393461faefa962b91b286977226e1e7c3f1e3dc5a5167c415d5e33c5bd1f` |

The focused test also pins the recovered `FreeRTOSConfig.h`, Clang port and
string adapters, upstream provenance record, and snapshot verifier. This
prevents a configuration or host-oracle change from silently changing the
reference behavior.

## Recovered compile-time configuration and ABI

Only values used by this closure are admitted. They are independently
consistent between the official disassembly, the recovered configuration, and
the pristine source conditionals:

| Parameter | Recovered G2 value |
|---|---|
| `BaseType_t`, `UBaseType_t`, `TickType_t` | 32-bit |
| pointer width | 32-bit |
| `configUSE_MUTEXES` | `1` |
| `configUSE_PREEMPTION` | `1` |
| `configUSE_TIMERS` | `1` |
| `INCLUDE_xTaskGetSchedulerState` | `1` |
| `configUSE_QUEUE_SETS` | `0` |
| `configMAX_PRIORITIES` | `56` |
| `tskIDLE_PRIORITY` | `0` |
| `Queue_t` size | `0x50` |
| mutex marker / `uxQueueType` | `pcHead == NULL`, the upstream alias |
| mutex holder | queue `+0x08` |
| send wait list | queue `+0x10` |
| receive wait list | queue `+0x24` |
| semaphore count | queue `+0x38` |
| length / item size | queue `+0x3C` / `+0x40` |
| receive / transmit lock | queue `+0x44` / `+0x45` |
| `List_t` / `TimeOut_t` | 20 / 8 bytes |

A potentially ambiguous mutex test is now closed by upstream itself:
`queue.c` defines `uxQueueType` as `pcHead` and `queueQUEUE_IS_MUTEX` as
`NULL`. Therefore the candidate's `queue->head == 0` is the released source
representation, not a vendor-specific semantic substitution.

## Official function boundary and source mapping

The authoritative OTA package is 3,523,396 bytes with SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`.
Removing its 32-byte preamble yields the installed application at runtime base
`0x00438000`, SHA-256
`19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

| Range | Identity | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00441B0A,0x00441C44)` | preceding `xQueueReceive` | 314 | `f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560` |
| `[0x00441C44,0x00441DA6)` | selected `xQueueSemaphoreTake` | 354 | `4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c` |
| `[0x00441DA6,0x00441E66)` | following `xQueueReceiveFromISR` | 192 | `cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4` |
| `[0x00441EC4,0x00441ED8)` | qualified private disinherit-priority helper | 20 | `21721e8f80852df9a1d4f0f23db76d3144a4c8c04a81606dccee5b3ff132819c` |

Every semantic region of the released implementation is present:

1. validate the queue, zero item size, and scheduler/blocking invariant;
2. atomically decrement a nonzero semaphore count;
3. record the current task as mutex holder for a mutex;
4. unblock a waiting giver and yield under preemption when required;
5. initialize timeout state once, suspend the scheduler, and lock the queue;
6. retry when a token appears before timeout;
7. inherit the mutex holder's priority before blocking on the receive list;
8. unlock, resume, and yield when resume did not already switch tasks; and
9. on timeout, compute the highest remaining waiter priority and disinherit the
   holder before returning `errQUEUE_EMPTY`.

Trace and coverage hooks compile to no operations under the recovered build;
they introduce no semantic source gap.

## Outgoing call closure

The official body has 33 direct `BL` instructions. Grouped by target:

| Target | Calls | Role |
|---|---:|---|
| `0x005FA0A4` | 3 | configured assertion failure |
| `0x004558A4` | 1 | scheduler state |
| `0x00441F88` | 3 | private queue unlock |
| `0x00454DCC` | 3 | resume scheduler |
| `0x004420D0` | 4 | enter critical |
| `0x00455556` | 1 | set timeout state |
| `0x004420E8` | 6 | exit critical |
| `0x00454D7C` | 1 | suspend scheduler |
| `0x00455566` | 1 | timeout check |
| `0x00441FF6` | 2 | private queue-empty query |
| `0x004558CC` | 1 | priority inheritance |
| `0x00455282` | 1 | place task on event list |
| `0x004420BC` | 2 | yield within API |
| `0x00455AE0` | 1 | increment mutex-held count |
| `0x00455370` | 1 | remove task from event list |
| `0x00441EC4` | 1 | highest remaining waiter priority |
| `0x00455A1C` | 1 | priority disinherit after timeout |

The helper call is exactly at `0x00441D90`, encoding `00f098f8`. In the new
target object this call is deliberately the sole `R_ARM_THM_CALL` relocation,
resolved by the separately compiled qualified helper. Fixed stock seams remain
immediate Thumb addresses and create no undefined ELF symbols.

## Caller and interior-reference topology

An exhaustive halfword-aligned Thumb scan finds exactly ten direct calls to
the public entry:

```text
0x00441780 00f060fa   0x00449802 f8f71ffa
0x0044999E f8f751f9   0x00449DA0 f7f750ff
0x00473842 cef7fff9   0x00484196 bdf755fd
0x004841F0 bdf728fd   0x00484246 bdf7fdfc
0x004842AE bdf7c9fc   0x00514014 2df716fe
```

Their ordered address digest is
`f713585a87faff9b034d775b62f3e98cf2cc6f292bd6fa556731a37588effb91`;
their address-plus-encoding digest is
`d2fd8eb3089d8db9783c09630b6ed9505b361be17da450fdc3bda5c2b38e8e1b`.
There is no public-entry `B.W`, wide conditional branch, narrow branch, or
external direct transfer to an interior instruction.

The byte-granular raw-value scan does report one apparent Thumb interior
pointer and it is not waived:

```text
raw address 0x005A9FB5 -> apparent value 0x00441D43
```

The ordered raw-record digest is
`55fca9e006b9d8ada8e1f9a1b64d3efadc2cc88e75ab9d40fbd875a8c7eb726c`.
Both the four-byte-aligned and halfword-aligned scans are empty. Focused linear
disassembly proves why: `0x005A9FB5` is an odd byte inside live executable
instructions. The surrounding entry at `0x005A9F98` begins with a `PUSH.W`
and has direct callers at `0x005A6574`, `0x005A8C20`, and `0x005AA41E`.
At the collision itself:

```text
0x005A9FB4  4543  MULS r5,r0,r5
0x005A9FB6  1d44  ADD  r5,r3
0x005A9FB8  0029  CMP  r1,#0
```

The four bytes beginning at the second byte of the `MULS` happen to read as
`43 1d 44 00`, or little-endian `0x00441D43`. The pinned 50-byte executable
context `[0x005A9F98,0x005A9FCA)` hashes to
`7c65189b672effd1b500b23b8d5b423bb446c504f2efdc269279959fdac332be`.
It is therefore an overlapping instruction-window coincidence, not stored
pointer data or an addressable Thumb instruction boundary.

## Exact pristine-source differential

The oracle fixture includes the authenticated pristine V10.5.1 `queue.c` and
invokes its real `xQueueSemaphoreTake()`. Its real private
`prvGetDisinheritPriorityAfterTimeout()` remains in the same translation unit.
Only the public task, allocator, list-initialization, and port seams are
scripted. The candidate fixture uses the same scripts and invokes the new
candidate plus the independently qualified project helper source.

For every case, the test compares the return, semaphore count, send/receive
waiter counts, mutex holder, both queue locks, timeout-check count,
disinherit holder and priority, and the complete ordered provider event and
argument trace. The cases cover:

- immediate ordinary semaphore take with a waiting giver and preemption;
- immediate mutex take and holder assignment;
- empty zero-wait failure;
- immediate timeout;
- token arrival during the timeout check and retry;
- block, yield, second check, and successful retry; and
- mutex priority inheritance, blocking, timeout, highest-waiter calculation,
  and disinherit to priority 6.

All snapshots and complete event traces match the pristine oracle exactly.
The last case proves the closure call ordering and arguments: inheritance
precedes placement on the receive list, the helper returns 6 from the genuine
receive-list state, and disinherit receives the original holder and priority
6.

## Apple and exact-root Linux target objects

Both reviewed profiles compile the semaphore candidate and helper twice using
the production Thumbv7E-M freestanding flags. Same-profile object pairs are
byte-identical.

| Profile | Candidate section | Candidate object | Helper section | Helper object |
|---|---|---|---|---|
| Apple Clang 21.0.0 | 602 bytes, SHA `c5b343d383bd3fa14d706f23ae1b7b46114583f2310e1ad77cad53635bd4276b` | 1,732 bytes, SHA `8e61053ec89d646062c0f84f6993069bc9acb2d6b19d72d861a6e52b087a1688` | 18 bytes, SHA `fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519` | 960 bytes, SHA `62ba4254d1709331735f4b1e8ec3c2f412a5ccdaa73c0d3a8086497f6ae5a04d` |
| Homebrew Clang 22.1.8, exact root | 600 bytes, SHA `e5021439d803107fff7701c5c335ca9d70297cedf3d4dfc2a88f1445c46ea619` | 1,708 bytes, SHA `97a32188abc9977e40a403d709679351c70ec5e895488ccf3f94b39fb76d2f54` | 18 bytes, same SHA | 940 bytes, SHA `f48b96a42912c1cb07aed3097fce5eb0f79b065400212bb988ffeee89f1a1e50` |

Both function sections are four-byte aligned. Apple places the helper call
relocation at candidate offset `0x244`; Linux places it at `0x242`. In both
cases it is type 10, `R_ARM_THM_CALL`, and names only the qualified helper.
The helper object has no undefined symbols or text relocation. The ordinary
anonymous type-42 `.ARM.exidx` metadata relocation is not executable closure.

Linux qualification used `/home/linuxbrew/.linuxbrew/bin/clang` and source
root `/Users/kalani/Repo/SybilSightABCD/openCFW` inside the retained
`opencfw-linux-llvm` container. It did not infer Linux bytes from Apple output
or substitute the native `/workspace` spelling.

## Atomic production promotion

The production overlay now appends the helper before the semaphore operation
and resolves the operation's sole `R_ARM_THM_CALL` to that source leaf. The old
broader `open_cfw_freertos_queue_semaphore_take` body is excluded from the
production compilation order; it remains behind an explicit host-oracle guard
for behavioral regression tests. The public stock span
`[0x00441C44,0x00441DA6)` redirects to the candidate and is NOP-filled.

| Profile | Helper placement | Semaphore placement | Overlay | Component | Package |
|---|---|---|---|---|---|
| Apple Clang 21.0.0 | offset 120,708, 18 bytes, `fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519` | offset 120,728, 602 bytes, relocated `77c3f659ca8916cd23c44f37e021f7a2c7f6bf9bf460b3f509cbebcc14e7193d` | 121,330 / `b0e7ec99bdf68b0b42b79e2bb935274f6b5a12d53a449cca3f021fa906ad1e3c` | 3,644,726 / `d9af47dd5b4668f23722a530df40b12dfb926ef5c0cc6fb603733b2e14a05a17` | 4,423,180 / `74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d` |
| exact-root Linux Clang 22.1.8 | offset 122,564, 18 bytes, `fdb52b44dbd26f4b66e98b7e7586ad503c2dbb5c7e01ff5c9818b3536c2d2519` | offset 122,584, 600 bytes, relocated `38e981592ecb3f7c2e2a205efc7366d72e61c10693fc57947bd62de80fe44392` | 123,184 / `2ece296109ba518aa5e9474bc46dc0f77003abd57231c5becd6525dd18673c63` | 3,646,580 / `0c65b98e4867b7aa143572ccb831879c88ebeded4c8e41d2e294a72bd0ea61a9` | 4,425,034 / `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1` |

The assembled-image audit proves that no wide or narrow branch and no stored
even or Thumb-form pointer reaches the retained stock helper
`[0x00441EC4,0x00441ED8)`. Its exact official bytes remain unchanged and no
redirect is necessary. The recursive mutex wrapper materializes the odd public
entry `0x00441C45` with `MOVW/MOVT r2` and reaches it with the one authenticated
`BLX r2`; it cannot bypass the public patch. Thus the candidate/helper pair is
source-closed without mutating the now-unreachable stock helper.

## Validation

Apple Clang:

```sh
python3 -m unittest -v \
  tests.test_freertos_queue_semaphore_take_upstream_candidate
```

Result: 7/7 passed.

Exact-root Linux/Homebrew Clang:

```sh
OPENCFW_CLANG=/home/linuxbrew/.linuxbrew/bin/clang \
OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
python3 -m unittest -v \
  tests.test_freertos_queue_semaphore_take_upstream_candidate
```

Result: 7/7 passed.
