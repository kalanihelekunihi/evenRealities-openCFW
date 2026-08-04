# G2 FreeRTOS assertion/interrupt-mask port-seam audit

Status: unequivocal upstream source boundary; safe fixed seam while the
official provider is retained; not production-integrated  
Scope: official G2 package `2.2.6.10`, Apollo-main application; offline,
read-only analysis only, with no signing, flashing, serial, debugger, or
hardware access

## Subsequent production status

The status line above records the original audit milestone and is now
historical. Production source-assembles the exact MIT-licensed
FreeRTOS-Kernel V10.5.1 pair from the sectionized Clang-syntax adaptation
`runtime_freertos_interrupt_mask.S` (SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`).
Its byte-exact fixed copies occupy `[0x005FA0A4,0x005FA0BA)` with SHA-256
`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`
and `[0x005FA0BA,0x005FA0C8)` with SHA-256
`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`;
independent isolated copies are appended at `[0x007B00D8,0x007B00EE)` and
`[0x007B00EE,0x007B00FC)`.

## Result

The even entry at `0x005FA0A4` is unequivocally the
FreeRTOS-Kernel V10.5.1 Cortex-M55
`ulSetInterruptMask` portable-layer leaf:

| Property | Recovered value |
|---|---|
| Official range | `[0x005FA0A4,0x005FA0BA)` |
| Size | 22 bytes |
| SHA-256 | `f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323` |
| Upstream source | `portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s`, lines 156-162 |
| Upstream release | FreeRTOS-Kernel V10.5.1 |
| License | MIT |
| Architecture | Arm Cortex-M55 / Armv8-M Mainline, Thumb |
| Calling convention | AAPCS32 |
| Return | previous `BASEPRI` in `r0` |
| Scratch register | `r1` |
| Side effect | `BASEPRI = 0x30`, followed by DSB and ISB |
| Outgoing calls | none |
| Literals, data, or private state | none |
| Direct `BL` encodings to entry | 181 |
| Direct `B.W` references | none |
| External branches into interior | none |
| Stored entry/interior addresses | none |

There is no private algorithm to recreate. The complete function is six
released-source assembly instructions with one recovered configuration
parameter:

```text
005FA0A4  mrs     r0, basepri
005FA0A8  mov.w   r1, #0x30
005FA0AC  msr     basepri, r1
005FA0B0  dsb     sy
005FA0B4  isb     sy
005FA0B8  bx      lr
```

The body can be source-owned. Because the vendored file uses IAR assembly
syntax while openCFW's current overlay compiler is Clang, promotion should
use a minimal syntax-adapted assembly translation that retains the upstream
MIT notice and pins the generated body and ABI. This is a toolchain-syntax
adaptation, not a behavioral reimplementation.

The existing stock entry is also a safe temporary fixed seam. That statement
is deliberately conditional: the authenticated official provider must keep
the complete 22-byte range, source calls must bind to even entry
`0x005FA0A4` with Thumb `BL` semantics, and removal of the provider must wait
until all 181 direct calls have migrated or the exact span itself is supplied
by source.

## Authoritative inputs

The reviewed official image is:

| Property | Value |
|---|---|
| File | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Installed application SHA-256 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Application load address | `0x00438000` |

The authenticated source comparator is:

| Property | Value |
|---|---|
| Release | FreeRTOS-Kernel V10.5.1 |
| Commit | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| Tree | `7496dfa815c3cea2f45a090c6e92d113f494b930` |
| File | `third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s` |
| File bytes | `11,686` |
| File SHA-256 | `eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f` |
| Git blob | `4d02a431e1d759f12f50e70fc55a7b0b4d368e89` |

The existing whole-port audit independently proves that G2 selects
`IAR/ARM_CM55_NTZ/non_secure`, not the TrustZone-context port, and uses
`configENABLE_MPU=0`. The mask leaf is present in both released M55 assembly
alternatives, but the surrounding first-task, SVC, and PendSV frame proves
the NTZ directory for this image.

## Exact boundary

The exact official bytes are:

```text
eff311804ff0300181f31188bff34f8fbff36f8f7047
```

Every instruction is accounted for:

| Official operation | Released-source role |
|---|---|
| `mrs r0,basepri` | save and return the prior interrupt threshold |
| `mov.w r1,#0x30` | materialize `configMAX_SYSCALL_INTERRUPT_PRIORITY` |
| `msr basepri,r1` | mask interrupts at the configured threshold |
| `dsb sy` | complete explicit memory accesses before continuing |
| `isb sy` | synchronize subsequent instruction execution |
| `bx lr` | return with the previous mask still in `r0` |

The predecessor and successor make the boundary positive rather than
heuristic:

| Range | Function | Bytes | SHA-256 |
|---|---|---:|---|
| `[0x005FA08C,0x005FA0A4)` | `vStartFirstTask` | 24 | `44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347` |
| `[0x005FA0A4,0x005FA0BA)` | `ulSetInterruptMask` | 22 | `f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323` |
| `[0x005FA0BA,0x005FA0C8)` | `vClearInterruptMask` | 14 | `97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a` |

The selected leaf owns its `bx lr`; neither neighbor falls through into it.
The immediately following `vClearInterruptMask` accepts a saved mask in `r0`,
writes it to `BASEPRI`, executes the same barriers, and returns. This exactly
matches the released pair.

## Upstream identity and configuration

The V10.5.1 source is:

```asm
ulSetInterruptMask:
    mrs r0, basepri
    mov r1, #configMAX_SYSCALL_INTERRUPT_PRIORITY
    msr basepri, r1
    dsb
    isb
    bx lr
```

The recovered immediate proves:

```c
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 0x30
```

Apollo510 implements four NVIC priority bits. In shifted hardware priority
form, `0x30` corresponds to logical priority 3. Source integration must keep
the shifted assembly value `0x30`; replacing it with unshifted integer `3`
would change the mask.

No other FreeRTOS setting changes this leaf. The broader image proves:

- Cortex-M55 / Armv8-M Mainline instruction availability;
- the NTZ/non-secure portable-layer shape;
- `configENABLE_MPU=0`;
- `configENABLE_FPU=1`;
- a 1024-Hz Apollo STIMER tick.

Only the architecture and mask value affect this six-instruction body. FPU,
MVE, MPU, TrustZone context, tick, heap, and TCB settings do not add a data or
call dependency here.

Writing `BASEPRI` is a privileged operation. The source-owned leaf must remain
in the privileged FreeRTOS portable-layer boundary. It writes `BASEPRI`
directly, not `BASEPRI_MAX`; therefore callers must retain the released
save/set/restore protocol and must not assume the instruction can only make a
pre-existing mask more restrictive.

## Why assertion paths call a mask function

G2's recovered `configASSERT` fail-stop expands to the following behavior:

1. call `ulSetInterruptMask`;
2. write zero through invalid address `0xFFFFFFFF`;
3. loop forever.

The old mask returned in `r0` is intentionally discarded on that fatal path.
The same leaf also implements the released port macros:

```c
#define portDISABLE_INTERRUPTS()          ulSetInterruptMask()
#define portSET_INTERRUPT_MASK_FROM_ISR() ulSetInterruptMask()
```

That dual use explains why the entry has far more callers than the assertion
sites currently under source-boundary review. Some callers are fatal
assertions; others save the old threshold for a later
`vClearInterruptMask(saved)` call.

## Caller and reference topology

The complete installed application was scanned at every halfword for direct
Thumb-2 `BL` and `B.W`, and for narrow `B`, `Bcc`, `CBZ`, and `CBNZ`
references to the entry or interior. Every byte offset was also scanned for
possible even or odd/Thumb stored entry/interior addresses.

The result is:

- 181 direct `BL` encodings to exactly `0x005FA0A4`;
- call-site-address SHA-256
  `f0187e62c4c399694d4fdd8e64a2e238724f6fb0ec89a6520c3020156eb9c106`;
- first call at `0x0043C7EA`;
- last call at `0x005847D0`;
- no direct `B.W` to the entry;
- no external wide or narrow branch into the interior;
- no stored even entry/interior address;
- no stored odd/Thumb entry/interior address.

The analyzer's JSON mode emits all 181 addresses. Representative,
independently understood uses are:

| Call site | Context |
|---:|---|
| `0x004415D4` | FreeRTOS queue-creation assertion |
| `0x0044208C` | Cortex-M55 portable-layer assertion |
| `0x00454F26` | `pcTaskGetName` assertion |
| `0x004561A2` | FreeRTOS `heap_4` assertion |
| `0x0047E6C8` | FreeRTOS timer-service assertion |
| `0x005847D0` | late application assertion path |

The address distribution is broad:

| 4-KiB page | Calls | 4-KiB page | Calls |
|---:|---:|---:|---:|
| `0x0043C000` | 2 | `0x0044_1000` | 37 |
| `0x0044_2000` | 6 | `0x0044_4000` | 5 |
| `0x0044_9000` | 2 | `0x0045_4000` | 14 |
| `0x0045_5000` | 31 | `0x0045_6000` | 5 |
| `0x0045_E000` | 1 | `0x0046_4000` | 2 |
| `0x0046_5000` | 7 | `0x0046_D000` | 1 |
| `0x0047_5000` | 2 | `0x0047_E000` | 20 |
| `0x0048_E000` | 4 | `0x0049_1000` | 2 |
| `0x004C_4000` | 2 | `0x004C_9000` | 3 |
| `0x004D_0000` | 2 | `0x004E_1000` | 3 |
| `0x0052_A000` | 2 | `0x0053_8000` | 3 |
| `0x0054_1000` | 1 | `0x0057_D000` | 8 |
| `0x0057_E000` | 14 | `0x0058_4000` | 2 |

The lack of a stored pointer means there is no observed callback/table ABI to
preserve for this function. As usual, a static image scan cannot exclude an
address computed arithmetically at runtime, but the exact 181 direct calls
are the complete recoverable reference set in the installed bytes.

## ABI and source-ownership decision

The callable contract is small and complete:

- even code address `0x005FA0A4`, entered by Thumb `BL`;
- no arguments;
- prior `BASEPRI` returned as `uint32_t` in `r0`;
- `r1` used as caller-saved scratch;
- `r2-r12`, SP, LR, and callee-saved registers untouched;
- no stack frame;
- no literal pool, relocation, global, TLS, heap, or HAL dependency;
- privileged architectural side effect `BASEPRI = 0x30`;
- DSB and ISB before return.

This is a strong source-ownership candidate. A focused replacement does not
need the rest of `portasm.s` to compile in the same translation unit. The
safe increment is a dedicated assembly source with this one global symbol,
an exact target/CPU declaration, and generated-byte checks.

### Temporary fixed-seam option

Binding newly source-generated FreeRTOS code to stock `0x005FA0A4` is safe
while all of these conditions hold:

1. the official provider retains authenticated
   `[0x005FA0A4,0x005FA0BA)`;
2. the linker emits a range-valid Thumb call to the even entry;
3. the caller accepts the AAPCS return/clobber contract above;
4. `BASEPRI=0x30` remains the system interrupt-priority contract;
5. provider ownership prevents another overlay from partially replacing the
   span.

This is useful for incremental promotion of `pcTaskGetName` and the
queue-creation cluster. It should be recorded as an explicit fixed-address
seam, not treated as an unresolved binary blob.

### Preferred production transition

Source-own the exact span early. Because 181 callers already target the stock
address, supplying generated bytes at the same address avoids changing every
call site and removes a highly shared opaque dependency in one bounded
increment. If the overlay architecture instead redirects the entry to an
appended implementation, it must prove branch range and preserve the whole
22-byte stock range for ownership accounting.

## Focused validation

The read-only analyzer is:

```sh
python3 tools/analyze_g2_freertos_assert_port_seam.py
python3 tools/analyze_g2_freertos_assert_port_seam.py --json
```

It checks:

- package and installed-application identities;
- exact leaf, predecessor, and successor bytes and hashes;
- six-instruction semantics and recovered `0x30` mask;
- authenticated V10.5.1 port-source file and source block;
- all 181 direct `BL` encodings, their address digest, and page distribution;
- absence of `B.W`, external interior, narrow, and stored references;
- the source-ownership and fixed-seam conditions in machine-readable output.

`tests/test_analyze_g2_freertos_assert_port_seam.py` contributes four focused
tests covering the boundary and upstream identity, complete call/reference
topology, JSON/read-only behavior, and rejection of a mutated official
package.

Focused validation result:

```text
Ran 4 tests in 7.114s

OK
```

## Recommendation

Classify `[0x005FA0A4,0x005FA0BA)` as a released FreeRTOS portable-layer
source boundary, not an unknown blob.

For the immediate `pcTaskGetName` and queue-creation promotions, using
`0x005FA0A4` as an audited fixed seam is safe while the official provider
remains. The preferred broader transition is to generate this exact leaf
from a syntax-adapted, MIT-retaining assembly source at the same address,
because doing so resolves the assertion dependency for 181 callers at once.

Do not source-own only the mask-setting half of the ABI and then change call
protocols. Callers that save `r0` require the paired `vClearInterruptMask` at
`0x005FA0BA`; that adjacent 14-byte leaf is itself unequivocal upstream
source and is the natural next companion boundary.
