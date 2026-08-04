# FreeRTOS scheduler-port trio source-boundary audit

Status: authenticated source implementation; promoted by the subsequent
FreeRTOS scheduler-cluster production tranche

Scope: official G2 package `2.2.6.10`, Apollo-main only; offline source,
host-behavior, target-object, and whole-image topology verification; no
firmware assembly, signing, flashing, or hardware writes

## Result

The contiguous Apollo-main scheduler-port trio is an unequivocal match for
the released FreeRTOS-Kernel V10.5.1
`portable/IAR/ARM_CM55_NTZ/non_secure/port.c` implementation:

| Official range | Bytes | Released function | Complete behavior |
|---|---:|---|---|
| `[0x004420BC,0x004420D0)` | 20 | `vPortYield` | write PendSV-set to ICSR, `DSB`, `ISB`, return, then 2-byte alignment |
| `[0x004420D0,0x004420E8)` | 24 | `vPortEnterCritical` | set BASEPRI, increment global nesting, `DSB`, `ISB` |
| `[0x004420E8,0x00442114)` | 44 | `vPortExitCritical` | assert nonzero depth, decrement, clear BASEPRI only at depth zero |

The exact recovered seams are:

- Arm System Control Block ICSR at `0xE000ED04`;
- PendSV-set bit `0x10000000` (`1U << 28`);
- the volatile 32-bit global `ulCriticalNesting` at `0x2000309C`;
- `portCRITICAL_NESTING_IN_TCB=0`;
- the authenticated `ulSetInterruptMask` entry at `0x005FA0A4`;
- the authenticated `vClearInterruptMask` entry at `0x005FA0BA`;
- shifted `configMAX_SYSCALL_INTERRUPT_PRIORITY=0x30` inside that assembly
  pair; and
- enabled fail-stop `configASSERT` behavior.

The project-prefixed implementation is retained in
[`research/candidates/freertos_scheduler_port_trio.c`](../../research/candidates/freertos_scheduler_port_trio.c)
with its interface in
[`freertos_scheduler_port_trio.h`](../../research/candidates/freertos_scheduler_port_trio.h).
Despite the historical `research/candidates` path, all three functions are now
named by `core_overlay/overlay.json`, source-assembled into Apollo-main, and
covered by the core-source manifest and aggregate production gates.

Current Apple placements are `vPortYield=0x007B0618`,
`vPortEnterCritical=0x007B0630`, and `vPortExitCritical=0x007B0650`.
The exact-root Linux placements are respectively `0x007B0D40`, `0x007B0D58`,
and `0x007B0D78`. Their mask relocations bind to the production source pair at
`0x007AFF08`/`0x007AFF1E` on Apple and `0x007B054C`/`0x007B0562` on Linux.

## Authoritative inputs

The reviewed firmware is:

| Property | Value |
|---|---|
| Package | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application bytes | `3,523,364` |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Application base | `0x00438000` |

The comparator is the authenticated FreeRTOS-Kernel V10.5.1 snapshot:

| Property | Value |
|---|---|
| Tag | `V10.5.1` |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| NTZ `port.c` bytes | `54,648` |
| NTZ `port.c` SHA-256 | `c2762e124d700d26ceb0dc737af706f361dd45c9e40bf683b916f1e430e37a08` |
| NTZ `port.c` Git blob | `349aeffb9c2fad0923fb736fa5b66c6611c5e8e4` |
| NTZ `portmacrocommon.h` bytes | `12,636` |
| NTZ `portmacrocommon.h` SHA-256 | `c184e6b1727732bbdd0d4dd33b9af4ea25d13040620666123941fff464bffc99` |
| NTZ `portmacrocommon.h` Git blob | `e68692a5addc314ddc595373c15631c03789faa8` |
| License | MIT, retained in the snapshot and candidate |

The snapshot verifier authenticates the release without network access:

```sh
python3 openCFW/third_party/freertos-kernel/verify_snapshot.py
```

## Exact official boundaries

The three complete official byte spans are:

```text
vPortYield
5ff0805056490860bff34f8fbff36f8f70470000

vPortEnterCritical
80b5b7f1e7ff4e480168491c0160bff34f8fbff36f8f01bd

vPortExitCritical
80b549490868002806d1b7f1d7ff00205ff0ff310860fee7
0868401e08600868002802d10020b7f1d4ff01bd
```

Their authentication pins are:

| Span | Size | SHA-256 |
|---|---:|---|
| `vPortYield` `[0x004420BC,0x004420D0)` | 20 | `dd981b3e9196c6fd87bb79719c94628c89e564d5728b3fdd1ff08c397eccb397` |
| `vPortEnterCritical` `[0x004420D0,0x004420E8)` | 24 | `5809638c22f928d2b32cd21cc9b92a292fad24cd8b8008de4ad92b9faeaba0d4` |
| `vPortExitCritical` `[0x004420E8,0x00442114)` | 44 | `bfd3ddb76c61ad634a3f58ed203260da3834895b646c9dffada546f9dc9d2a31` |
| complete trio `[0x004420BC,0x00442114)` | 88 | `ba9b86be2e0caa3b3bb32b45a7f1f4730fc94f6ad80153d470de5cb6e7a9b228` |

The neighboring functions close the entry boundaries:

| Span | Meaning | SHA-256 |
|---|---|---|
| `[0x004420A6,0x004420BC)` | complete `prvSetupFPU` predecessor | `59f9a18538c1aab61aefe1664793178c6c16cc5f1c4d79b3c8502ddda0b742c8` |
| `[0x00442114,0x00442134)` | complete `SysTick_Handler` successor | `2999c107f0c2c7a14aa1dffb07531b0b9389af39295a4ae606201faf02675a6f` |

There is no fall-through between these callable boundaries. The final
`0x0000` halfword in the yield range is alignment after its `BX LR`, not a
second entry or part of the released algorithm.

## Binary-to-source ordering proof

### `vPortYield`

The official function:

1. materializes `0x10000000`;
2. loads the ICSR address through the literal at `0x0044221C`;
3. performs one volatile word store to `0xE000ED04`;
4. executes `DSB SY`;
5. executes `ISB SY`; and
6. returns.

That is the released assignment
`portNVIC_INT_CTRL_REG = portNVIC_PENDSVSET_BIT` followed by its two explicit
architecture barriers. The same ICSR literal is reused by the adjacent
`SysTick_Handler`, which pends PendSV when `xTaskIncrementTick` requests a
switch.

### `vPortEnterCritical`

The official function:

1. calls `ulSetInterruptMask` at `0x005FA0A4`;
2. loads the nesting-word address from literal `0x00442210`;
3. performs one volatile read of the 32-bit word at `0x2000309C`;
4. performs a wrapping 32-bit increment and one volatile write;
5. executes `DSB SY`, then `ISB SY`; and
6. returns.

The called assembly leaf reads the old BASEPRI, writes `0x30` to BASEPRI,
then executes its own DSB/ISB pair. The C function intentionally ignores the
returned old mask, exactly as the released port does.

### `vPortExitCritical`

The official function preserves all released volatile evaluations and their
ordering:

1. read `ulCriticalNesting` for `configASSERT`;
2. if zero, call `ulSetInterruptMask`, write zero to `0xFFFFFFFF`, and loop;
3. otherwise read `ulCriticalNesting` again, subtract one, and write it;
4. read `ulCriticalNesting` a third time;
5. when that read is zero, pass zero to `vClearInterruptMask`; and
6. return.

The explicit rereads matter because the upstream object is volatile. The
candidate therefore does not collapse them into one cached local. The clear
leaf writes the supplied zero to BASEPRI and executes DSB/ISB, so interrupts
are restored only when the outermost critical section exits.

The two relevant literals are exact:

| Literal address | Word | Meaning |
|---|---:|---|
| `0x00442210` | `0x2000309C` | `ulCriticalNesting` |
| `0x0044221C` | `0xE000ED04` | System Control Block ICSR |

## Port dependency authentication

The outgoing mask dependency is the already authenticated released
Cortex-M55 assembly pair:

| Entry | Range | Size | Role |
|---|---|---:|---|
| `ulSetInterruptMask` | `[0x005FA0A4,0x005FA0BA)` | 22 | read BASEPRI, write `0x30`, DSB, ISB |
| `vClearInterruptMask` | `[0x005FA0BA,0x005FA0C8)` | 14 | restore supplied BASEPRI, DSB, ISB |

The concatenated pair SHA-256 is
`422a4cac7b1abe90c7c7b0c431e2d85ef4d733cffb2da3b2708311f183cce849`.
Official `BL` edges are exact at:

| Call site | Target |
|---:|---:|
| `0x004420D2` | `0x005FA0A4` |
| `0x004420F2` | `0x005FA0A4` |
| `0x0044210E` | `0x005FA0BA` |

The unlinked target-object fixture intentionally leaves these two symbols
unresolved so relocation closure can be tested. The production overlay resolves
them explicitly to the source-owned authenticated pair; no substitute mask
primitive is used.

## Configuration closure

The trio depends on the following recovered configuration and ABI choices:

| Choice | Recovered value | Evidence |
|---|---:|---|
| portable variant | `IAR/ARM_CM55_NTZ/non_secure` | authenticated wider context/SVC/PendSV shape |
| `configENABLE_MPU` | `0` | selected NTZ/non-MPU port shape |
| `portCRITICAL_NESTING_IN_TCB` | `0` | fixed global word, no TCB access |
| `configMAX_SYSCALL_INTERRUPT_PRIORITY` | shifted `0x30` | immediate in `ulSetInterruptMask` |
| `configASSERT` | enabled | complete zero-depth fail-stop path |
| port word / `uint32_t` | 4 bytes | word loads/stores and target static assertion |
| ICSR | `0xE000ED04` | literal plus store topology |
| PendSV set | bit 28 | exact immediate `0x10000000` |

`configENABLE_FPU=1` and the Apollo STIMER tick override are proven elsewhere,
but neither changes these three bodies. The source boundary does not claim the
neighboring FPU setup or SysTick handler.

## Whole-image control-flow topology

The entire 3,523,364-byte installed application was scanned at every
halfword for `BL`, `B.W`, narrow `B`, conditional `B`, `CBZ`, and `CBNZ`
targets.

| Entry | Direct `BL` callers | Caller-address SHA-256 | Address+encoding record SHA-256 |
|---|---:|---|---|
| `vPortYield` | 21 | `a3e06a6ce5af90723601814b9ab099b79ec4240fcfb185ae287630f5b2ab90a7` | `82bf0d7ac31cb2985e55ebbe5e31791d74e3c826be25da010fd121d281bd7001` |
| `vPortEnterCritical` | 45 | `65bc28cb458bf50bb2b30160bf661f686d8ce2d9fcdae800244ed901933f3993` | `8365ac4db9e8d5531c7791a7462440c5999ce30de0ef75c43e004233c3295792` |
| `vPortExitCritical` | 51 | `61250f3aa182674a0ee06462d2efaf5308511f36178f58561040dac2c1d5b631` | `605cbb784ec11f6d07fbf7e4f26d16d8b6c51263be5d10e88f46a76f81a0cafd` |

The focused test retains every caller address and authenticates the exact
four-byte encoding at each site. The scan found:

- no entry `B.W` edge for any of the three functions;
- no external wide or narrow branch into any interior halfword;
- no second function entry inside the three ranges; and
- only the expected internal branches in `vPortExitCritical`.

This is the closure used by the production entry redirects: the full official
caller topology reaches only the three public starts.

## Stored-pointer closure

A byte-granular 32-bit scan found no aligned stored even or Thumb entry
pointer for the trio and no aligned stored interior pointer.

It did find 20 deliberately retained false candidates. Every candidate:

- begins at an odd application address;
- decodes to the even word `0x004420F0`, the address of an internal exit
  conditional branch instruction; and
- crosses instruction/data bytes rather than occupying an aligned pointer
  slot.

The ordered false-candidate address SHA-256 is
`1b3d733ff9b6e796ce8d6e3006d7db32056b161eca81ca46692b6e04e9b224c1`;
the ordered `(location,value,canonical)` record SHA-256 is
`ce7c5d1626f4674601c631282988e55400d74fa286ead46cd2d573c4bd23ec4f`.
Classifying these matches prevents an absence claim from silently ignoring
the byte-granular scan results.

## Source implementation

The retained files are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `research/candidates/freertos_scheduler_port_trio.c` | 5,437 | `8fdefac8d8219c25b9a7a5424b6469b2882f9ae0331bfe33e69720b804a9a24e` |
| `research/candidates/freertos_scheduler_port_trio.h` | 814 | `8b5e6fb78ae1c3211e7bf0925ede8c04c1bc8d7dd2102a1b11814c545a40c0f4` |
| `tests/fixtures/freertos_scheduler_port_trio_candidate_host.c` | 5,363 | `e29a2dce133e12d75e13e72e53bf23368ad54df0466e765fa95531f648c52693` |

The candidate keeps the V10.5.1 MIT notice and released algorithms, but uses
project-prefixed entry names. Its seam macros have fixed target defaults and
host-test substitutions. The substitutions expose every volatile read,
volatile write, mask call, ICSR write, DSB, ISB, and assertion event without
weakening the target implementation.

The target source contains no writable data. The only unresolved code
dependencies are the authenticated mask-pair symbols.

## Apple and Linux target-object contract

Both reviewed toolchains use the Apollo overlay-compatible target and flags:

```text
--target=thumbv7em-none-eabi -mthumb -O2 -ffreestanding
-fno-jump-tables -fomit-frame-pointer -fno-builtin
-mno-unaligned-access -fno-unwind-tables
-fno-asynchronous-unwind-tables -fropi
-ffunction-sections -fdata-sections -Wall -Wextra -Werror
```

The reviewed compilers are Apple clang 21.0.0 and Homebrew clang 22.1.8.
They emit byte-identical function sections for this candidate:

| Candidate section | Size | Alignment | SHA-256 |
|---|---:|---:|---|
| `.text.open_cfw_freertos_port_yield` | 24 | 4 | `105148e84e8d81859d7c85803d553503d05745bd56d807495d62f3bf9da68235` |
| `.text.open_cfw_freertos_port_enter_critical` | 30 | 4 | `18797972899b42b6333a1353a25820dc720a5e477d0275b3fb4f039cbc0ef158` |
| `.text.open_cfw_freertos_port_exit_critical` | 54 | 4 | `1106c10ba143e84c0335da8c09658f88594e4578a8dfece201e73ee36f00900f` |

The exact unresolved text relocations are also identical:

| Section | Offset | ELF relocation | Symbol | Meaning |
|---|---:|---|---|---|
| enter | `0x02` | type 10, `R_ARM_THM_CALL` | `ulSetInterruptMask` | initial BASEPRI mask call |
| exit | `0x1C` | type 30, `R_ARM_THM_JUMP24` | `vClearInterruptMask` | compiler tail-call on final exit |
| exit | `0x22` | type 10, `R_ARM_THM_CALL` | `ulSetInterruptMask` | cold assertion path |

Yield has no relocation. ICSR and `ulCriticalNesting` are emitted as fixed
`MOVW`/`MOVT` address materialization and therefore have no linker relocation.
Each function has one 8-byte cant-unwind `.ARM.exidx` record
`0000000001000000`, SHA-256
`01acecb507abfe1a354aa8064f4af5d3f1acd019e37db3c11c97523b71c76e9d`,
with one offset-zero type-42 `R_ARM_PREL31` relocation to its own text section.

The candidate is not byte-identical to the official IAR object and does not
claim to be. Clang materializes fixed addresses locally, selects a tail-call
for the clear-mask path, and outlines the cold assertion block within the
exit section. What is pinned is the complete released behavior, side-effect
order, fixed seams, symbols, output bytes, and relocations under each reviewed
compiler.

## Host behavior contract

The host fixture proves:

- yield logs ICSR write, DSB, ISB in that order;
- enter logs set-mask, one nesting read, one incrementing write, DSB, ISB;
- an enter at `0xFFFFFFFF` wraps the 32-bit depth to zero, matching the
  released unsigned operation;
- an exit at depth two performs three reads and one write without clearing
  the mask;
- an exit at depth one performs three reads, writes zero, and clears the mask
  with argument zero; and
- an exit at depth zero takes the assertion hook before any decrement or
  clear operation.

The target-object checks independently prove that the host seam substitutions
did not remove target DSB/ISB instructions, fixed addresses, or mask-symbol
dependencies.

## Validation

Apple-clang validation:

```sh
python3 -m unittest -v \
  openCFW/tests/test_freertos_scheduler_port_trio_candidate.py
```

Result: 8 tests passed.

Linux/Homebrew-clang validation in the reviewed LLVM 22.1.8 container:

```sh
docker exec \
  -e OPENCFW_CLANG=/home/linuxbrew/.linuxbrew/opt/llvm/bin/clang \
  -e OPENCFW_TOOLCHAIN_PROFILE=linux-clang \
  opencfw-linux-llvm \
  python3 -m unittest -v \
    tests/test_freertos_scheduler_port_trio_candidate.py
```

Result: the same 8 tests passed, including the exact target-section and
relocation contract.

## Original promotion boundary and current production result

The original isolated audit stopped before integration and required a later
production tranche to:

1. choose reviewed appended placement for all three project-prefixed entries;
2. bind the two unresolved symbols to the authenticated interrupt-mask pair;
3. generate entry redirects for all three complete official ranges;
4. preserve the yield alignment policy and the exact caller topology;
5. record Apple and Linux placement-dependent redirect bytes and aggregate
   pins;
6. update production overlay evidence, notices, memory map, coverage, and
   manifest regions together; and
7. repeat full package and flash-plan verification before any hardware use.

The subsequent scheduler-cluster promotion performed these mutations. The
following pins record the stable post-semaphore, pre-reset/unordered historical
baseline; later source promotions supersede these aggregate hashes without
moving the scheduler functions:

| Profile | Overlay | Apollo-main component | Core-source package |
|---|---|---|---|
| Apple clang 21.0.0 | 121,330 / `b0e7ec99bdf68b0b42b79e2bb935274f6b5a12d53a449cca3f021fa906ad1e3c` | 3,644,726 / `d9af47dd5b4668f23722a530df40b12dfb926ef5c0cc6fb603733b2e14a05a17` | 4,423,180 / `74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d` |
| exact-root Linux clang 22.1.8 | 123,184 / `2ece296109ba518aa5e9474bc46dc0f77003abd57231c5becd6525dd18673c63` | 3,646,580 / `0c65b98e4867b7aa143572ccb831879c88ebeded4c8e41d2e294a72bd0ea61a9` | 4,425,034 / `b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1` |

The scheduler cluster is live production source, not a pending candidate. The
original official ranges, pre-promotion hashes, and aggregate baseline above
remain historical authentication evidence.
