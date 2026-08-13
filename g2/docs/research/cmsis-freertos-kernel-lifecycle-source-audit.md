# G2 CMSIS-FreeRTOS kernel-lifecycle source audit

Status: production source-integrated as one writer-coupled closure  
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: offline firmware/source analysis, host execution, and dual-profile
reproducible builds; no signing, flashing, or hardware access

## Result

The last two stock-backed public functions in the linked CMSIS-FreeRTOS object
are now source-owned together:

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `osKernelInitialize` | `[0x0044903C,0x0044906C)` | 48 | `70065824750aff11e5e4b17a7996f4aa72d42be6a4739515a6b7a22d5679b775` |
| `osKernelStart` | `[0x00449094,0x004490CC)` | 56 | `01d0e472c73fbab1af81f34ee5916c26978d5358e7a24075b790028aeabe8911` |

Both wrappers access the same volatile CMSIS `KernelState` word at
`0x20074384`; the already source-owned `osKernelGetState` reads that word.
Admission is therefore atomic. `osKernelInitialize` changes inactive (`0`) to
ready (`1`) only in thread context while FreeRTOS reports not-started (`1`).
`osKernelStart` accepts only ready/not-started, writes running (`2`) before
entering the scheduler, and returns the exact CMSIS status values (`0`, `-1`,
or `-6`).

The stock `SVC_Setup` entry at `[0x0044900C,0x0044900E)` is exactly `bx lr`
(`7047`, SHA-256
`c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8`).
The source therefore preserves its configured no-op semantics without a
retained call. Trace-recorder and heap-5 setup are absent from the G2 build,
matching the recovered compile configuration.

## Dependency closure

The two leaves use only reviewed boundaries:

| Dependency | Ownership/boundary |
|---|---|
| `IRQ_Context` | source-owned `open_cfw_cmsis_irq_context` |
| `xTaskGetSchedulerState` | source-owned `open_cfw_freertos_task_get_scheduler_state`; stock oracle `[0x004558A4,0x004558C4)` |
| CMSIS `KernelState` | fixed volatile word `0x20074384`, shared with source-owned get-state |
| `vTaskStartScheduler` | authenticated retained `[0x00454CEC,0x00454D7C)`, 144 bytes, SHA-256 `2fabf4882dc6db88c73cd573ba3f454e7f6f0cafb1329670ad52e39ef1cbe01d`; subsequently recreated as a production-excluded dual-profile V10.5.1 candidate |

The retained scheduler-start body is pristine FreeRTOS V10.5.1 control flow
over G2 task/global and port seams. Keeping it retained avoids pretending that
the Apollo STIMER, trace/hook, idle/timer task creation, and scheduler-global
RAM layout are already source-migrated. The later scheduler-start candidate
now closes the core algorithm while preserving exactly those explicit seams;
production still retains the stock provider. The wrapper boundary itself is
fully closed and does not widen that claim.

## Provenance

The source oracle is Arm CMSIS-FreeRTOS v10.5.1 annotated-tag commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Its exact 70,106-byte
`cmsis_os2.c` blob was first introduced by commit
`13acfbef7be85119fc6bc56832c455d4547d92c7`. The separately authenticated
FreeRTOS kernel is V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. As elsewhere in the wrapper
census, those are the correct reconstruction pins; source-identical later
commits and dead-stripped changes prevent proving Even's unique private
checkout from this binary alone.

The Apache-2.0 bounded implementation is
`runtime_cmsis_kernel_lifecycle.c`: 2,385 bytes, SHA-256
`ec75881048b6fd4536baaed046cc1c5aeb00909b3cac58dbf7bdba1d91140f24`.
Selector macros compile initialization and start as independent relocated
leaves while retaining one reviewed source unit for the shared-state policy.

## Target and production pins

| Profile/item | Size / offset | Linked SHA-256 |
|---|---:|---|
| Apple initialize | 50 / 137,260 | `2da493da67483c1f6fdb77b7958fcb79d531948b24d77ab8f7d7a31967a4c1ab` |
| Apple start | 56 / 137,312 | `e6b14852638048830f9777c1ada618148fc0c7a0e9ff69859a48cebb67eadf60` |
| Linux initialize | 50 / 139,140 | `7c915db88585f25e0f03db84a3ed7aa950c7b9de1862d71fadf50cb7c8651e70` |
| Linux start | 56 / 139,192 | `7f61a7b8b6cb04c286cd3ddf7baef6c3bfa9d64a886053b3966353b29aac0f15` |

Both profiles emit identical unrelocated leaves: initialize SHA-256
`c5cc9f2380f5bbaa4d4ac610d4e104765fa52abb227ed06ef24069d81b2257a8`
and start SHA-256
`f2ee18ec358566d7e41cb39c682ac2db5c2131ff9c8ac4fafb0bdb75fa0b8c09`.
Initialize has call relocations at offsets 2 and 16. Start adds the retained
`0x00454CEC` scheduler call at offset 42.

Canonical Apple overlay/component/package roots are respectively
`137368` / `442b4efd0192cb01f35db01db32248bd9c0d27c39b47f3f5a354da55382e670b`,
`3660764` / `0bd818eab6e12b465711a2fe0e8f23db1d885b5f58ae0396e3eaa709b24efb0c`,
and `4439258` / `16c879e54526237f7e2cad3200cc1f99cc535510b7d4ea7e67128a1af2b491d0`.
Reviewed Linux roots are `139248` / `8b33add5721bf8e91b432ac8ff5383d8ddf51d502febe92768ccc46c645c9da8`,
`3662644` / `533735a474831cae79dbec297789dd639ecbbd06d0c2f085b4d4aad19d99df0f`,
and `4441138` / `a38542adb130ad8a9bbb2b4d1d693ff61d3b2a859ce009d135caadbbf8a906ef`.

## Verification

Six host/target tests pin source and fixture bytes, all state and IRQ gates,
the single initialization transition, the write-before-scheduler-call order,
both target relocation contracts, stock spans, the retained provider, both
compiler profiles, production redirects, and manifest regions. The manifest
also now classifies the previously hidden 40-byte generated
`osKernelGetState` redirect. CMSIS wrapper production ownership is complete:
38/38 public linked APIs and 5/5 private helpers.

Run:

```sh
make -C openCFW cmsis-freertos-kernel-lifecycle
```
