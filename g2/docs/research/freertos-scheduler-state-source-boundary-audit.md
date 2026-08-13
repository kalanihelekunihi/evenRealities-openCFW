# G2 FreeRTOS scheduler-state source-boundary audit

Status: source-integrated in the Apollo-main production overlay  
Scope: official G2 package `2.2.6.10`, Apollo-main application; offline
analysis, host/target compilation, and subsequent source-overlay integration,
with no signing, flashing, or hardware access

## Result

The next lowest-risk exact-upstream FreeRTOS boundary after
`xTaskGetCurrentTaskHandle` is FreeRTOS-Kernel V10.5.1
`xTaskGetSchedulerState`:

| Property | Recovered value |
|---|---|
| Official range | `0x004558A4...0x004558C3` |
| End-exclusive range | `[0x004558A4,0x004558C4)` |
| Size | 32 bytes |
| SHA-256 | `619a0c1adee43616c7a6e9566fec269cd838c72d14e62358b80cb21fbe76ad53` |
| Upstream source | `third_party/freertos-kernel/tasks.c`, `xTaskGetSchedulerState` |
| Direct callers | ten `BL` sites |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| TCB fields read | none |
| Stock global seams | `xSchedulerRunning` at `0x20074A3C`; `uxSchedulerSuspended` at `0x20074A58` |
| Integrated target implementation | one 32-byte relocation-free Thumb leaf |

The official instructions exactly implement the released V10.5.1
three-state policy:

- return `taskSCHEDULER_NOT_STARTED` (`1`) when the running word is zero;
- otherwise return `taskSCHEDULER_RUNNING` (`2`) when the suspension-depth
  word is zero;
- otherwise return `taskSCHEDULER_SUSPENDED` (`0`).

The first zero case short-circuits without reading the suspension depth,
matching the released source. The function makes no call, accesses no object
through a pointer, and has no port, interrupt, TCB, or vendor-structure seam.
Its complete source-replacement boundary is therefore unequivocal.

The production-integrated source is
`components/apollo_main/core_overlay/runtime_freertos_scheduler_state.c`.
The Apollo-main overlay registers the source and redirects the complete
authenticated stock entry to it.

## Authoritative inputs

The reviewed official image is:

| Property | Value |
|---|---|
| File | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application bytes | `3,523,364` |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Application load address | `0x00438000` |

The source comparator is the authenticated FreeRTOS-Kernel V10.5.1
snapshot:

| Property | Value |
|---|---|
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `tasks.c` bytes | `223,695` |
| `tasks.c` SHA-256 | `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| `tasks.c` Git blob | `d97085d8736905c1eeb9d9e871c81e5970ee70ed` |

`third_party/freertos-kernel/verify_snapshot.py` authenticates the annotated
tag, peeled commit, tree, selected file blobs, and retained MIT license.

## Exact stock-to-source proof

The complete official body is:

```text
004558A4  ldr.w   r0, [pc, #0x7BC]  ; literal at 0x00456064
004558A8  ldr     r0, [r0]           ; xSchedulerRunning
004558AA  cmp     r0, #0
004558AC  bne     0x004558B2
004558AE  movs    r0, #1             ; NOT_STARTED
004558B0  b       0x004558C2
004558B2  ldr.w   r0, [pc, #0x7B4]  ; literal at 0x00456068
004558B6  ldr     r0, [r0]           ; uxSchedulerSuspended
004558B8  cmp     r0, #0
004558BA  bne     0x004558C0
004558BC  movs    r0, #2             ; RUNNING
004558BE  b       0x004558C2
004558C0  movs    r0, #0             ; SUSPENDED
004558C2  bx      lr
```

The official bytes are:

```text
dff8bc070068002801d1012007e0dff8
b4070068002801d1022000e000207047
```

At `0x004558A4`, aligned architectural PC `0x004558A8` plus `0x7BC`
selects literal word `0x00456064`, whose value is `0x20074A3C`. At
`0x004558B2`, aligned PC `0x004558B4` plus `0x7B4` selects
`0x00456068`, whose value is `0x20074A58`. The adjacent literal bytes are
`3c4a0720584a0720`.

This is a one-to-one instruction mapping to the released source:

1. test volatile `xSchedulerRunning` against `pdFALSE`;
2. if false, return constant `taskSCHEDULER_NOT_STARTED`;
3. otherwise test volatile `uxSchedulerSuspended` against unsigned
   `pdFALSE`;
4. return `taskSCHEDULER_RUNNING` for zero or
   `taskSCHEDULER_SUSPENDED` for nonzero.

The return constants are pinned by pristine V10.5.1 `task.h`: suspended
`0`, not-started `1`, and running `2`.

The neighboring boundaries are independently pinned:

| Range | Recovered content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x0045589C,0x004558A4)` | `xTaskGetCurrentTaskHandle` | 8 | `c7437c4b802c4991fe9a7bda7e790a1e252276812c72d57ef2b0db2cc18ac661` |
| `[0x004558A4,0x004558C4)` | `xTaskGetSchedulerState` | 32 | `619a0c1adee43616c7a6e9566fec269cd838c72d14e62358b80cb21fbe76ad53` |
| `[0x004558C4,0x004558CC)` | padding/literal data before the next function | 8 | `100260c9dee102e78bd4e6abef6f51428506ae5d24384ab87fa2e44b42244bbe` |

There is no fall-through from either function neighbor. The selected
function owns its terminal `bx lr` and includes no padding or literal data.

## Global-seam closure

The two fixed SRAM words are not assigned names from proximity alone.
Independent stock writer paths confirm their released-source roles.

### Running flag

The scheduler-start path at `0x00454D4A...0x00454D51` executes:

```text
movs    r0, #1
ldr.w   r1, [pc, #0x5C4]  ; literal at 0x00455314
str     r0, [r1]
```

Literal `0x00455314` is `0x20074A3C`, the same word read by the audited
leaf. This is pristine `xSchedulerRunning = pdTRUE` immediately before the
retained port scheduler start.

### Suspension depth

The complete leaf at `[0x00454D7C,0x00454D88)` loads the literal at
`0x00455468`, reads word `0x20074A58`, increments it, stores it, and returns.
Its 12 bytes have SHA-256
`3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2`.
This is pristine `vTaskSuspendAll`.

The resume path at `0x00454DEA...0x00454DF3`, after its nonzero assertion
and critical-section entry, reads the same word, subtracts one, and stores
it. Its exact bytes are:

```text
edf771f93068401e3060
```

Those independent increment and decrement paths prove a nested unsigned
suspension depth, not a Boolean or vendor flag. The scheduler-state leaf
correctly treats every nonzero value as suspended.

The integrated implementation intentionally retains these two fixed addresses.
A future fully linked FreeRTOS kernel should replace them with source symbols
only as part of one atomic kernel-global RAM-layout migration.

## ABI and configuration closure

The callable ABI is ordinary 32-bit Arm AAPCS:

| Item | Contract |
|---|---|
| Arguments | none |
| Return | signed 32-bit scheduler-state constant in `r0` |
| Stock scratch state | `r0` and condition flags |
| Candidate scratch state | `r0`, caller-clobbered `r1`, and condition flags |
| Stack use | none |
| Calls/tail calls | none |

The body does not require:

- the size or any field offset of G2's vendor-extended TCB;
- ready, delayed, queue, timer, event-group, or list object layout;
- interrupt masking, a critical section, or scheduler suspension around the
  reads;
- the Cortex-M55 port, TrustZone, MPU, FPU, or Apollo STIMER configuration;
- an assertion path, trace hook, callback, allocator, or libc helper.

V10.5.1 compiles the function when either
`INCLUDE_xTaskGetSchedulerState == 1` or `configUSE_TIMERS == 1`.
The recovered G2 configuration proves `configUSE_TIMERS=1`; therefore the
entry and its pristine body do not depend on resolving the remaining
`INCLUDE_xTaskGetSchedulerState` choice.

Both globals are volatile 32-bit FreeRTOS base types. Tests additionally
cover negative and otherwise noncanonical nonzero running values, suspension
depths above one, and `UINT32_MAX`. This proves the source retains the exact
zero/nonzero policy rather than narrowing either seam to a byte or Boolean.

## Whole-image topology

The complete installed application was scanned at every halfword for Thumb
`BL`, `B.W`, narrow unconditional/conditional branches, `CBZ`, and `CBNZ`,
and at every byte for possible even or odd/Thumb stored addresses.

### Direct entry references

| Call site | Encoding | Observed use of return |
|---|---|---|
| `0x00441852` | `14f027f8` | queue-path assertion distinguishes suspended state |
| `0x00441B48` | `13f0acfe` | queue-path assertion distinguishes suspended state |
| `0x00441C74` | `13f016fe` | queue-path assertion distinguishes suspended state |
| `0x0044901E` | `0cf041fc` | execution-context check distinguishes not-started state |
| `0x0044904C` | `0cf02afc` | initialization gate checks not-started state |
| `0x0044906E` | `0cf019fc` | wrapper maps all three scheduler states |
| `0x004490A4` | `0cf0fefb` | initialization gate checks not-started state |
| `0x0044AAE2` | `0af0dffe` | diagnostic path distinguishes not-started state |
| `0x0047E7DE` | `d7f761f8` | timer command permits blocking only while running |
| `0x0047EC44` | `d6f72efe` | timer/event path distinguishes suspended state |

The SHA-256 of those addresses packed in order as little-endian 32-bit words
is
`609013b7cfb9a23d1572508ddc6d8da5466fff4dcdd9083f11de9d47cd848733`.

The scan finds:

- exactly those ten `BL` calls to the entry;
- no `B.W` or narrow branch to the entry;
- no external direct branch into the 30-byte interior;
- no stored even entry address, odd/Thumb entry address, or interior address,
  including in an unaligned byte-granular scan.

There is therefore no callback table, vector, jump table, hidden alternate
entry, or interior ownership that must move with the function.

## Integrated source implementation

The integrated implementation preserves the released decision tree and the
MIT notice. Its
only G2 adaptations name the two authenticated stock words through
`OPEN_CFW_FREERTOS_SCHEDULER_RUNNING` and
`OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED`. Tests override those macros with
instrumented host readers; the freestanding Arm build uses `0x20074A3C` and
`0x20074A58`.

With the core overlay's Cortex-M flags at `-O2`, Clang emits:

```text
00000000  movw    r0, #0x4A3C
00000004  movt    r0, #0x2007
00000008  ldr     r1, [r0]
0000000A  cmp     r1, #0
0000000C  itt     eq
0000000E  moveq   r0, #1
00000010  bxeq    lr
00000012  ldr     r0, [r0, #0x1C]
00000014  cmp     r0, #0
00000016  mov.w   r0, #0
0000001A  it      eq
0000001C  moveq   r0, #2
0000001E  bx      lr
```

The compiler folds the second absolute word into a `+0x1C` load from the
first word's address; both endpoints are individually pinned by the source
and tests.

The target bytes are:

```text
44f63c20c2f207000168002904bf0120
7047c06900284ff0000008bf02207047
```

The emitted function is 32 bytes with SHA-256
`93ec039f8b8fd056e62524a8ae691c9e0cbe2be878b2610347deb960d930fe2c`.
It has no relocation, undefined symbol, data section, callee, or second
function. It happens to equal the stock body size, but exact size equality is
not relied upon for behavioral identity.

## Focused validation

`tests/test_runtime_freertos_scheduler_state.py` contributes nine tests that:

- authenticate the official image and vendored V10.5.1 snapshot;
- pin the complete stock body, neighbors, literal addresses, and both SRAM
  words;
- pin independent scheduler-start, suspend, and resume writer semantics;
- host-execute the full zero/nonzero truth table with edge values;
- prove the running-word false case skips the suspension-depth read;
- pin the target symbol, bytes, SHA-256, lack of relocations, and lack of
  undefined symbols;
- scan the complete official application for wide and narrow branch topology;
- scan every byte for stored entry and interior pointers.

Source SHA-256 is
`3276b613e2100191cebbd15f151e636b2feae410cd5aaae09ac18fcefc82af02`;
fixture SHA-256 is
`3da5604e2dcded353217e829bcc01b23a63b13c54e951454c378fd8b152d97e0`;
and test SHA-256 is
`5e13f830130362b320ec53b9ed94443a062e60a1e457e05eb984420c950bde2d`.

The focused suite passes:

```text
Ran 9 tests in 4.020s

OK
```

## Applied integration contract

The Apollo-main production overlay:

1. registers only
   `open_cfw_freertos_task_get_scheduler_state` as the new source;
2. redirects the complete 32-byte stock span
   `[0x004558A4,0x004558C4)` with the established `B.W` plus NOP policy;
3. retains fixed global words `0x20074A3C` and `0x20074A58` until kernel RAM
   globals are migrated atomically;
4. preserves all ten existing caller instructions.

Aggregate relocation drift, package ownership, reproducibility, and
full-regression gates remain required whenever this integration changes.

## Ranked follow-ups

1. The retained private queue creation and mutex-initialization helpers are
   identifiable V10.5.1 code, but they include allocator, list, trace, and
   queue-layout dependencies and should be recovered as a cluster.
2. `pcTaskGetName` is source-identifiable, but it crosses the
   vendor-extended TCB ABI and should follow a focused TCB/name-offset audit.
3. Additional small task-query leaves near the released `tasks.c` tail are
   candidates only after entry boundaries and TCB field offsets are closed.
4. Cortex-M55 port functions are source-correlated but remain port- and
   interrupt-policy boundaries, so they are less suitable than generic
   kernel leaves for the next atomic increment.
