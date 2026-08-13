# FreeRTOS `tasks.c` next closure audit

Status: production-integrated and dual-profile qualified for official G2
package `2.2.6.10`; the candidate sections below preserve the pre-promotion
read-only analysis

## Result

The smallest coherent, dependency-free, and functionally useful remaining
FreeRTOS `tasks.c` boundary is the released V10.5.1 private helper
`prvTaskCheckFreeStackSpace`:

| Property | Recovered value |
|---|---|
| Official range | `[0x00455820,0x00455836)` |
| Size | 22 bytes |
| SHA-256 | `4719035f92eec4dbde4be499b966bb24eead59d609a3b0f362724e7efe616048` |
| Upstream source | `third_party/freertos-kernel/tasks.c`, `prvTaskCheckFreeStackSpace` |
| Direct callers | one, `BL` at `0x0045579A` |
| Calls made | none |
| Fixed globals or providers | none |
| Direct TCB/list access | none |
| External entry/interior branches | none other than the one entry `BL` |
| Stored entry/interior pointers | none; one unaligned cross-instruction false hit |
| Configuration inputs | fill byte `0xA5`, downward-growing stack, 4-byte `StackType_t`, 16-bit `configSTACK_DEPTH_TYPE` |
| License | FreeRTOS MIT |

The function counts consecutive stack-fill bytes, converts the byte count to
32-bit stack words, truncates the result to the configured 16-bit depth type,
and returns. Every official instruction maps in order to the authenticated
V10.5.1 source. The G2-specific work is limited to recovering the four macro
and type selections that instantiate that source; there is no private G2
algorithm to decompile or recreate.

This boundary is useful beyond its small 22-byte stock footprint. It is the
only callable opaque helper below the trace-enabled `vTaskGetInfo` path, which
feeds task-status and system-state diagnostics. Promoting it removes an exact
opaque dependency and leaves a much cleaner future boundary around
`vTaskGetInfo` without taking on scheduler mutation, list ownership, or the
vendor-extended TCB tail.

## Current-production exclusion check

The production graph was reviewed before selecting the boundary. It already
source-owns these authenticated `tasks.c` operations:

- `xTaskGetTickCount` and `xTaskGetTickCountFromISR`;
- `uxTaskGetNumberOfTasks` and `pcTaskGetName`;
- `vTaskSuspendAll`, `xTaskResumeAll`, and `xTaskIncrementTick`;
- `vTaskInternalSetTimeOutState` and `vTaskMissedYield`;
- `prvResetNextTaskUnblockTime`;
- `xTaskGetCurrentTaskHandle` and `xTaskGetSchedulerState`;
- `uxTaskResetEventItemValue`; and
- `pvTaskIncrementMutexHeldCount`.

`prvTaskCheckFreeStackSpace` is absent from all four relevant production
collections in `components/apollo_main/core_overlay/overlay.json`:
`isolated_leaves`, `relocated_leaves`, `in_place_leaves`, and `patch_sites`.
It is therefore a genuinely remaining opaque boundary, not a duplicate
recommendation under a different project-prefixed name.

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
| Runtime range | `[0x00438000,0x00794324)` |

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
V10.5.1 tag, peeled commit, tree, retained file blobs, and MIT license. The
selected source is therefore unequivocal upstream reuse, not a function
reconstructed from pseudocode.

## Complete official boundary

The exact official bytes are:

```text
0100002001e0491c401c0a78a52afad0800880b27047
```

The complete instruction body is:

```text
00455820  0100      movs    r1,r0
00455822  0020      movs    r0,#0
00455824  01e0      b       0x0045582A
00455826  491c      adds    r1,r1,#1
00455828  401c      adds    r0,r0,#1
0045582A  0a78      ldrb    r2,[r1]
0045582C  a52a      cmp     r2,#0xA5
0045582E  fad0      beq     0x00455826
00455830  8008      lsrs    r0,r0,#2
00455832  80b2      uxth    r0,r0
00455834  7047      bx      lr
```

There is no literal pool, alignment halfword, tail-merged return, or
fall-through ownership in the selected span. Its immediate neighbors are
independently bounded:

| Range | Content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x004557B0,0x00455820)` | preceding `prvListTasksWithinSingleList` | 112 | `63602a889f3517bffbd24a33632e71fb509ba29186aebd36d496c7f8ec0ad9bf` |
| `[0x00455820,0x00455836)` | selected `prvTaskCheckFreeStackSpace` | 22 | `4719035f92eec4dbde4be499b966bb24eead59d609a3b0f362724e7efe616048` |
| `[0x00455836,0x00455876)` | following `prvDeleteTCB` | 64 | `86f7fc5725fe0fbbe85c07f68669981bad154cd58163427a6ead8106538e2a12` |

## One-to-one upstream proof

The complete released V10.5.1 operation is:

```c
static configSTACK_DEPTH_TYPE prvTaskCheckFreeStackSpace(
    const uint8_t * pucStackByte )
{
    uint32_t ulCount = 0U;

    while( *pucStackByte == ( uint8_t ) tskSTACK_FILL_BYTE )
    {
        pucStackByte -= portSTACK_GROWTH;
        ulCount++;
    }

    ulCount /= ( uint32_t ) sizeof( StackType_t );

    return ( configSTACK_DEPTH_TYPE ) ulCount;
}
```

The binary-to-source correspondence is exact:

| Official operation | Released-source role |
|---|---|
| copy `r0` to `r1`; clear `r0` | working byte pointer and `ulCount=0` |
| initial branch to the byte test | source `while` pre-test |
| increment `r1` by one | `pucStackByte -= portSTACK_GROWTH` with growth `-1` |
| increment `r0` | `ulCount++` |
| load byte and compare with `0xA5` | compare against `tskSTACK_FILL_BYTE` |
| branch back while equal | source loop |
| logical shift right by two | divide by `sizeof(StackType_t)==4` |
| `uxth r0,r0` | cast to 16-bit `configSTACK_DEPTH_TYPE` |
| `bx lr` | return |

No official instruction lacks an upstream role, and no released source
operation is absent from the official body.

## Exact upstream logic versus recovered G2 parameters

The algorithm comes unchanged from authenticated V10.5.1. Focused
disassembly is needed only to select its compile-time parameters:

| Item | Classification | Recovered value and proof |
|---|---|---|
| loop and count algorithm | exact upstream | instruction order matches the released function completely |
| `tskSTACK_FILL_BYTE` | upstream constant, confirmed in G2 | immediate compare with `0xA5`; V10.5.1 `tasks.c` defines `0xA5U` |
| `portSTACK_GROWTH` | authenticated port choice, confirmed in G2 | pointer increments one byte, proving `-1`; selected ARM_CM55_NTZ port defines `-1` |
| `StackType_t` | authenticated port type, confirmed in G2 | shift by two proves four bytes; selected port defines `uint32_t` |
| `configSTACK_DEPTH_TYPE` | G2 configuration choice | final `uxth` plus caller's halfword store proves `uint16_t`, which is the V10.5.1 default |
| feature gate | G2 configuration | `configUSE_TRACE_FACILITY=1` is independently proven and is sufficient to retain this helper |

The two `INCLUDE_uxTaskGetStackHighWaterMark*` switches do not need to be
guessed. V10.5.1 compiles this helper when any one of trace facility,
high-water-mark, or high-water-mark-2 support is enabled, and the already
proven trace facility makes the condition true.

## Caller, ABI, and structure seam

The sole direct caller is inside official `vTaskGetInfo`:

| Property | Value |
|---|---|
| Caller body | `[0x00455728,0x004557A8)` |
| Caller size | 128 bytes |
| Caller SHA-256 | `53d97f8c2e506f69df7908f9b3d2c644fd4f21b456f5961311f1ce34d975f626` |
| Call site | `0x0045579A` |
| Call encoding | `00f041f8` |
| Ordered caller-address SHA-256 | `500b947255a4da26c3ce4d43573e250360f3068a7ab9c330fa2b88389dc14b97` |
| Address-plus-encoding SHA-256 | `3573325d452b97c91ecc9e6ddb2a6188e7fc9c9fe0c37b25dc2344f6d18be4b8` |

The relevant caller sequence is:

```text
00455794  cmp     r4,#0
00455796  beq     0x004557A2
00455798  ldr     r0,[r5,#0x30]
0045579A  bl      0x00455820
0045579E  strh    r0,[r6,#0x20]
```

This recovers the complete callable ABI:

- `r0` receives a `const uint8_t *` to the low-address edge of a downward
  growing stack;
- the pointer comes from `TCB_t.pxStack` at G2 TCB offset `+0x30`;
- `r0` returns the zero-extended 16-bit count of untouched `StackType_t`
  entries; and
- the caller stores it to `TaskStatus_t.usStackHighWaterMark` at offset
  `+0x20`.

The selected helper itself sees only the supplied byte pointer. It does not
dereference a TCB, `TaskStatus_t`, `List_t`, or `ListItem_t`, so those caller
offsets are evidence for the ABI and configuration rather than dependencies
that must be reproduced in the leaf. No list offset is involved.

The scan-to-first-non-fill-byte behavior assumes the ordinary FreeRTOS stack
initialization contract: the caller supplies a valid stack buffer containing
a non-fill boundary before inaccessible memory. The replacement must preserve
that contract; it should not add a private length argument or bounds policy.
The source counter is exactly `uint32_t`, as in V10.5.1. On the 32-bit target,
a valid object cannot contain `2^32` consecutive accessible fill bytes and a
later sentinel, so a successful valid-buffer scan cannot overflow that
counter. A missing sentinel leaves the upstream contract before it can
produce a defined result. The separately observable narrowing is the final
cast to the 16-bit depth type; focused tests cover the `65,535`, `65,536`, and
`65,537`-word boundary.

## Whole-image reachability closure

The complete installed application was scanned at every halfword for Thumb
`BL`, unconditional `B.W`, narrow unconditional/conditional branches,
`CBZ`, and `CBNZ` into the selected range.

| Reference class | Result |
|---|---|
| direct `BL` to entry | `0x0045579A -> 0x00455820` only |
| direct `B.W` to entry | none |
| external wide branch into interior | none |
| external narrow branch to entry/interior | none |

The leaf has two internal control-flow edges, both wholly owned by the
selected body:

- `0x00455824 -> 0x0045582A`, the loop pre-test; and
- `0x0045582E -> 0x00455826`, the loop back edge.

No external edge targets either interior destination or any other interior
halfword. Redirecting the complete entry therefore preserves all executable
reachability.

Every byte offset in the installed application was also checked for possible
even and odd/Thumb entry or interior address words. There is:

- no naturally aligned stored entry pointer;
- no naturally aligned stored interior pointer;
- no stored Thumb/odd entry or interior pointer; and
- one raw unaligned window at `0x00456353` equal to even entry value
  `0x00455820`.

That last window begins at the second byte of the valid instruction
`0x00456352: 0720 movs r0,#7` and continues through the following
`0x00456354: 5845 cmp r0,r11`. It is not four-byte aligned, is not referenced
as data, crosses instruction boundaries, and has no Thumb bit. It is a pinned
false positive, not a callback or alternate owner.

## Complete dependency closure

The selected function closes on its own:

```text
prvTaskCheckFreeStackSpace
  input: const uint8_t * stack-fill scan origin
  constants: 0xA5, portSTACK_GROWTH=-1, sizeof(StackType_t)=4
  result type: uint16_t
  callees: none
  globals: none
  writable data: none
  read-only data/literals: none
  relocations: none
  TCB/list fields: none inside the leaf
  hooks/trace/assert/port calls: none
```

`configUSE_TRACE_FACILITY=1` explains why the caller and helper exist, but no
trace macro executes inside the helper. Likewise, the source has no
`configASSERT`, critical-section operation, yield, scheduler state, memory
allocator, libc call, or architecture instruction. A target object should
therefore contain only one text section plus ordinary discardable EHABI
metadata and zero undefined runtime symbols.

## Why this boundary comes before other opaque `tasks.c` candidates

| Remaining candidate | Stock bytes | Immediate closure cost | Reason to follow rather than lead |
|---|---:|---|---|
| **`prvTaskCheckFreeStackSpace`** | **22** | no callee/global/TCB/list closure | selected |
| `prvInitialiseTaskLists` | 84 | six call sites to list initialization plus ready/delayed/termination/suspended globals | subsequently promoted with direct source-owned `vListInitialise` closure |
| `prvCheckTasksWaitingTermination` + `prvDeleteTCB` | 60 + 64 | critical sections, list removal, task counters, heap free, TCB `+0x30/+0x6D`, assertion seam | coherent later cleanup cluster |
| `xTaskDelayUntil` + `prvAddCurrentTaskToDelayedList` | 60 + 118 | scheduler suspend/resume, yield, ready/delayed lists, tick arithmetic | broader scheduling mutation |
| `vTaskPrioritySet` | 218 | ready/event lists, current/base priority, yield policy | broad scheduler operation |

This ranking is independent of the concurrent queue-core audit: the selected
helper belongs solely to `tasks.c`, shares no queue layout, and requires no
queue provider.

## Promotion order and implementation contract

Promotion should be one atomic leaf, followed by separately reviewed larger
task helpers:

1. Retain the authenticated V10.5.1 MIT notice and source pin.
2. Add a project-prefixed isolated source adaptation such as
   `open_cfw_freertos_task_check_free_stack_space`, preserving the released
   loop exactly while materializing the four proven configuration selections.
3. Add compile-time checks that `sizeof(StackType_t)==4`,
   `configSTACK_DEPTH_TYPE` is two bytes, and the selected stack-growth value
   is `-1`; keep `0xA5` tied to the upstream constant.
4. Compile it as a four-byte-aligned relocated leaf at the current overlay
   tail. The retained text must have no relocation or undefined symbol.
5. Replace the complete 22-byte official span at `0x00455820` with one Thumb
   `B.W` and nine `0xBF00` NOPs. Leave the stock call at `0x0045579A`
   unchanged; it will reach the entry redirect.
6. Split the canonical manifest's containing opaque region into the 22-byte
   generated replacement plus preserved neighboring regions, then append the
   new source-owned leaf/alignment region.
7. Differential-test the source leaf against the pristine V10.5.1 oracle for
   zero fill bytes, one through three bytes, exact and non-exact multiples of
   four, long runs, and a sentinel after the fill run. Verify truncation to
   16 bits and forward byte traversal.
8. Pin the stock span/hash, sole caller/encoding, internal branch topology,
   absence of external interior branches, and the classified unaligned raw
   address false hit.
9. Rebuild and repin Apple and exact-root Linux artifacts independently, then
   run complete aggregate verification before any hardware consideration.

`prvInitialiseTaskLists` has since been verified and promoted as
`open_cfw_freertos_task_lists_initialize`; its only callable dependency binds
directly to source-owned `open_cfw_freertos_list_initialise`. The termination
cleanup pair is therefore the next candidate in this phase-local ranking and
should remain its own cluster so heap/TCB allocation provenance is not mixed
into the completed dependency-light initializer promotion.

## Validation performed

Read-only validation completed successfully:

- the authenticated FreeRTOS snapshot verifier passed;
- the official package, installed-image, selected-body, neighbor, and caller
  size/SHA-256 pins were recomputed from the official bundle;
- Capstone and Ghidra independently decoded the selected body and caller;
- the full installed image was scanned for wide/narrow entry and interior
  branches and for stored even/odd addresses;
- the current production JSON was parsed and confirmed to contain no existing
  free-stack-check leaf or patch; and
- no production source, configuration, manifest, test, build artifact,
  package, signing state, flash state, or hardware was changed.

This audit establishes source-replacement readiness. It does not claim that
the leaf has already been integrated or that a resulting package has been
tested on G2 hardware.

## Candidate implementation status

The audited boundary now has an isolated, non-production candidate:

| File | Bytes | SHA-256 |
|---|---:|---|
| `components/shared/freertos/runtime_freertos_task_check_free_stack_space.c` | 2,269 | `ba8cd2018984f4e6a131698d86a0eb4abd0d07dd1e81e75979211f00bf3904de` |
| `components/shared/freertos/runtime_freertos_task_check_free_stack_space.h` | 1,267 | `f87ee206a0ab1f62b2b93478e5ca6cf461dc96bfb047af98766b5849a4434d2a` |
| `tests/test_freertos_task_check_free_stack_space_candidate.py` | 20,244 | `c97778be5b3bb23269676390755a6cab70bf508d5c76da7ebdaef430ee79874b` |

The source preserves the released V10.5.1 loop and MIT attribution under the
project-prefixed symbol
`open_cfw_freertos_task_check_free_stack_space`. Its header makes the four
recovered selections explicit and rejects drift at compile time:
`0xA5`, stack growth `-1`, four-byte `StackType_t`, and two-byte
`configSTACK_DEPTH_TYPE`.

Six focused tests pass. They compare the candidate with a separately compiled
pristine-source oracle for zero through three fill bytes, exact and partial
word counts, long scans, and 16-bit result wrap; prove sentinel and surrounding
guard preservation; repin the official body, sole caller, internal and
whole-image branch topology, and unaligned stored-address false hit; and
confirm that production JSON does not name the candidate.

Apple clang 21.0.0 and the qualified Homebrew Linux clang 22.1.8 both emit
the same one 62-byte Thumb function section with SHA-256
`ff66515dc9532c1f35f76e48b2f800e66630027d52910645200832c0c32f0802`.
It has four-byte alignment and no named undefined symbol, writable allocated
section, text relocation, or retained data. The only relocation is the
ordinary discardable `R_ARM_PREL31` record in `.rel.ARM.exidx.*` targeting
`.ARM.exidx.*`. The six focused tests pass under both compilers and pin the
complete text bytes rather than accepting a merely non-empty section.

This is candidate evidence only. The source is deliberately absent from
`overlay.json`, all patch-site lists, manifests, Makefile targets, artifact
pins, production accounting, and package assembly.

## Production promotion result

`prvTaskCheckFreeStackSpace` now has a complete 22-byte stock redirect and a
62-byte relocation-free source leaf. Apple places it at
`[0x007B1400,0x007B143E)`; Linux places the identical bytes at
`[0x007B1B54,0x007B1B92)`. The active leaf retains the pinned SHA-256
`ff66515dc9532c1f35f76e48b2f800e66630027d52910645200832c0c32f0802`.

The production package pins are 4,420,916 bytes /
`1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2`
for Apple and 4,422,792 bytes /
`b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea`
for Linux. A recording pass and two ordinary fail-closed Linux builds were
byte-identical. The prior exclusion checks and candidate-only statements in
this document describe the historical audit stage, not current production
state. No hardware was flashed, reset, or executed.
