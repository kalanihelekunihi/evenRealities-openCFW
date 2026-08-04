# G2 FreeRTOS V10.5.1 configuration and Cortex-M55 port audit

Status: focused binary recovery plus production integration evidence for the
five fixed-address NTZ context/exception leaves and the bounded
`xTaskGetTickCount`/`xTaskGetTickCountFromISR` source seam in official G2
package `2.2.6.10`
Scope: Apollo-main application only; source assembly and offline package
verification; no signing or hardware writes

## Result

The official application provides enough evidence to make one source-port
choice unequivocally:

- use the authenticated FreeRTOS-Kernel V10.5.1 source baseline already under
  [`third_party/freertos-kernel`](../../third_party/freertos-kernel/README.openCFW.md);
- select
  [`portable/IAR/ARM_CM55_NTZ/non_secure`](../../third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure),
  with `configENABLE_MPU=0`;
- do **not** select the TrustZone-aware
  `portable/IAR/ARM_CM55/non_secure` alternative.

This is not yet permission to link the pristine kernel without G2 adaptation.
The portable layer is a conclusive source match, but the G2 kernel has at
least one material vendor modification: its 112-byte TCB stores the task's
stack depth at offset `0x54`. Pristine V10.5.1 uses that position for
`pxEndOfStack` only when `configRECORD_STACK_HIGH_ADDRESS=1`; it does not
provide the observed G2 stack-depth field. The G2 timer, trace, hook, and
Apollo STIMER seams also have to be supplied.

The safe source-replacement boundary is therefore:

1. pristine V10.5.1 kernel and `ARM_CM55_NTZ/non_secure` port as the base;
2. a recovered G2 `FreeRTOSConfig.h`;
3. a small, explicit G2 tasks/TCB compatibility patch;
4. the recovered Apollo STIMER tick/tickless implementation;
5. recovered application hooks and the `heap_4` allocator configuration.

### Open-source reuse decision

FreeRTOS-Kernel V10.5.1 is unequivocally reusable here under its retained MIT
license. The 49-file authenticated snapshot now retains the exact released
`portable/MemMang/heap_4.c`, 20,608 CRLF bytes with SHA-256
`d48a51e34caed771e6650d95f6c2527e52fde2a6ebc6f83b49d003aef0135e05`,
as an authenticated, unselected reference. It is not compiled or linked and
does not select the G2 allocator configuration or placement.

Current official Ambiq Apollo510 HAL/CMSIS sources are also source-available
under their upstream notices and corroborate the STIMER register meanings.
They are not yet selected wholesale because the exact G2 AmbiqSuite revision
has not been authenticated. Until it is, use them to name and check recovered
register/ABI seams, not as an assumed drop-in binary match.

## Evidence grades

- **Proven**: a positive instruction, data-layout, call, vector, or exact
  source-alternative difference exists in the official binary.
- **Derived**: arithmetic or macro meaning follows from proven binary values
  plus the Apollo510 architecture definition.
- **Strongly constrained**: the value is required to reproduce several
  observed offsets or compiled branches, but a bespoke vendor fork could
  theoretically encode the same result another way.
- **Unresolved**: the reviewed binary region cannot distinguish the choices.

## Authoritative inputs

The reviewed package is:

| Property | Value |
|---|---|
| File | `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` |
| Package bytes | `3,523,396` |
| Package SHA-256 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| OTA preamble | 32 bytes |
| Application load address | `0x00438000` |

The source comparator is the authenticated FreeRTOS-Kernel `V10.5.1`
snapshot at commit
`def7d2df2b0506d3d249334974f51e427c17a41c`, tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`. Its offline verifier is:

```sh
python3 openCFW/third_party/freertos-kernel/verify_snapshot.py
```

The focused binary verifier added with this audit is:

```sh
python3 openCFW/tools/analyze_g2_freertos_port.py
```

It checks the package identity, vectors, 21 reviewed instruction spans, port
semantics, TCB seam, tick seam, and allocator constants without writing any
files.

## Vector ownership

| Vector | Table index | Official entry | Meaning |
|---|---:|---:|---|
| Initial MSP | 0 | `0x2007FB00` | application main stack |
| Reset | 1 | `0x005E4233` | Thumb reset handler |
| SVC | 11 | `0x005FA121` | port assembly SVC shim |
| PendSV | 14 | `0x005FA0C9` | FreeRTOS context switch |
| SysTick | 15 | `0x00442115` | FreeRTOS tick-handler body |
| External IRQ 32 | 48 | `0x00456427` | Apollo STIMER compare-A ISR |

The SysTick vector remains valid, but it is not the normal periodic clock
source. The overridden timer setup and external IRQ 32 drive the production
tick from Apollo STIMER compare A.

## Why the NTZ port is proven

The complete official port-assembly region is
`0x005FA058...0x005FA131`. Its decisive behavior is:

- `vRestoreContextOfFirstTask` pops exactly `{PSPLIM, EXC_RETURN}`, writes
  `CONTROL=2`, restores PSP, clears BASEPRI, and exception-returns.
- `PendSV_Handler` conditionally saves `s16-s31`, then saves exactly
  `{PSPLIM, EXC_RETURN, r4-r11}`.
- The only `BL` in PendSV is to `vTaskSwitchContext` at `0x004551B4`.
- The SVC C handler accepts only SVC number 2, enables the FPU, and restores
  the first task. Any other SVC reaches the configured fail-stop assertion.
- There is no secure-context word in the initial or switched task context,
  no `xSecureContext` global access, and no call corresponding to
  `SecureContext_SaveContext` or `SecureContext_LoadContext`.
- There is no saved `CONTROL` word and no MAIR/RBAR/RLAR/MPU programming.

That is the exact structural path in V10.5.1
`ARM_CM55_NTZ/non_secure/portasm.s` with `configENABLE_MPU=0`.

The rejected `ARM_CM55/non_secure` source necessarily has all of the
following absent from the G2 binary:

- an `xSecureContext` word before PSPLIM in the task context;
- secure-context save/load calls and secure-stack EXC_RETURN tests in PendSV;
- SVC 0/1 services and `vPortFreeSecureContext`;
- larger restore/save frame shapes even when MPU is disabled.

This distinguishes the two released alternatives positively; it is not an
absence-only guess.

### Security interpretation

`configENABLE_TRUSTZONE=0` is proven for the FreeRTOS portable layer. The
reviewed application uses the non-secure/NTZ context model. This does **not**
prove that Apollo510 secure boot, SAU attribution, the bootloader, or other
images are disabled. Those device-wide security decisions remain outside
this audit.

## Portable-layer function map

| Official address | Recovered function | Binary-supported behavior |
|---:|---|---|
| `0x005FA058` | `vRestoreContextOfFirstTask` | two-word NTZ/non-MPU context header |
| `0x005FA07E` | `vRaisePrivilege` | clears CONTROL.nPRIV |
| `0x005FA08C` | `vStartFirstTask` | restores MSP from VTOR, enables IRQ/FIQ, `SVC 2` |
| `0x005FA0A4` | `ulSetInterruptMask` | saves BASEPRI, installs `0x30`, DSB/ISB |
| `0x005FA0BA` | `vClearInterruptMask` | restores saved BASEPRI |
| `0x005FA0C8` | `PendSV_Handler` | NTZ/non-MPU switch with conditional FP high-register context |
| `0x005FA120` | `SVC_Handler` | selects MSP/PSP and branches to C handler |
| `0x004420A6` | `prvSetupFPU` | enables CP10/CP11 and FPCCR ASPEN/LSPEN |
| `0x004420BC` | `vPortYield` | pends PendSV through ICSR |
| `0x004420D0` | `vPortEnterCritical` | BASEPRI mask plus global nesting counter |
| `0x004420E8` | `vPortExitCritical` | checked nesting decrement and unmask |
| `0x00442114` | `SysTick_Handler` | masked `xTaskIncrementTick`, optional PendSV |
| `0x00442134` | `vPortSVCHandler_C` | only SVC 2 accepted |
| `0x0044215A` | `pxPortInitialiseStack` | preload-register frame, EXC_RETURN `0xFFFFFFFD`, PSPLIM |
| `0x004421E2` | `xPortStartScheduler` | lowest PendSV/SysTick priorities, custom timer setup |
| `0x00442228` | `xPortIsInsideInterrupt` | `IPSR != 0` |

The initial software frame is 18 32-bit words: the standard exception/task
register material plus EXC_RETURN and PSPLIM. It has neither an MPU CONTROL
word nor a TrustZone secure-context word.

## Recovered configuration

### Proven values

| Configuration or ABI choice | Recovered value | Decisive evidence |
|---|---:|---|
| `configENABLE_TRUSTZONE` | `0` | NTZ frame and SVC/PendSV shape |
| portable directory | `IAR/ARM_CM55_NTZ/non_secure` | exact alternative comparison |
| `configENABLE_MPU` | `0` | no CONTROL/MPU task context or MPU programming |
| `configENABLE_FPU` | `1` | CPACR/FPCCR setup and `s16-s31` switch path |
| `portPRELOAD_REGISTERS` | `1` | `0x12121212`, `0x03030303`, … initial frame |
| `portCRITICAL_NESTING_IN_TCB` | `0` | global critical nesting at `0x2000309C` |
| `configMAX_SYSCALL_INTERRUPT_PRIORITY` | `0x30` | immediate written to BASEPRI |
| port minimum interrupt priority | `0xFF` | PendSV and SysTick SHPR3 bytes ORed to `0xFF` |
| `configMAX_PRIORITIES` | `56` | priority bounds `0x38`; 56 ready lists |
| highest task priority | `55` | invalid priorities clamp to `0x37` |
| `configMAX_TASK_NAME_LEN` | `32` | copy bound and terminator at TCB `+0x53` |
| `configUSE_16_BIT_TICKS` | `0` | 32-bit tick/list control arithmetic and `0xFFFFFFFF` max |
| `configTICK_RATE_HZ` | `1024` | 32.768-kHz STIMER divided by 32 counts |
| `configUSE_PREEMPTION` | `1` | unblocked higher/equal-priority task requests switch |
| `configUSE_TIME_SLICING` | `1` | multiple tasks on current ready list request switch each tick |
| `configIDLE_SHOULD_YIELD` | `1` | idle yields when priority-zero ready count is at least two |
| `configUSE_PORT_OPTIMISED_TASK_SELECTION` | `0` | scheduler scans ready lists downward rather than CLZ/bitmap selection |
| `configUSE_TICKLESS_IDLE` | `1` | idle invokes `vPortSuppressTicksAndSleep` |
| `configEXPECTED_IDLE_TIME_BEFORE_SLEEP` | `2` | idle tickless threshold is exactly two ticks |
| `configUSE_IDLE_HOOK` | `1` | idle calls hook at `0x0046D898` |
| `configUSE_TICK_HOOK` | `0` | complete tick increment paths have no hook call |
| `configCHECK_FOR_STACK_OVERFLOW` | `>1` (normally `2`) | every switch checks four `0xA5A5A5A5` words at stack base |
| `configUSE_MALLOC_FAILED_HOOK` | `1` | failed `pvPortMalloc` calls `0x0046D85E` |
| `configASSERT` | enabled | invalid paths mask interrupts, fault-write, and loop |
| `configSUPPORT_STATIC_ALLOCATION` | `1` | static task/queue/timer/event creators and provenance bytes |
| `configSUPPORT_DYNAMIC_ALLOCATION` | `1` | dynamic task/queue/timer/event creators |
| `configUSE_TIMERS` | `1` | timer lists, queue, task, and API family |
| `INCLUDE_xTimerPendFunctionCall` | `1` | four-word pended-callback message and ISR API |
| `configTIMER_QUEUE_LENGTH` | `50` | static queue creator tuple `(50,16,...)` |
| `configTIMER_TASK_PRIORITY` | `54` | timer task creation priority `0x36` |
| `configUSE_DAEMON_TASK_STARTUP_HOOK` | `0` | timer service entry begins its normal loop with no startup-hook call |
| `configQUEUE_REGISTRY_SIZE` | `0` | timer queue initialization has no registry branch/call |
| `configUSE_MUTEXES` | `1` | mutex holder/base-priority/held-count behavior |
| `configUSE_RECURSIVE_MUTEXES` | `1` | recursive mutex count and API behavior |
| `configUSE_TRACE_FACILITY` | `1` | TCB, queue, timer, and event-group trace-number fields |
| `configUSE_QUEUE_SETS` | `0` | no queue-set-container word in exact 80-byte Queue_t |
| `configUSE_TASK_NOTIFICATIONS` | `1` | notification value/state and API family |
| `configTASK_NOTIFICATION_ARRAY_ENTRIES` | `1` | one value at `+0x68`, one state byte at `+0x6C` |
| `configHEAP_CLEAR_MEMORY_ON_FREE` | `0` | complete `vPortFree` has no payload clear |
| `configTOTAL_HEAP_SIZE` | `0x2F000` | immediate in heap initialization |

The V10.5.1 IAR M55 port defines its lowest PendSV/SysTick priority as the
port-local constant 255; it is not recovered as a G2
`configKERNEL_INTERRUPT_PRIORITY` macro.

Apollo510 CMSIS declares four implemented NVIC priority bits. On that
hardware, the proven shifted BASEPRI value `0x30` corresponds to logical
priority 3, and the port's `0xFF` lowest-priority write is implemented as
priority 15. Preserve the shifted `0x30` value in the assembly boundary even
if a source configuration also exposes the logical priority as 3.

### Strongly constrained values

These are the values required for the observed 112-byte TCB if pristine
V10.5.1 conditional fields are retained around the G2 stack-depth extension:

| Configuration | Compatible value | Reason |
|---|---:|---|
| `configUSE_APPLICATION_TASK_TAG` | `0` | no pointer between trace/mutex/notification fields |
| `configNUM_THREAD_LOCAL_STORAGE_POINTERS` | `0` | no TLS-pointer words |
| `configGENERATE_RUN_TIME_STATS` | `0` | no per-TCB runtime-counter word; G2 tracing uses external tables |
| `configUSE_NEWLIB_REENTRANT` | `0` | no newlib/TLS block in the TCB |
| `configUSE_C_RUNTIME_TLS_SUPPORT` | `0` | no runtime TLS block |
| `configUSE_POSIX_ERRNO` | `0` | no TCB errno word |
| `configRECORD_STACK_HIGH_ADDRESS` | `0` plus G2 extension | `+0x54` is a stack depth, so pristine `pxEndOfStack` must not occupy it |
| `INCLUDE_xTaskAbortDelay` | `0` | no observed access to byte `+0x6E`; reviewed API shape absent |
| `INCLUDE_vTaskSuspend` | `1` | stock `xTaskCheckForTimeOut` implements the `portMAX_DELAY` indefinite-wait branch |

The stock G2 switch path writes external trace state using the TCB number at
`+0x58`. That is compatible with `configUSE_TRACE_FACILITY=1` plus custom
`traceTASK_SWITCHED_IN/OUT` macros, not the standard per-TCB runtime-stat
field.

### Unresolved configuration

| Item | Why it remains unresolved |
|---|---|
| `configENABLE_MVE` | FPU=1 already compiles the same `s16-s31` assembly; MVE adds no distinguishing instruction in this port |
| `configCPU_CLOCK_HZ` | the architectural SysTick calculation is overridden by Apollo STIMER |
| `configTIMER_TASK_STACK_DEPTH` | required syntactically, but compiled out by static timer-task allocation |
| remaining `INCLUDE_*` API switches | not required for port selection and not exhaustively inventoried here |
| exact G2 AmbiqSuite/Apollo HAL revision | current Apollo510 sources corroborate registers, but the G2 source revision is not authenticated yet |
| device-wide TrustZone/SAU policy | belongs to boot/security initialization, not the NTZ RTOS port |

For source integration, `configTIMER_TASK_STACK_DEPTH=4096` is a sensible
compatibility default, but it is not a recovered compile-time value. The
official `vApplicationGetTimerTaskMemory` callback at `0x004D3610` supplies:

- static TCB `0x20071EA0`;
- static stack `0x2003FA98`;
- runtime stack depth `0x1000` words.

## Tick and tickless implementation

The overridden `vPortSetupTimerInterrupt` is
`0x0045643E...0x00456495`. It:

1. stores 32 as the counter increments per tick;
2. computes `(UINT32_MAX / 32) - 4` as the maximum suppressible tick count;
3. enables external IRQ 32 and STIMER compare-A interrupt bit 0;
4. programs compare A;
5. preserves the upper configuration state while selecting configuration
   value `0x103`.

Apollo510 defines STIMER configuration bit 8 as compare-A enable and clock
selector 3 as `XTAL_32KHZ`, 32,768 Hz. Thus:

```text
tick rate = 32,768 counter increments/s ÷ 32 increments/tick
          = 1,024 ticks/s
tick time = 0.9765625 ms
```

The current official Ambiq Apollo510 header is useful corroboration for those
stable register values, but it is not treated as proof of the exact G2 HAL
revision:

- [`am_hal_stimer.h` at official commit `bea5e88`](https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/bea5e88e58344a6b49a51282d6fe5dbc53ae477e/mcu/apollo510/hal/am_hal_stimer.h):
  `AM_HAL_STIMER_CFG_COMPARE_A_ENABLE`, `AM_HAL_STIMER_XTAL_32KHZ`, and
  minimum compare delta 4;
- [`apollo510.h` at the same commit](https://github.com/AmbiqMicro/ambiqhal_ambiq/blob/bea5e88e58344a6b49a51282d6fe5dbc53ae477e/CMSIS/AmbiqMicro/Include/apollo510.h):
  compare-A enable at bit 8, clock selector in bits 0-3,
  `XTAL_32KHZ=3`, and four NVIC priority bits.

The maximum suppressible interval is 134,217,723 ticks, approximately
131,071.995 seconds or 36.409 hours.

The ISR at `0x00456426` clears compare-A status and enters the elapsed-tick
dispatcher at `0x004563B4`. The dispatcher:

- reads the 32-bit wrapping STIMER;
- computes elapsed counts relative to `0x20074884`;
- divides by counts-per-tick at `0x20074888`;
- advances compare A;
- invokes `xTaskIncrementTick` once per elapsed tick;
- pends PendSV if any increment requests a switch.

The tickless function at `0x00456498` clamps the idle interval to the maximum,
disables interrupts, confirms sleep, programs compare A, invokes the
pre-sleep hook, performs WFI only if that hook leaves it necessary, invokes
the post-sleep hook, recomputes elapsed ticks, re-arms compare A, steps the
kernel tick, and re-enables interrupts.

Hook seams are:

| Official address | Hook role |
|---:|---|
| `0x0046D836` | pre-sleep/power-manager path |
| `0x0046D856` | post-sleep/power-manager path |
| `0x0046D898` | idle hook |
| `0x0046D85E` | malloc-failed hook; logs and loops |
| `0x0046D86C` | stack-overflow hook; logs, BKPT, and loops |

## Kernel object ABI

All reviewed kernel scalar types and pointers are 32-bit. Stack elements are
32-bit and the allocator alignment is eight bytes.

### Fundamental list types

| Type | Bytes | Layout |
|---|---:|---|
| `ListItem_t` | `0x14` | value, next, previous, owner, container |
| `MiniListItem_t` | `0x0C` | value, next, previous |
| `List_t` | `0x14` | item count, index pointer, mini end item |

### Queue_t

The exact queue control block is `0x50` bytes:

| Offset | Field |
|---:|---|
| `+0x00` | storage head |
| `+0x04` | write pointer |
| `+0x08` | queue tail / mutex holder |
| `+0x0C` | last-read pointer / recursive call count |
| `+0x10` | tasks waiting to send (`List_t`) |
| `+0x24` | tasks waiting to receive (`List_t`) |
| `+0x38` | messages waiting |
| `+0x3C` | queue length |
| `+0x40` | item size |
| `+0x44` | receive lock byte |
| `+0x45` | transmit lock byte |
| `+0x46` | static-allocation provenance byte |
| `+0x47` | alignment padding |
| `+0x48` | trace queue number |
| `+0x4C` | trace queue-type byte plus padding |

The absence of a word between `+0x46` and `+0x48` proves
`configUSE_QUEUE_SETS=0`; the provenance and trace fields prove both
allocation modes and `configUSE_TRACE_FACILITY=1`.

### Timer_t

The exact timer object is `0x2C` bytes:

| Offset | Field |
|---:|---|
| `+0x00` | name pointer |
| `+0x04` | timer `ListItem_t` |
| `+0x18` | period in ticks |
| `+0x1C` | callback ID/context |
| `+0x20` | callback pointer |
| `+0x24` | trace timer number |
| `+0x28` | status byte plus padding |

Dynamic creation allocates exactly `0x2C`; static creation verifies the same
size. Status bit 1 is static ownership and bit 2 is auto-reload, matching
V10.5.1.

The daemon message is 16 bytes because
`INCLUDE_xTimerPendFunctionCall=1`: command ID plus a 12-byte callback union.
The timer queue is therefore 50 items × 16 bytes = 800 bytes.

### EventGroup_t

The exact event-group object is `0x20` bytes:

| Offset | Field |
|---:|---|
| `+0x00` | event bits |
| `+0x04` | waiting-task `List_t` |
| `+0x18` | trace event-group number |
| `+0x1C` | static-allocation provenance byte plus padding |

### TCB

The exact TCB is `0x70` bytes:

| Offset | Field |
|---:|---|
| `+0x00` | top of stack |
| `+0x04` | state `ListItem_t` |
| `+0x18` | event `ListItem_t` |
| `+0x2C` | current priority |
| `+0x30` | stack base |
| `+0x34` | task name, 32 bytes |
| `+0x54` | **G2 stack-depth word** |
| `+0x58` | TCB/trace number |
| `+0x5C` | task/trace number |
| `+0x60` | base priority |
| `+0x64` | mutexes held |
| `+0x68` | notification value |
| `+0x6C` | notification state byte |
| `+0x6D` | static-allocation provenance byte |
| `+0x6E` | padding |

The static creator verifies `sizeof(TCB_t)==0x70`; the dynamic creator
allocates `0x70`. Task initialization writes the incoming stack depth
directly to `+0x54`, bounds names at 32, bounds priorities at 56, initializes
base priority at `+0x60`, and builds the initial port frame.

This is the main pristine-source incompatibility. A replacement must not
turn `+0x54` into a pointer or shift every subsequent field. Add an explicit
G2 field and compile-time `sizeof`/`offsetof` assertions.

## Allocator seam

The kernel allocator at `0x00456110...0x00456337` is FreeRTOS `heap_4`, not
the separate application TLSF allocator.

| Property | Recovered value |
|---|---:|
| heap base | `0x20004558` |
| nominal heap size | `0x2F000` = 192,512 bytes |
| nominal end | `0x20033558` |
| alignment | 8 bytes |
| block header | 8 bytes |
| allocated bit | `0x80000000` in block size |
| locking | `vTaskSuspendAll` / `xTaskResumeAll` |
| free-list policy | address-sorted insertion with adjacent coalescing |
| malloc-failed hook | `0x0046D85E` |

Important globals are:

| Address | Role |
|---:|---|
| `0x20074158` | start-list sentinel |
| `0x2007465C` | end marker pointer |
| `0x20074660` | current free bytes |
| `0x20074664` | minimum-ever free bytes |
| `0x20074668` | successful allocation count |
| `0x2007466C` | successful free count |

The current production profile selects these authenticated V10.5.1
algorithms through `runtime_freertos_heap4.c`. It preserves this
configuration, linker placement, and every complete public/private stock span;
it does not substitute the application TLSF heap. The bounded adapter keeps
the scheduler suspend/resume and malloc-hook calls as explicit fixed seams.
The 16,885-byte source has SHA-256
`d848b90a00da24db963c49dbff2472314b2a76c6cf269efef46e6cac56889986`;
its four relocated leaves and four alignment bytes occupy
`[0x007B031C,0x007B057E)`, while the complete 552-byte official closure
`[0x00456110,0x00456338)` redirects to them atomically.

## Preceding production tick-query source boundary

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` unequivocally supplies the
MIT `xTaskGetTickCount` and `xTaskGetTickCountFromISR` algorithms. The
223,695-byte upstream `tasks.c` hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The production boundary uses a 3,412-byte source adapter and 1,186-byte
header, with SHA-256 values
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`
and
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.

Focused disassembly corrects the ISR entry and authenticates both complete
functions:

| Function | Official span | Bytes | Official bytes | SHA-256 |
|---|---|---:|---|---|
| `xTaskGetTickCount` | `[0x00454EFE,0x00454F06)` | 8 | `dff8ac0800687047` | `6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0` |
| `xTaskGetTickCountFromISR` | `[0x00454F06,0x00454F10)` | 10 | `0020dff8a00800687047` | `8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a` |

The pair hashes to
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
Address `0x00454F08` is the ISR function's second instruction, not an entry;
no direct or stored reference targets it. The normal getter has nine direct
`BL` callers, with ordered-list digest
`3b032511b7c47b3afe47149262380345e354dea6d00f2b9dda369d10ce89abcd`.
The sole ISR caller is `0x004490D6`.

The literal at `0x004557AC` recovers `xTickCount` at RAM `0x20074A34`.
Production expresses that G2 binding through a relocation-free source
provider at `[0x007B07EC,0x007B07F8)`. After two generated alignment bytes,
the normal and ISR source leaves occupy `[0x007B07F8,0x007B07FC)` and
`[0x007B07FC,0x007B0800)`; each has one `R_ARM_THM_JUMP24` relocation to
the provider. Complete non-linking redirects and NOP fill replace the two
stock spans.

The resulting 115,932-byte overlay and 3,639,328-byte main component hash to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`
and
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`.
Main ownership is 116,114 source-owned, 81,626 generated patch-site, and
3,441,556 opaque base bytes.

The 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`;
116,738 bytes (2.642457%) are source, 83,415 (1.888165%) are generated,
4,217,629 (95.469378%) are opaque, and 200,153 (4.530622%) are controlled.
Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions. The placed inventory contains 53 source-compiled regions,
574 generated source-entry replacements, and 18 generated alignments.

This boundary owns read-only tick queries only. The Apollo STIMER increment
ISR, tickless path, scheduler transitions, and broader kernel state remain
stock or separately bounded.

## Recommended source integration gates

The evidence is now sufficient to select the NTZ port in source, but not to
skip compatibility checks. Before the replacement kernel is admitted to an
image:

1. add `_Static_assert` checks for all object sizes and the TCB/queue/timer/
   event-group offsets above;
2. implement the G2 TCB stack-depth extension at `+0x54`;
3. provide the STIMER compare-A IRQ 32 setup, ISR, tickless function, and
   power hooks;
4. configure BASEPRI exactly as `0x30`;
5. retain the 1024-Hz time base; do not round it to 1000 Hz;
6. retain `heap_4` and the 8-byte ABI until all binary callers are removed;
7. reproduce static timer-task memory and the 50 × 16-byte timer queue;
8. compile and disassemble the replacement port, checking the same NTZ/non-MPU
   frame shape with `analyze_g2_freertos_port.py`-equivalent assertions;
9. keep the pristine vendor snapshot unchanged and place all G2 modifications
   in an auditable patch/configuration layer.

## Exact reviewed span pins

The analyzer carries the full list. The most discriminating spans are:

| Span | Bytes | SHA-256 |
|---|---:|---|
| `0x005FA058...0x005FA07D` restore first task | 38 | `10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8` |
| `0x005FA0C8...0x005FA11F` PendSV | 88 | `d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3` |
| `0x00442134...0x00442159` SVC C | 38 | `7afe568df362a8b1af03c36af654ed56bd68da6b7266ee1172eb556ae2276c19` |
| `0x0044215A...0x004421E1` initial stack | 136 | `f97bdb238b175f9e72f3f03b228ffda3b69351cbe53e0b70c65707f600372caa` |
| `0x00454938...0x004549FB` task initialization | 196 | `54a87da84dbcdf7871563962b44490d635a2a924225fed68b99ccce811b397b2` |
| `0x00454EFE...0x00454F05` normal tick getter | 8 | `6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0` |
| `0x00454F06...0x00454F0F` ISR tick getter | 10 | `8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a` |
| `0x0045643E...0x00456495` STIMER setup | 88 | `5a54cfc80b658ae5b645ac53b60f0e3098f0fd24fd4b5bedcfb0f822007b30ae` |
| `0x00456498...0x0045655B` tickless | 196 | `d6716a7a132b61665a401d513ce75119e5210640f69f5d16424067cb4216e8da` |
| `0x00456110...0x0045620F` malloc | 256 | `8d86a7daf341ad836729e4abdd25b66b45f97a56d6d1077c07bf0c5718f8dc57` |
| `0x00456210...0x0045627F` free | 112 | `d754aec282080b2deafeb6756cbacc156af70a311499ee4d73eeb7497f12b032` |

## Final decision

The `ARM_CM55_NTZ/non_secure` V10.5.1 port is unequivocally identified. Its
five bounded context/exception leaves are now source-assembled in place with
the recovered configuration and G2 seams described below. The
TrustZone-aware port is not linked.

The exact normal and ISR tick-count getters are also source-owned through the
bounded provider/getter seam above. This does not expand source ownership to
the Apollo STIMER tick interrupt, tickless idle, or scheduler core.

The FreeRTOS kernel core is also an appropriate open-source reconstruction
base, but it is not a wholesale unmodified replacement: the TCB stack-depth
extension, external trace behavior, Apollo STIMER tick/tickless code,
application hooks, timer static memory, and `heap_4` placement are mandatory
compatibility work. MVE, exact HAL revision, remaining `INCLUDE_*` switches,
and device-wide secure attribution remain explicit follow-up items.

## FreeRTOS NTZ production milestone (superseded artifact snapshot)

This milestone was completed on 2026-07-30. Its five-leaf technical boundary
remains source-integrated, but the aggregate artifact, manifest, and coverage
pins recorded in this section are intentionally retained as the NTZ tranche
snapshot and have been superseded by the later dual-image littlefs
disk-version-parts release.

At this milestone, the production boundary intentionally stopped at five
context/exception assembly leaves. It did not claim a complete pristine-kernel
link. The
5,487-byte MIT-licensed adapter
`components/apollo_main/core_overlay/runtime_freertos_ntz_port.S` has
SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
Its authenticated upstream comparator remains the 11,686-byte V10.5.1
`portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s`, Git blob
`4d02a431e1d759f12f50e70fc55a7b0b4d368e89`, SHA-256
`eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f`,
from commit `def7d2df2b0506d3d249334974f51e427c17a41c`, tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`. This source pin is the
authenticated reconstruction baseline, not a claim about Even's historical
checkout.

Apple Clang 21.0.0 targets `arm-none-eabi` with
`-mcpu=cortex-m55 -mthumb -ffreestanding -fno-builtin
-ffunction-sections -fdata-sections -fno-unwind-tables
-fno-asynchronous-unwind-tables -Wall -Wextra -Werror`. The relocatable ELF
contains an empty generic `.text`, five two-byte-aligned executable
`PROGBITS` sections, no local pool/tail, and only four undefined symbols.

| Function section | Runtime span | Bytes | Raw ELF body SHA-256 | Relocated stock/expected SHA-256 |
|---|---|---:|---|---|
| `vRestoreContextOfFirstTask` | `[0x005FA058,0x005FA07E)` | 38 | `6cd49195f965664fa52a501576fafc8f84a77f4719cf755515ef7606b3a1d8be` | `10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8` |
| `vRaisePrivilege` | `[0x005FA07E,0x005FA08C)` | 14 | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` |
| `vStartFirstTask` | `[0x005FA08C,0x005FA0A4)` | 24 | `28d1d6e471df04ae8476e1355225e2d4d3673d4af90b68338fc8589441ae16b7` | `44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347` |
| `PendSV_Handler` | `[0x005FA0C8,0x005FA120)` | 88 | `12c7f208de16f3d5636cd00d8307847552937eb484b86b185b45b686553953ee` | `d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3` |
| `SVC_Handler` | `[0x005FA120,0x005FA132)` | 18 | `1807cfce5ab3df565e585de5dd35011f18e5994e748363f15cb7376aa796e1c4` | `d0fac197473b52d6ed466462d237ddb20dd8096a6507ea559e75d4bd9d88da94` |

The exact six relocation records are:

1. `vRestoreContextOfFirstTask+0x00 R_ARM_THM_PC8` to
   `open_cfw_freertos_px_current_tcb_literal` at `0x005FA134`, requiring
   bytes `204a0720`;
2. `vStartFirstTask+0x00 R_ARM_THM_PC8` to
   `open_cfw_freertos_vtor_literal` at `0x005FA138`, requiring bytes
   `08ed00e0`;
3. `PendSV_Handler+0x18 R_ARM_THM_PC8` to the same `0x005FA134` word;
4. `PendSV_Handler+0x2E R_ARM_THM_CALL` to `vTaskSwitchContext` at
   `0x004551B4`;
5. `PendSV_Handler+0x3A R_ARM_THM_PC8` to the same `0x005FA134` word; and
6. `SVC_Handler+0x0E R_ARM_THM_JUMP24` to `vPortSVCHandler_C` at
   `0x00442134`.

The pool remains `[0x005FA132,0x005FA13C)`, containing
`pxCurrentTCB=0x20074A20` and `SCB_VTOR=0xE000ED08`; vectors remain SVC
`0x005FA121` and PendSV `0x005FA0C9`. The ordered 182 relocated bytes have
SHA-256
`ca6be773f86c12eea198872e73541d97ce6bb806e2d03c57c1f540ad43c1e2fd`.

The `in_place_leaves` safety contract keeps these names out of the appended
overlay ABI and `patch_sites`, compiles each fixed-address leaf separately,
requires exact source/compiler/stock/output pins and the complete ordered
relocation list, authenticates referenced literal bytes, and rejects overlap,
range drift, or changed original bytes. That preserves exception/vector
addresses and avoids a new redirect in the timing-sensitive path.

The milestone's appended overlay was 114,324 bytes with SHA-256
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`;
the 3,637,720-byte provider had SHA-256
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`;
the 4,415,834-byte package had SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`.
The component report recorded 182 source-owned in-place bytes, 114,506 total
source-owned bytes, and 3,443,066 opaque base bytes.

The milestone manifest had 750 placed, two unresolved, and five
container-only regions,
with flash-plan SHA-256
`eda45c2cc276bd70bc123267d9fbdc09b0ae4aa030a7557f874c259ca7f5fee8`.
It classified 114,820 source bytes (2.600188%), 81,477 generated bytes
(1.845110%), 4,219,537 opaque bytes (95.554702%), and 196,297 controlled
bytes (4.445298%).

Focused production tests passed 23/23 in 18.333 seconds; linker and inherited
focused tests passed 21/21 in 0.705 seconds. The standard source build and
core-source manifest verification passed. Three output-isolated lanes under
`build/repro-freertos-ntz-output-{a,b,c}` reproduced the main and boot
overlays/providers, package, and flash plan byte-for-byte; lane temporary
manifests were moved to Trash. All 248 Apollo-main tests passed in 582.904
seconds. `./make.sh test` passed all 1,838 tests in 1,038.709 seconds,
including all six CMSIS constructor compile-closure tests. No hardware was
accessed.

The historical disk-version-parts aggregate superseded only those artifact
and ownership pins at that tranche: main overlay/provider were
114,346/3,637,742 bytes with
SHA-256
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`
and
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`;
boot overlay/provider are 302/148,902 bytes with SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`
and
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`.
That tranche's 4,415,876-byte package had SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`;
its 757/2/5 manifest produces a 546,404-byte flash plan with SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`.
Its package ownership was 114,860 source, 81,523 generated, 4,219,493 opaque,
and 196,383 controlled bytes. These historical values are superseded by the
later littlefs allocator, CMSIS message-queue and mutex-constructor production
tranches documented in `../source-coverage.md`.

The separately authenticated CMSIS-FreeRTOS v10.5.1 plus CMSIS_5 5.9.0
whole-file snapshot remains candidate-only and non-production-ready. The
independently bounded `osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew`
leaves have since been integrated into production; the statement here applies
only to the broader whole-file snapshot and unrelated services. The bounded
semaphore leaf closes through production `vQueueDelete` and `heap_4`.
Candidate-only shims
at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
provide `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}` and
compile the authenticated, unmodified `cmsis_os2.c` for Cortex-M55 with
`-Oz -Werror`. The retained candidate closure totals 370 text bytes:
`IRQ_Context` 46, `osMessageQueueNew` 88, `osMutexNew` 98, and
`osSemaphoreNew` 138. It retains zero read-only or writable data and four
8-byte EHABI `.ARM.exidx` sections; 6/6 isolated tests pass in 0.231 seconds.

This proves only candidate compile closure. It does not establish the
historical G2 checkout or stock byte identity. No authenticated G2 RTE/device
header exists; `SystemCoreClock` and MVE remain unresolved; `INCLUDE_*`
switches are compile-only assumptions; assert, NVIC, and libc seams remain
outside the retained root; and candidate `StaticTask_t` is 108 bytes versus
the 112-byte stock G2 TCB. Apache-2.0 wrapper/header notices and the FreeRTOS
MIT notice remain in force.

The broader constructor-candidate inventory intentionally retains its four
EHABI records as evidence about the complete candidate translation unit. That
policy is distinct from the production mini-link strict-leaf policy used by
the EasyLogger output/async chain: for one selected function, the extractor
authenticates only the exact 8-byte `.ARM.exidx` CANTUNWIND companion and its
local-section `R_ARM_PREL31` binding, then deliberately discards that metadata
rather than appending it as executable closure. It rejects personality/data,
non-CANTUNWIND, and cross-function variants. Existing production in-place
assembly rules remain separate and do not acquire unwind-personality support.

## Preceding production missed-yield source boundary

The next exact task leaf is FreeRTOS-Kernel V10.5.1
`vTaskMissedYield`. Authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c` defines the complete operation
as `xYieldPending = pdTRUE`. The official G2 function is ten bytes at
`[0x004555E6,0x004555F0)`, with SHA-256
`8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d`.
Its only callers are `0x00441FA2` and `0x00441FD8`.

Focused disassembly recovers `xYieldPending` at `0x20074A44`. The leaf
contains no configuration-sensitive branch: it performs one volatile
32-bit `BaseType_t` store of `pdTRUE` and returns. This is enough to admit a
bounded source adaptation without claiming the scheduler path that later
consumes the flag.

The canonical 14-byte source leaf is placed at
`[0x007B0800,0x007B080E)`. The resulting 115,946-byte overlay and
3,639,342-byte Apollo-main component hash to
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`
and
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`.
Main builder accounting is 116,128 source-owned bytes including 182 in
place, 81,636 generated patch bytes, 81,818 replaced-stock bytes, and
3,441,546 opaque bytes. The 4,417,796-byte package hashes to
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.

Homebrew clang 22.1.8 emits the same leaf bytes at
`[0x007B0F38,0x007B0F46)` after two profile-specific alignment bytes. Its
aggregate uses separate fail-closed Linux pins; the source-root sensitivity
of unrelated TLSF `__FILE__` data is documented in
[`../linux-reproducible-build.md`](../linux-reproducible-build.md).

## Preceding production event-item and mutex-held source boundary

Authenticated FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` makes both current task leaves
unequivocal:

| Function | Official span | Size | SHA-256 | Direct caller |
|---|---|---:|---|---|
| `uxTaskResetEventItemValue` | `[0x00455ACA,0x00455AE0)` | 22 | `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049` | `0x0047ECCE` |
| `pvTaskIncrementMutexHeldCount` | `[0x00455AE0,0x00455AF6)` | 22 | `3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f` | `0x00441D46` |

Both preserve separate volatile current-TCB evaluations through
`pxCurrentTCB=0x20074A20`. Reset pins the event-list item value at TCB
offset `+0x18`, priority at `+0x2C`, and `configMAX_PRIORITIES=56`.
Mutex-held pins `uxMutexesHeld` at `+0x64` and confirms
`configUSE_MUTEXES=1`.

The canonical reset leaf is 26 bytes at `[0x007B0810,0x007B082A)`, SHA-256
`04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6`.
The canonical mutex-held leaf is 24 bytes at
`[0x007B082C,0x007B0844)`, SHA-256
`494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf`.
Two generated alignment bytes precede each.

The resulting 116,000-byte overlay, 3,639,396-byte component, and
4,417,850-byte package hash to
`203b31ea09e03c919da51b4d194cab2c3325ad5d5eed3efc7464018af90e2059`,
`78375130a88e6ec0d14bc936b8f16f4535056344288419baba83d81fd4f3bdc3`,
and
`9ffe927fdb587db9fae07043d7dc0938d2519c95d29e71cd0dca021cadf31d85`.
Builder accounting is 116,182 source-owned bytes including 182 in place,
81,680 generated patch bytes, 81,862 replaced-stock bytes, and 3,441,502
opaque bytes.

Package ownership is 116,802 source, 83,473 generated, and 4,217,575 opaque
bytes; 200,275 bytes are controlled. Its 604,237-byte flash plan hashes to
`c25b80e357274ee25903c74d6472cb0a3ab30d6f5d702a053b88c145e3ddd521`
and records 838 placed, two unresolved, and five container-only regions.

Homebrew clang 22.1.8 places reset at
`[0x007B0F48,0x007B0F62)` and mutex-held at
`[0x007B0F64,0x007B0F7C)`. Its 117,848-byte overlay, 3,641,244-byte
component, and 4,419,698-byte package carry the separate fail-closed pins
documented in
[`../linux-reproducible-build.md`](../linux-reproducible-build.md). Complete
focused evidence is in
[`freertos-reset-event-item-value-source-boundary-audit.md`](freertos-reset-event-item-value-source-boundary-audit.md)
and
[`freertos-mutex-held-source-boundary-audit.md`](freertos-mutex-held-source-boundary-audit.md).

## Prior production scheduler-suspend and timeout-state source boundary

The next production tranche reuses authenticated FreeRTOS-Kernel V10.5.1
`vTaskSuspendAll` and `vTaskInternalSetTimeOutState` from the same commit.
Focused disassembly recovers only the target-specific kernel words, ordering,
and timeout-state ABI:

| Function | Official span | Bytes | SHA-256 | Recovered seam |
|---|---|---:|---|---|
| `vTaskSuspendAll` | `[0x00454D7C,0x00454D88)` | 12 | `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2` | volatile `uxSchedulerSuspended` at `0x20074A58`, 32-bit wrapping increment, compiler and memory barriers |
| `vTaskInternalSetTimeOutState` | `[0x00455556,0x00455566)` | 16 | `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` | signed `xNumOfOverflows` at `0x20074A48`, unsigned `xTickCount` at `0x20074A34`, 8-byte/4-aligned `TimeOut_t` fields at `+0` and `+4` |

The timeout leaf preserves overflow-read/store before tick-read/store. Its
four direct callers are `0x00441886`, `0x00441B90`, `0x00441CBC`, and
`0x004555D0`; no alternate entry, interior transfer, or stored function
pointer reaches the span. Apple clang 21 and Homebrew clang 22.1.8 emit the
same relocation-free 18-byte body, SHA-256
`8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a`.

Canonical placement is `[0x007B0844,0x007B0854)` for the 16-byte suspend
leaf and `[0x007B0854,0x007B0866)` for the 18-byte timeout leaf, with no
intervening padding. Linux places the byte-identical leaves at
`[0x007B0F7C,0x007B0F8C)` and `[0x007B0F8C,0x007B0F9E)`.

The current fail-closed production pins are:

| Profile / artifact | Bytes | SHA-256 |
|---|---:|---|
| canonical overlay | 116,034 | `d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd` |
| canonical Apollo-main component | 3,639,430 | `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc` |
| canonical core-source package | 4,417,884 | `e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7` |
| Linux overlay | 117,882 | `5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326` |
| Linux Apollo-main component | 3,641,278 | `6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163` |
| Linux core-source package | 4,419,732 | `a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4` |

The overlay records 596 functions and 563 patch sites. Builder accounting is
116,216 source-owned bytes including 182 in place, 81,708 generated patch
bytes, 81,890 replaced-stock bytes, and 3,441,474 opaque bytes. Package
ownership is 116,836 source, 83,501 generated, and 4,217,547 opaque bytes;
200,337 bytes are controlled. The 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

The Linux aggregate retains the recorded source root
`/Users/kalani/Repo/SybilSightABCD` because unrelated TLSF data embeds
absolute `__FILE__`. Complete timeout evidence is in
[`freertos-timeout-state-source-boundary-audit.md`](freertos-timeout-state-source-boundary-audit.md);
the scheduler-suspend boundary is documented separately in
`freertos-suspend-all-source-boundary-audit.md`.

## Prior queue/task closure configuration milestone

The recovered configuration now supports production
`xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace` from authenticated FreeRTOS-Kernel V10.5.1.
The first two reuse the already pinned queue/list/TCB layout, scheduler
globals, interrupt-mask providers, and yield policy. The stack helper adds
four explicit selections: `tskSTACK_FILL_BYTE=0xA5`,
`portSTACK_GROWTH=-1`, four-byte `StackType_t`, and two-byte
`configSTACK_DEPTH_TYPE`.

Apple's 119,066-byte overlay hashes to
`da056ac28814f1b07c90d3651b290cd459bfde5e3cbcf30fed9a75a72729a0ae`;
Linux's 120,942-byte overlay hashes to
`8d56bdf484f3b1d67378f53eef89d7aea88282c6d552b8b2b1ee2bb7e0cb6905`.
The corresponding packages are 4,420,916 and 4,422,792 bytes with SHA-256
`1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2`
and
`b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea`.
The Linux package was reproduced twice under the reviewed exact-root profile.
This remains offline structural qualification; no G2 hardware was accessed.

## Current timeout-check configuration milestone

Production `xTaskCheckForTimeOut` closes the timeout-specific configuration
questions with instruction-level evidence. The stock body compares the full
32-bit wait value against `UINT32_MAX` and returns false on equality before
reading overflow state, proving `INCLUDE_vTaskSuspend=1`, 32-bit
`TickType_t`, and `portMAX_DELAY=UINT32_MAX`. It proceeds directly from
elapsed-time computation to that test without the current-TCB aborted-delay
load/clear block, independently confirming `INCLUDE_xTaskAbortDelay=0`.

The source leaf preserves the already recovered `TimeOut_t` ABI: eight bytes,
four-byte alignment, signed overflow count at `+0`, and unsigned entry tick
at `+4`. It binds `xTickCount=0x20074A34`,
`xNumOfOverflows=0x20074A48`, assertion mask `0x005FA0A4`, critical entry
and exit `0x004420D0`/`0x004420E8`, and the source-owned internal snapshot at
`0x00455556`. No additional configuration default is inferred.

Apple's current 119,204-byte overlay hashes to
`4b3071e64d0e183efbb59788c94dca8ae01fba6d952aecbb9682893844171a79`;
Linux's 121,080-byte overlay hashes to
`75054c31d8ca3e50659443c470f11a604fb715db430e08b3ad4c468042282324`.
The corresponding packages are 4,421,054 and 4,422,930 bytes with SHA-256
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`
and
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
Two fail-closed builds per profile reproduced all retained artifacts. This is
offline structural qualification only; no G2 was connected, signed, flashed,
reset, booted, or executed.
