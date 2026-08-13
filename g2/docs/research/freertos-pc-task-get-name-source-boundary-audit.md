# G2 FreeRTOS task-name source-boundary audit

Status: production-integrated bounded source replacement
Scope: official G2 package `2.2.6.10`, Apollo-main application; offline
analysis, host/target compilation, component assembly, and package
reconstruction only, with no signing, flashing, or hardware access

## Subsequent production status

`pcTaskGetName` is now production-integrated and its mask-provider dependency
is source-owned. Production source-assembles the exact MIT-licensed
FreeRTOS-Kernel V10.5.1 pair from the sectionized Clang-syntax adaptation
`runtime_freertos_interrupt_mask.S` (SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`).
The fixed pair occupies `[0x005FA0A4,0x005FA0BA)` with SHA-256
`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`
and `[0x005FA0BA,0x005FA0C8)` with SHA-256
`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`.
The current Apple copies occupy `[0x007AFF08,0x007AFF1E)` and
`[0x007AFF1E,0x007AFF2C)`; exact-root Linux uses
`[0x007B054C,0x007B0562)` and `[0x007B0562,0x007B0570)`. The current getter
occupies `[0x007B0030,0x007B0056)` on Apple and
`[0x007B0650,0x007B0676)` on Linux, with its relocation bound directly to the
profile's source-owned `ulSetInterruptMask`. The older candidate sequencing
below is retained as historical audit evidence.

## Result

`pcTaskGetName` is an unequivocal FreeRTOS-Kernel V10.5.1 source boundary:

| Property | Recovered value |
|---|---|
| Official entry | `0x00454F16` |
| End-exclusive range | `[0x00454F16,0x00454F38)` |
| Size | 34 bytes |
| SHA-256 | `a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817` |
| Upstream source | `third_party/freertos-kernel/tasks.c`, `pcTaskGetName` |
| Direct callers | one `BL` at `0x0044AAEE` |
| External entry/interior branches | none |
| Stored entry/interior pointers | none; one classified unaligned false positive |
| Outgoing call | `ulSetInterruptMask` at `0x005FA0A4`, assertion path only |
| Stock global seam | `pxCurrentTCB` word at `0x20074A20` |
| TCB field seam | `pcTaskName[0]` at `+0x34` |
| Name extent | 32 bytes, `+0x34...+0x53` |
| G2 extension | stack-depth word at `+0x54`, after the complete name |

The official algorithm is exactly the released V10.5.1 implementation:

1. use the caller-supplied TCB when the handle is non-NULL;
2. otherwise load `pxCurrentTCB`;
3. assert that the selected TCB is non-NULL;
4. return its address plus `0x34`.

The G2 vendor stack-depth extension does **not** affect this getter. It begins
at `+0x54`, immediately after the complete 32-byte task name. It remains a
required compatibility patch for a fully linked G2 `TCB_t`, because it shifts
all later trace, mutex, notification, and provenance fields relative to an
unmodified configuration. The getter itself neither reads nor crosses that
extension.

The historical isolated candidate is
`research/candidates/freertos_pc_task_get_name.c`. Production uses the
reviewed single-section adaptation
`components/apollo_main/core_overlay/runtime_freertos_pc_task_get_name.c`,
whose only retained relocation binds directly to source-owned
`ulSetInterruptMask`.

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

## Exact stock boundary

The complete official body is:

```text
00454F16  push    {r7, lr}
00454F18  cmp     r0, #0
00454F1A  bne     0x00454F22
00454F1C  ldr     r0, [pc, #0x284] ; literal at 0x004551A4
00454F1E  ldr     r0, [r0]         ; pxCurrentTCB at 0x20074A20
00454F20  b       0x00454F22
00454F22  cmp     r0, #0
00454F24  bne     0x00454F34
00454F26  bl      0x005FA0A4       ; ulSetInterruptMask
00454F2A  movs    r0, #0
00454F2C  movs.w  r1, #-1
00454F30  str     r0, [r1]         ; configured fail-stop fault write
00454F32  b       0x00454F32
00454F34  adds    r0, #0x34
00454F36  pop     {r1, pc}
```

The exact bytes are:

```text
80b5002802d1a1480068ffe7002806d1
a5f1bdf800205ff0ff310860fee7343002bd
```

The neighboring ownership is independently bounded:

| Range | Content | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x00454F10,0x00454F16)` | preceding `uxTaskGetNumberOfTasks` | 6 | `43e18c3d205509129b075a8eb8c2c70afde30da1b933ac72d2963813aea8cfec` |
| `[0x00454F16,0x00454F38)` | complete `pcTaskGetName` | 34 | `a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817` |
| `[0x00454F38,0x00454F44)` | first 12 bytes of following function | 12 | `29d9d5a1c65067aa3d10780636da13d31b3fe14eb136d506df195690a0fb497e` |

There is no fall-through from either neighbor. The selected range owns its
return and all of its assertion loop.

## One-to-one upstream comparison

Pristine V10.5.1 defines handle selection as:

```c
#define prvGetTCBFromHandle( pxHandle ) \
    ( ( ( pxHandle ) == NULL ) ? pxCurrentTCB : ( pxHandle ) )
```

Its complete public getter is:

```c
char * pcTaskGetName( TaskHandle_t xTaskToQuery )
{
    TCB_t * pxTCB;

    pxTCB = prvGetTCBFromHandle( xTaskToQuery );
    configASSERT( pxTCB );
    return &( pxTCB->pcTaskName[ 0 ] );
}
```

Every stock instruction has a released-source role:

| Stock operation | V10.5.1 source role |
|---|---|
| NULL test and `pxCurrentTCB` load | `prvGetTCBFromHandle` |
| second NULL test | `configASSERT(pxTCB)` |
| mask call, invalid write, loop | recovered G2 `configASSERT` fail-stop |
| `adds r0,#0x34` | address of `pcTaskName[0]` |
| return | public `char *` result |

There is no private algorithm to recreate. The only G2 adaptations are fixed
global placement, TCB layout, and assertion binding.

## TCB and configuration implications

The recovered G2 TCB is 112 bytes (`0x70`). The prefix required by this
function is:

| Offset | Field | Size |
|---:|---|---:|
| `+0x00` | top-of-stack pointer | 4 |
| `+0x04` | state `ListItem_t` | 20 |
| `+0x18` | event `ListItem_t` | 20 |
| `+0x2C` | current priority | 4 |
| `+0x30` | stack-base pointer | 4 |
| `+0x34` | `pcTaskName[32]` | 32 |
| `+0x54` | G2 stack-depth word | 4 |

The `+0x34` name offset follows from independently recovered choices:

- 32-bit pointers and `UBaseType_t`;
- no MPU wrapper state in the TCB prefix;
- two 20-byte V10.5.1 `ListItem_t` objects;
- `configMAX_TASK_NAME_LEN=32`.

Trace, mutex, application-tag, TLS, runtime-stat, notification, and allocation
configuration fields occur after the task name and cannot change this
getter's offset.

The official task initializer at `[0x00454976,0x0045499E)` has SHA-256
`f59595f8a0b62d16cbeedde20fca564d9d2687162a2a2bd9208197c382960c10`.
It:

1. stores incoming stack depth at `[TCB + 0x54]`;
2. bounds the name-copy loop at `0x20`;
3. stores each byte at `[TCB + index + 0x34]`;
4. forces the final byte at `[TCB + 0x53]` to zero.

This positively proves both the field extent and extension order. It is not
an inference from the getter's final add alone.

Pristine V10.5.1 has no stack-depth field at `+0x54`.
`configRECORD_STACK_HIGH_ADDRESS=1` would place `pxEndOfStack` there instead,
which is incompatible with G2. The full-kernel port therefore still requires
`configRECORD_STACK_HIGH_ADDRESS=0` plus the explicit G2 stack-depth extension.
The isolated candidate stops its structural model at `0x54`, so later fields
cannot be accidentally shifted or assumed.

## Global and assertion seams

The PC-relative literal at `0x004551A4` contains `0x20074A20`. That is the
same `pxCurrentTCB` word already authenticated by the integrated
`xTaskGetCurrentTaskHandle` boundary.

The assertion call targets `[0x005FA0A4,0x005FA0BA)`, a 22-byte
`ulSetInterruptMask` leaf with SHA-256
`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`.
It:

1. reads `BASEPRI`;
2. installs recovered mask `0x30`;
3. executes DSB and ISB;
4. returns the previous mask.

`pcTaskGetName` discards that return value, writes zero through address
`0xFFFFFFFF`, and loops. This matches the configured G2 fail-stop assertion
policy seen throughout the kernel.

The getter does not otherwise access a port function, scheduler list, critical
section, heap, trace hook, libc helper, or later TCB field.

## Caller and reference topology

The complete installed application was scanned at every halfword for Thumb
`BL`, `B.W`, narrow unconditional/conditional branches, `CBZ`, and `CBNZ`.
Every byte offset was also scanned for possible even or odd/Thumb stored
addresses.

The only direct call is:

| Call site | Encoding | Context |
|---|---|---|
| `0x0044AAEE` | `0af012fa` | EasyLogger current-thread/process-name helper |

The SHA-256 of that caller address encoded as one little-endian 32-bit word
is
`6b6b656546449e21e970d725927d278f881d1c0bf448fd732bf3759f73366ee4`.

The caller helper at `[0x0044AAE0,0x0044AAF8)`:

1. calls `xTaskGetSchedulerState`;
2. returns literal `"unknown"` when the scheduler is not started;
3. otherwise calls `xTaskGetCurrentTaskHandle`;
4. passes that result to `pcTaskGetName`.

Both EasyLogger process and thread wrappers at `0x0044AB14` and `0x0044AB1C`
call that common helper. Thus the one stock call site has two application
consumers, but neither stores or passes the getter as a callback.

The scan finds:

- one direct `BL` to the entry;
- no wide or narrow jump to the entry;
- no external wide or narrow branch into the interior;
- no stored entry pointer;
- no stored odd/Thumb entry or interior pointer.

A naive byte-granular scan reports one possible even interior value:

| Byte address | Apparent value |
|---:|---:|
| `0x004A56B7` | `0x00454F20` |

It is not a stored code pointer. The containing aligned 12-byte literal pool
is:

```text
4c450020 4e450020 4f450020
```

Those are aligned SRAM values `0x2000454C`, `0x2000454E`, and `0x2000454F`.
Reading from the odd byte offset `0x004A56B7` merely overlaps the latter two
values. No aligned load or branch references it as a code address.

## Isolated target candidate

The candidate retains the upstream MIT notice and algorithm. Its bounded
prefix type has compile-time checks for:

- `task_name` offset `0x34`;
- prefix size `0x54`.

Using the production overlay's freestanding target flags with Clang `-O2`,
the public candidate is 22 bytes:

```text
00000000  cbnz    r0, 0x0000000E
00000002  movw    r0, #0x4A20
00000006  movt    r0, #0x2007
0000000A  ldr     r0, [r0]
0000000C  cbz     r0, 0x00000012
0000000E  adds    r0, #0x34
00000010  bx      lr
00000012  bl      assertion helper
```

Its exact bytes are:

```text
28b944f62020c2f20700006808b13430704700f001f8
```

The function SHA-256 is
`b25b4e6b432db1958db52b71a623c5a0b1b71bf119497b4e0f96fab118602d14`.

The complete `.text` is 38 bytes: the 22-byte public function, a two-byte
alignment NOP, and a 14-byte local fail-stop helper. Its SHA-256 is
`fb4c24b6071973df5bdae74251b5fc8b2fe1ccef8d065188398b7b8c8761540d`.
It has:

- one global public function;
- one local assertion helper;
- no data section;
- one undefined symbol, `ulSetInterruptMask`;
- exactly one `R_ARM_THM_CALL` relocation at text offset `0x18`.

Candidate source SHA-256 is
`cd80886bfec8eb99df0a07ca721685f387a44c079c1da8139fa944e99ff8a278`;
host fixture SHA-256 is
`31f0d146f5d49b39d00dc73cf40b32e3fc798739e9908f8ee54f24f5f4d7cf8c`.

The candidate is shorter than stock because Clang uses `CBZ`/`CBNZ`, locally
materializes the fixed SRAM address, and places the fail-stop in a shared
local helper. This changes neither the callable AAPCS contract nor observable
valid-input behavior.

## Focused validation

`tests/test_freertos_pc_task_get_name_candidate.py` contributes eight tests
that:

- authenticate the official package and vendored V10.5.1 snapshot;
- pin the complete stock body, neighbors, literal, and port dependency;
- pin the independent name writer, terminator, and G2 extension ordering;
- scan the complete image for wide, narrow, stored, and interior references;
- classify the sole byte-overlap false positive;
- host-execute explicit-handle and NULL/current-handle behavior;
- prove the returned pointer is exactly 52 bytes into the TCB;
- target-compile and pin both functions, text, symbol sizes, undefined seam,
  and relocation.

The focused suite passes:

```text
Ran 8 tests in 3.996s

OK
```

Run it with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  openCFW/tests/test_freertos_pc_task_get_name_candidate.py
```

## Historical first-production result and current placement

The admitted 3,489-byte source has SHA-256
`d46408b0bdce9622ac1fa8c694ccc790c76169b681d0c413a4ada35fbe29d21a`.
Under the reviewed Clang profile it emits one 38-byte, four-byte-aligned
function section with raw SHA-256
`b680e949844cca19a586fbe865837f8180e592434ac1517b29ceb1482c9dd3b6`.
Its complete relocation allowlist is one `R_ARM_THM_CALL` at `+0x14` to
source-owned `ulSetInterruptMask`.

In the original task-name promotion, the leaf occupied
`[0x007B0280,0x007B02A6)` and had SHA-256
`88edbdea558812d213013a8d319a09c63dafa86ec91a7640f427c72c77552da1`.
The generated `B.W` plus NOP replacement covers the complete official span
`[0x00454F16,0x00454F38)` and has SHA-256
`bab8b15cc5c97baa2336a66e065fd3c653e116d106a278a0cae74e172f83c0ee`.
The sole caller remains unchanged.

At that historical point, the Apollo-main overlay was 114,562 bytes with
SHA-256
`188a9b26fce7b7899e3c0eebd698552edc6a453396b9b05107841c63d488e8ee`.
Its 3,637,958-byte provider has SHA-256
`6830ed33f567b4ac8b4c401612b83b56caa38d107bb9b1fc5d210dce9add9214`.
The complete 4,416,140-byte package has SHA-256
`624e18cea8e36c954809f2d36b8b539275e7fa8ba9f305a166ed9e83b7a86d43`.
Its 554,360-byte flash plan has SHA-256
`4b1ce318c286cb7a0a83c144b149c61581ca658080c229bd7474cf84ed472b35`
and contains 768 placed, two unresolved, five container-only, and six
protected regions.

Those initial aggregate pins have been superseded by later source promotions;
the live placements are recorded in "Subsequent production status" above.
The dedicated production gate in
`tests/test_runtime_freertos_pc_task_get_name.py` passes 7/7 tests. It pins
upstream/source identity, stock boundaries and reference topology, the G2
TCB/name layout, host semantics, target section and relocation closure,
production placement/redirect/accounting, and reconstructable manifest
regions.

For a future fully linked FreeRTOS kernel, the broader G2 TCB patch remains
mandatory: keep `configRECORD_STACK_HIGH_ADDRESS=0`, add the stack-depth word
at `+0x54`, and assert all later recovered offsets and total size `0x70`.
