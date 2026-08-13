# G2 FreeRTOS queue-wrapper tranche source-boundary audit

Status: audited upstream-source candidates; not registered by the
Apollo-main production overlay  
Scope: Apollo-main application from official G2 package `2.2.6.10`;
offline disassembly, authenticated-source comparison, and current
source-ownership review only

## Subsequent production status

The candidate/ranking language below describes an earlier milestone. These
wrappers are now production source, and their assertion calls retain the
fixed address of a byte-exact, source-assembled MIT FreeRTOS-Kernel V10.5.1
mask leaf. The sectionized Clang-syntax pair source
`runtime_freertos_interrupt_mask.S` has SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`.
Its fixed copies are `[0x005FA0A4,0x005FA0BA)`
(`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`)
and `[0x005FA0BA,0x005FA0C8)`
(`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`);
isolated copies are appended at `[0x007B00D8,0x007B00EE)` and
`[0x007B00EE,0x007B00FC)`.

## Result

The next three queue-creation wrappers are unequivocally the released
FreeRTOS-Kernel V10.5.1 `queue.c` implementations:

| Function | Official end-exclusive range | Bytes | SHA-256 |
|---|---|---:|---|
| `xQueueCreateMutexStatic` | `[0x004416F0,0x00441710)` | 32 | `2977000da7aab5b87abce1270dca6518785de04a1e72d08082802713d478fd28` |
| `xQueueCreateCountingSemaphoreStatic` | `[0x00441790,0x004417C2)` | 50 | `a46100f23dd51b8276a4c2ebafa1ba96c6813114810ae0f5297764c20368eb62` |
| `xQueueCreateCountingSemaphore` | `[0x004417C2,0x004417EE)` | 44 | `ed30ebca04b655b1ec31e60296d977382d0712057db88f99b205a555b374120f` |

Their ordered, noncontiguous concatenation is 126 bytes with SHA-256
`1d305cd5e6313c35b3489f26b310b4161252543b882bc6c62e9c55d567523460`.

All queue-side calls close over functions already owned by source:

- `xQueueCreateMutexStatic` calls the source-owned static generic creator and
  mutex initializer;
- the static counting wrapper calls the source-owned static generic creator;
  and
- the dynamic counting wrapper calls the source-owned dynamic generic
  creator.

The mutex wrapper adds no fixed executable seam of its own. The two counting
wrappers retain one non-queue dependency: invalid dimensions call the
reviewed `configASSERT` fail-stop port entry at `0x005FA0A4`. This is the
same explicit assertion seam already used by the source-owned generic
creators. Therefore the **queue closure is complete**, while the broader
port/assertion closure is intentionally not.

No unknown ABI, configuration, caller, or reference fact blocks a bounded
source implementation. The ranked promotion sequence is:

1. promote `xQueueCreateMutexStatic` alone as the smallest zero-new-seam
   increment;
2. promote both counting-semaphore wrappers together as one 94-byte semantic
   unit, retaining the reviewed assertion seam; or
3. promote all three in one 126-byte tranche if a single package rebuild is
   preferred.

The counting pair should not be split without a specific size or scheduling
reason: they share the same validation rule, queue type, zero-item ABI,
`Queue_t` count-field write, trace-hook configuration, and assertion
behavior.

## Reproducible analyzer

The read-only analyzer is:

```sh
python3 tools/analyze_g2_freertos_queue_wrapper_tranche.py
python3 tools/analyze_g2_freertos_queue_wrapper_tranche.py --json
```

It authenticates both official and upstream inputs, verifies exact bodies
and neighboring boundaries, decodes outgoing calls, scans the complete
installed application for wide and narrow Thumb references and stored
pointers, and checks the current Apollo-main redirect ownership for all
three queue dependencies. It has no device, serial, signing, or flashing
path.

Focused regression coverage is:

```sh
python3 -m unittest \
  tests.test_analyze_g2_freertos_queue_wrapper_tranche
```

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
| Upstream file | `third_party/freertos-kernel/queue.c` |
| Version | `V10.5.1` |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| `queue.c` bytes | `125,614` |
| `queue.c` SHA-256 | `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` |
| `queue.c` Git blob | `5c872e0302839d96aab90919788fdc2b0be1c09e` |
| License | MIT |

The analyzer also isolates and pins the three complete source function
blocks:

| Function | Source-block bytes | Source-block SHA-256 |
|---|---:|---|
| `xQueueCreateMutexStatic` | 643 | `790cfc1e7f21e0f961b35020ea6f47ce0d9d147b2370be4c1620787b2a3d4c0f` |
| `xQueueCreateCountingSemaphoreStatic` | 1,024 | `47ec21550eaab3b4f847f2e803ec67fd8804bacb02cfdeb3d2e0fc0421c94f36` |
| `xQueueCreateCountingSemaphore` | 898 | `c20b22c99a49745040aa25673f39b1eee8831b790011b8ae18f47fce674e1802` |

The entire upstream file is authenticated first. The source-block digests
then make the exact released algorithms used by this audit independently
reviewable.

## Exact boundary proof

The function immediately before the static mutex wrapper is the already
source-owned dynamic mutex creator:

| Range | Bytes | SHA-256 |
|---|---:|---|
| `[0x004416D6,0x004416F0)` | 26 | `fd3801ca9d39f700a0c4dc5598707c4dd9c6efd75ec8c25d432e7ef29c15eddf` |

It ends with `pop {r4,pc}` at `0x004416EE`. The static mutex wrapper starts
with its own `push {r2,r3,r4,lr}` at `0x004416F0` and ends with
`pop {r1,r2,r4,pc}` at `0x0044170E`.

Two complete recursive-mutex functions occupy the intentional interval
between the static mutex and static counting wrappers:

| Range | Role | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00441710,0x00441750)` | recursive mutex give | 64 | `ba48b7e573af0899510fa67e97d7127b06f55015f5aeb951fb834f94d44ec1c9` |
| `[0x00441750,0x00441790)` | recursive mutex take | 64 | `08842b983b428e0e38c484385f62d27b6c50719ce1028019a36c343b4ccdc726` |

The static counting wrapper begins at `0x00441790` with its own
`push {r2,r3,r4,lr}`. Its valid return is at `0x004417B2`; its active
assertion path ends in a local fail-stop loop at `0x004417C0`. The dynamic
counting wrapper begins immediately at `0x004417C2` with
`push {r4,lr}` and has the corresponding local fail-stop loop at
`0x004417EC`.

The next complete public function, `xQueueGenericSend`, starts at
`0x004417EE`. Its first 34 bytes through `0x00441810` have SHA-256
`ea3a9434f23c3dadb07815859e3ebe84fe83b99e51c40f64d9832729e8a819b5`.
No wrapper shares a literal pool, instruction, or alignment byte with a
neighbor.

## Released-source behavior and ABI

### `xQueueCreateMutexStatic`

The public AAPCS32 Thumb ABI is:

| Register | Value |
|---|---|
| `r0` | eight-bit mutex queue type; only the low byte is significant |
| `r1` | caller-owned `StaticQueue_t *` |
| return `r0` | queue handle or null |

The official body:

1. normalizes the type with `UXTB`;
2. calls `xQueueGenericCreateStatic(1, 0, NULL, pxStaticQueue, type)`;
3. passes the result to `prvInitialiseMutex`; and
4. returns that handle unchanged.

This exactly matches V10.5.1. The wrapper itself does not validate the
static buffer; the generic static creator performs the released assertions.
Both ordinary mutex type `1` and recursive mutex type `4` are observed in
official callers.

### `xQueueCreateCountingSemaphoreStatic`

The public ABI is:

| Register | Value |
|---|---|
| `r0` | 32-bit unsigned maximum count |
| `r1` | 32-bit unsigned initial count |
| `r2` | caller-owned `StaticQueue_t *` |
| return `r0` | queue handle or null |

The official body:

1. requires `maximum != 0`;
2. requires `initial <= maximum` using an unsigned comparison;
3. calls
   `xQueueGenericCreateStatic(maximum, 0, NULL, buffer, 2)`;
4. writes the initial count at handle offset `+0x38` if creation succeeds;
   and
5. returns the handle.

Invalid dimensions call `0x005FA0A4`, write zero through `0xFFFFFFFF`, and
loop. A null buffer reaches the generic creator's own released assertion
path. There is no trace-hook call in the official body.

### `xQueueCreateCountingSemaphore`

The public ABI is:

| Register | Value |
|---|---|
| `r0` | 32-bit unsigned maximum count |
| `r1` | 32-bit unsigned initial count |
| return `r0` | queue handle or null |

The official body applies the same unsigned validation, calls
`xQueueGenericCreate(maximum, 0, 2)`, writes the initial count at `+0x38`
on success, and returns the handle. Ordinary dynamic allocation failure
returns null without asserting or dereferencing it. Invalid dimensions use
the same active fail-stop path as the static wrapper.

## Configuration and object ABI closed by disassembly

| Property | Recovered value | Evidence |
|---|---:|---|
| `configUSE_MUTEXES` | `1` | public static mutex wrapper retained |
| `configUSE_COUNTING_SEMAPHORES` | `1` | both counting wrappers retained |
| `configSUPPORT_STATIC_ALLOCATION` | `1` | static mutex and counting wrappers |
| `configSUPPORT_DYNAMIC_ALLOCATION` | `1` | dynamic counting wrapper |
| `configASSERT` | enabled | both invalid-count paths call the fail-stop port entry |
| `configUSE_TRACE_FACILITY` | `1` | already recovered 80-byte `Queue_t` trace fields |
| counting creation hooks | empty | no hook call or side effect at released hook sites |
| `mtCOVERAGE_TEST_MARKER()` | empty | invalid paths contain only assert fail-stop |
| `queueSEMAPHORE_QUEUE_ITEM_LENGTH` | `0` | both generic calls pass item size zero |
| `queueQUEUE_TYPE_COUNTING_SEMAPHORE` | `2` | both generic calls pass queue type two |
| `Queue_t.uxMessagesWaiting` | `+0x38` | both successful counting paths store there |
| `StaticQueue_t` | `0x50` bytes | static creator ABI and CMSIS caller checks |
| pointer / `UBaseType_t` | 32 bits | register ABI, offsets, and unsigned comparisons |

The wrappers neither add nor modify the queue object layout. They reuse the
exact 80-byte ABI established by the generic-creation integration.

## Outgoing dependency closure

The complete outgoing-call inventory is:

| Wrapper call site | Target | Current ownership |
|---:|---:|---|
| `0x00441700` | `xQueueGenericCreateStatic` at `0x004415CA` | source-owned |
| `0x00441708` | `prvInitialiseMutex` at `0x004416B8` | source-owned |
| `0x004417A8` | `xQueueGenericCreateStatic` at `0x004415CA` | source-owned |
| `0x004417B4` | assertion fail-stop at `0x005FA0A4` | retained reviewed port seam |
| `0x004417D4` | `xQueueGenericCreate` at `0x00441636` | source-owned |
| `0x004417E0` | assertion fail-stop at `0x005FA0A4` | retained reviewed port seam |

The production overlay currently registers `B.W` redirects for all three
queue targets:

- `open_cfw_freertos_queue_generic_create_static`;
- `open_cfw_freertos_queue_generic_create`; and
- `open_cfw_freertos_queue_initialise_mutex`.

A production implementation should link wrapper-to-creator/initializer
calls directly by source symbol. It should not emit a
source-to-stock-redirect-to-source hop. The fixed assertion entry can remain
the same explicit compatibility seam until the port/assertion project is
promoted.

## Whole-image caller and reference topology

The complete installed application was scanned:

- at every halfword for Thumb `BL` and `B.W`;
- at every halfword for narrow unconditional and conditional branches plus
  `CBZ`/`CBNZ`; and
- at every byte for little-endian even or odd/Thumb entry and interior
  pointers.

| Function | Direct `BL` callers | `B.W` callers | External interior branches | Stored entry/interior pointers |
|---|---:|---:|---:|---:|
| `xQueueCreateMutexStatic` | 3 | 0 | 0 | 0 |
| `xQueueCreateCountingSemaphoreStatic` | 2 | 0 | 0 | 0 |
| `xQueueCreateCountingSemaphore` | 1 | 0 | 0 | 0 |

### Static mutex wrapper callers

| Call site | Encoding | Recovered role |
|---:|---|---|
| `0x0043C7DE` | `04f087ff` | private lazy static recursive-mutex initializer |
| `0x00449778` | `f7f7baff` | CMSIS-RTOS2 `osMutexNew`, static recursive-mutex path |
| `0x00449784` | `f7f7b4ff` | CMSIS-RTOS2 `osMutexNew`, static ordinary-mutex path |

The packed caller-address digest is
`18956e929d4db6cfb12a062fedc6d04916549fe51dcca21ff4aca45ba1c72784`.

The private lazy initializer is exactly
`[0x0043C7CC,0x0043C7FA)` (46 bytes, SHA-256
`07dec9d3df52f103cf3cee74011d23364e87a095f4bbbfbe797e3e6b7bedac6f`).
It creates type `4` into the static buffer at `0x20072998`, publishes the
handle through `0x20074388`, and asserts if creation did not succeed.

The complete CMSIS mutex creator is
`[0x0044971C,0x004497B6)` (154 bytes, SHA-256
`09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec`).
Its other two creation branches call the source-owned dynamic mutex wrapper.

### Counting-wrapper callers

| Call site | Encoding | Recovered role |
|---:|---|---|
| `0x00449938` | `f7f72aff` | CMSIS-RTOS2 `osSemaphoreNew`, static branch |
| `0x00449CCA` | `f7f761fd` | CMSIS-RTOS2 `osMemoryPoolNew`, static availability semaphore |
| `0x00449944` | `f7f73dff` | CMSIS-RTOS2 `osSemaphoreNew`, dynamic branch |

The static wrapper caller-list digest is
`5002b370782bf8b3f503055d7c11af7630622fe21b3858cd9cbe74b42f9d2873`.
The dynamic wrapper caller-list digest is
`2a96b89cb1e27e8aa093eafe45e2990e706084ea8d179689b1c61c66ed925bad`.

The complete CMSIS semaphore creator is
`[0x0044989A,0x0044994E)` (180 bytes, SHA-256
`ebdcf69b866e35e468ba9ce84d7e7ac9b58377b5ffcc439762d729f7d99a098c`).
The memory-pool creator is
`[0x00449C14,0x00449D3E)` (298 bytes, SHA-256
`c108de1748627d51427e2771a74fe9b3ddcd5b53c5816ebb2f82972e8bdc6136`).
It uses the static counting semaphore as its block-availability count with
both maximum and initial count equal to the pool's block count.

The absence of exterior interior branches and stored pointers means each
complete wrapper entry can use the established whole-function `B.W` redirect
policy without preserving an official interior entry.

## Source-integration design

Use bounded adaptations of the authenticated V10.5.1 functions rather than
decompilation-derived rewrites. A production increment should:

1. reuse the existing project-prefixed 80-byte queue-control view;
2. link directly to the three current source-owned creator/initializer
   symbols;
3. preserve the exact public AAPCS32 parameter widths and return behavior;
4. retain `type & 0xFF` behavior for the static mutex wrapper;
5. use an unsigned `initial <= maximum` comparison;
6. write the count only after a non-null creation result;
7. retain the fixed `0x005FA0A5` Thumb assertion call until that port seam is
   source-owned;
8. keep trace and coverage hooks configuration-controlled and empty for the
   recovered G2 configuration; and
9. redirect only the complete official spans listed above.

At integration time, add a host behavior oracle for successful creation,
creator failure, invalid dimensions, boundary values, and mutex type
forwarding. Then run target compilation, relocation review, aggregate
ownership, offline package inspection, reproducibility, and full regression
gates.

Do not compile pristine `queue.c` wholesale merely to obtain these wrappers.
The complete translation unit still spans unrelated scheduler, port, and
configuration surfaces. The authenticated released algorithms are certain;
the bounded build boundary remains the appropriate production unit.

## Ranked atomic integration recommendation

1. **`xQueueCreateMutexStatic` (32 bytes).** This is the strongest immediate
   promotion. Every outgoing call is already source-owned, it has no direct
   assertion or allocator seam, and all three complete callers target only
   its public entry.
2. **Both counting wrappers together (94 bytes).** Integrate static and
   dynamic variants atomically. They close over current source-owned queue
   creators and differ only in buffer/allocation provenance. Retain the
   already audited assertion entry for invalid dimensions.
3. **All three wrappers together (126 bytes).** This is equally defensible
   when minimizing build/release cycles matters more than the smallest
   reviewable change. It still adds no new unknown seam.
4. **Source-own the assertion port entry separately.** This is not a blocker
   for the wrapper tranche, but it is the next step required to make the
   counting pair close entirely over source-generated executable code rather
   than one reviewed official port function.
5. **Continue into `xQueueGenericReset` only as a separate audit.** That
   function has critical-section and event-list behavior and should not be
   conflated with these trivial public wrappers.

## Limitations

This audit is offline and static. No device was connected, and no serial,
debugger, signing, flashing, or runtime claim was attempted. Public names
come from exact released-source behavior and the established CMSIS-RTOS2
call contexts. The private caller at `0x0043C7CC` is intentionally named by
its observable lazy-initialization role rather than assigned a speculative
application subsystem name.
