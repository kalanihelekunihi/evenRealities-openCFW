# G2 FreeRTOS current-task-handle source-boundary audit

Status: source-integrated in the Apollo-main overlay  
Scope: official G2 package `2.2.6.10`, Apollo-main application; offline
analysis, host/target compilation, and package assembly, with no signing,
flashing, or hardware access

## Result

The next lowest-risk exact-upstream FreeRTOS boundary after the four complete
`list.c` leaves and the seven source-owned `queue.c` entries is
FreeRTOS-Kernel V10.5.1 `xTaskGetCurrentTaskHandle`:

| Property | Recovered value |
|---|---|
| Official range | `0x0045589C...0x004558A3` |
| End-exclusive range | `[0x0045589C,0x004558A4)` |
| Size | 8 bytes |
| SHA-256 | `c7437c4b802c4991fe9a7bda7e790a1e252276812c72d57ef2b0db2cc18ac661` |
| Upstream source | `third_party/freertos-kernel/tasks.c`, `xTaskGetCurrentTaskHandle` |
| Direct callers | seven `BL` sites |
| Stored entry/interior pointers | none |
| External branches into the interior | none |
| Calls made by the function | none |
| TCB fields read | none |
| Stock global seam | `pxCurrentTCB` word at `0x20074A20` |
| Isolated target candidate | one 12-byte relocation-free Thumb leaf |

The complete official algorithm loads the pointer stored in `pxCurrentTCB`
and returns it. It does not dereference the TCB, enter a critical section,
call a port function, inspect scheduler state, or depend on the G2 vendor TCB
extension. The stock instructions and the pristine V10.5.1 source therefore
match unequivocally.

The integrated source is
`components/apollo_main/core_overlay/runtime_freertos_task_current.c`. The
core overlay replaces the complete authenticated stock entry and preserves
the fixed `pxCurrentTCB` seam explicitly.

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

The source comparator is the authenticated FreeRTOS-Kernel V10.5.1 snapshot:

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
0045589C  ldr.w   r0, [pc, #0x7BC]  ; literal at 0x0045605C
004558A0  ldr     r0, [r0]           ; load pxCurrentTCB
004558A2  bx      lr
```

The official bytes are:

```text
dff8bc0700687047
```

For the first instruction, aligned architectural PC is `0x004558A0`.
Adding `0x7BC` selects literal word `0x0045605C`, whose exact little-endian
value is `0x20074A20`. The second instruction reads the pointer stored in that
word; the third returns it in AAPCS result register `r0`.

This maps one-to-one to the released V10.5.1 function:

1. assign volatile global `pxCurrentTCB` to a local `TaskHandle_t`;
2. return that local handle.

The neighboring boundaries are independently pinned:

| Range | Recovered content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00455876,0x0045589C)` | preceding private unblock-time reset leaf | 38 | `a789916ee424c824c5c5f2302e62e4a861f0fa1289917d9c0e095947bce82598` |
| `[0x0045589C,0x004558A4)` | `xTaskGetCurrentTaskHandle` | 8 | `c7437c4b802c4991fe9a7bda7e790a1e252276812c72d57ef2b0db2cc18ac661` |
| `[0x004558A4,0x004558C4)` | `xTaskGetSchedulerState` | 32 | `619a0c1adee43616c7a6e9566fec269cd838c72d14e62358b80cb21fbe76ad53` |

There is no fall-through from either neighbor. The selected function owns
its terminal `bx lr` and contains no padding or literal data.

## ABI and configuration closure

The callable ABI is ordinary 32-bit Arm AAPCS:

| Item | Contract |
|---|---|
| Arguments | none |
| Return | task handle in `r0` |
| Stock scratch state | `r0` and condition flags only |
| Stack use | none |
| Calls/tail calls | none |

The only data seam is a volatile pointer-sized word at `0x20074A20`.
The function does not require:

- the size or any field offset of G2's 112-byte vendor-extended TCB;
- scheduler, ready-list, delayed-list, queue, timer, or event-group layout;
- interrupt masking, a critical section, or scheduler suspension;
- the Cortex-M55 port, TrustZone, MPU, FPU, or STIMER configuration;
- an assertion path, trace hook, callback, or heap operation.

The V10.5.1 function exists when either
`INCLUDE_xTaskGetCurrentTaskHandle == 1` or `configUSE_MUTEXES == 1`.
The recovered G2 configuration proves `configUSE_MUTEXES=1`, and the seven
out-of-line calls prove the entry is retained. No unresolved configuration
choice changes its body.

The fixed RAM seam is appropriate for this incremental replacement because
the current overlay retains the official kernel globals in place. A future
fully linked FreeRTOS kernel should replace the absolute seam with its source
`pxCurrentTCB` symbol as part of one atomic RAM-layout migration.

## Whole-image topology

The complete installed application was scanned at every halfword for Thumb
`BL`, `B.W`, narrow unconditional/conditional branches, `CBZ`, and `CBNZ`,
and at every byte for possible even or odd/Thumb stored addresses.

### Direct entry references

| Call site | Encoding | Observed role |
|---|---|---|
| `0x00441726` | `14f0b9f8` | recursive-mutex give compares the holder with the current task |
| `0x00441768` | `14f098f8` | recursive-mutex take compares the holder with the current task |
| `0x004491AC` | `0cf076fb` | eight-byte task-ID wrapper returns the current handle |
| `0x0044AAEA` | `0af0d7fe` | scheduler-aware diagnostic path passes the current task to the retained name getter |
| `0x004D46F4` | `81f7d2f8` | synchronization-object path snapshots the current task before entering its critical section |
| `0x0057DE9A` | `d7f6fffc` | cleanup path passes the current task to the retained task-delete entry |
| `0x0057E1AA` | `d7f677fb` | synchronization-object path publishes the current task as owner |

The SHA-256 of those addresses packed in order as little-endian 32-bit words
is
`a22105e1442e84e34d21999b89f988c63154933abc8956da81428f09975ab464`.

The scan finds:

- exactly those seven `BL` calls to the entry;
- no `B.W` or narrow branch to the entry;
- no external direct branch into the six-byte interior;
- no stored even entry address, odd/Thumb entry address, or interior address,
  including in an unaligned byte-granular scan.

There is therefore no callback table, vector, jump table, hidden alternate
entry, or interior ownership that must move with the function.

## Isolated candidate

The candidate retains the upstream two-step local-result algorithm and the
MIT notice. Its only G2 adaptation names the authenticated stock
`pxCurrentTCB` word through
`OPEN_CFW_FREERTOS_TASK_CURRENT_TCB`. Tests override that macro with a host
word; the freestanding Arm build uses `0x20074A20`.

With the core overlay's Cortex-M flags at `-O2`, Clang emits:

```text
00000000  movw    r0, #0x4A20
00000004  movt    r0, #0x2007
00000008  ldr     r0, [r0]
0000000A  bx      lr
```

The target bytes are:

```text
44f62020c2f2070000687047
```

The emitted function is 12 bytes with SHA-256
`1f544f3f3ad352dc5493c0588030e18636a6705a67aea031264ab89c98a3ee0b`.
It has no relocation, undefined symbol, data section, callee, or second
function. It is four bytes larger than stock because it materializes the
absolute RAM address locally instead of sharing IAR's distant literal pool;
that size difference does not change behavior or ABI.

## Focused validation

`tests/test_runtime_freertos_task_current.py` contributes eight tests that:

- authenticate the official image and vendored V10.5.1 snapshot;
- pin the complete stock body, neighbors, literal address, and RAM word;
- host-execute null, ordinary, 32-bit-edge, and 64-bit sentinel handles,
  proving the TCB is not dereferenced;
- pin the target symbol, bytes, SHA-256, lack of relocations, and lack of
  undefined symbols;
- scan the complete official application for wide and narrow branch topology;
- scan every byte for stored entry and interior pointers.

The focused suite passes:

```text
Ran 8 tests

OK
```

## Recommended integration contract

A later aggregate integration should:

1. register only
   `open_cfw_freertos_task_get_current_task_handle` as the new source;
2. redirect the complete eight-byte stock span
   `[0x0045589C,0x004558A4)` with the established `B.W` plus NOP policy;
3. retain absolute `pxCurrentTCB` word `0x20074A20` until kernel RAM globals
   are migrated atomically;
4. preserve all seven existing caller instructions;
5. rerun aggregate relocation drift, package ownership, reproducibility, and
   full-regression gates before claiming source ownership.

## Ranked follow-ups

1. `xTaskGetSchedulerState` at `[0x004558A4,0x004558C4)` is the next strongest
   released-source leaf. Its instructions exactly implement the V10.5.1
   three-state return policy, but it owns two stock global seams rather than
   one.
2. The retained private queue creation and mutex-initialization helpers are
   identifiable V10.5.1 code, but they include allocator, list, trace, and
   queue-layout dependencies and should be recovered as a cluster.
3. `pcTaskGetName` is source-identifiable, but it crosses the vendor-extended
   TCB ABI and should follow a focused TCB/name-offset audit.
4. Cortex-M55 port functions are source-correlated but remain port- and
   interrupt-policy boundaries, so they are less suitable than generic kernel
   leaves for the next atomic increment.
