# FreeRTOS-Kernel V10.5.1 authenticated snapshot

This directory contains an authenticated, byte-preserving subset of the
official
[`FreeRTOS/FreeRTOS-Kernel`](https://github.com/FreeRTOS/FreeRTOS-Kernel)
`V10.5.1` release. The annotated tag object
`d7b40dbed508c305c2a32ccf3982045ec9ba8734` peels to commit
[`def7d2df2b0506d3d249334974f51e427c17a41c`](https://github.com/FreeRTOS/FreeRTOS-Kernel/commit/def7d2df2b0506d3d249334974f51e427c17a41c)
and tree `7496dfa815c3cea2f45a090c6e92d113f494b930`.

The release tag is annotated but **not cryptographically signed**. The
authentication boundary is therefore the official repository URL, tag-object
identity, peeled commit and tree, and the independently pinned size, Git blob
SHA-1, and SHA-256 of every copied file. The offline verifier does not claim a
signed FreeRTOS release.

## Snapshot contents

The 49 pristine upstream files are kept at their original repository paths:

- all seven kernel implementation units: `tasks.c`, `queue.c`, `list.c`,
  `timers.c`, `event_groups.c`, `stream_buffer.c`, and `croutine.c`;
- every public/private kernel header shipped under `include/`;
- the complete upstream MIT license;
- `portable/Common/mpu_wrappers.c`;
- the complete released IAR Cortex-M55 port in
  `portable/IAR/ARM_CM55/{non_secure,secure}`;
- the complete released IAR Cortex-M55 no-TrustZone port in
  `portable/IAR/ARM_CM55_NTZ/non_secure`; and
- the exact released `portable/MemMang/heap_4.c` as an authenticated,
  unselected allocator reference; and
- the upstream portable-layer and Armv8-M selection notes.

The core set supports progressive source replacement of queue, task, list,
timer, event-group, and stream/message-buffer behavior without obtaining
upstream source during a build. `croutine.c` and its header are retained
because they are part of the complete V10.5.1 kernel core even when
`configUSE_CO_ROUTINES` is disabled.

The two IAR Cortex-M55 variants are alternatives. They must never be compiled
together.

## G2 configuration and port boundary

This vendor directory deliberately contains no G2-authored files and selects
neither portable variant. In particular, it excludes:

- `FreeRTOSConfig.h` and every recovered configuration constant;
- Ambiq Apollo510 CMSIS, device, interrupt, startup, and clock support;
- application hooks and the tick source;
- G2 linker configuration and assembly glue;
- selection, configuration, or production integration of any
  `portable/MemMang` task/application allocator, including the retained
  `heap_4.c` reference, and the openCFW TLSF adapter; and
- any ABI shim or address binding to official firmware.

Focused binary comparison now unequivocally selects the released
`ARM_CM55_NTZ/non_secure` port with TrustZone and MPU disabled and FPU context
support enabled. It also recovers `BASEPRI=0x30`, a 1,024-Hz Apollo STIMER
compare-A tick on IRQ 32, tickless idle, 56 priorities, 32-byte task names,
and the `heap_4` geometry. Both upstream alternatives remain preserved here
for authentication, but only `ARM_CM55_NTZ/non_secure` is eligible for the G2
port layer.

Before linking a full upstream kernel, openCFW must still provide a reviewed
G2 `FreeRTOSConfig.h`, Apollo STIMER tick/tickless glue, application hooks,
and a reviewed allocator selection, heap placement, and adapter. The retained
`heap_4.c` is source reference material only and is not compiled or linked by
this snapshot. Most importantly, pristine `tasks.c` is not drop-in:
the exact 112-byte G2 TCB has a vendor stack-depth word at offset `+0x54`.
That compatibility change must remain outside this pristine vendor tree.
MVE, the exact AmbiqSuite revision, and unrelated `INCLUDE_*` switches remain
unresolved. The proof and read-only verifier are documented in
`docs/research/freertos-g2-config-port-audit.md`.

The TrustZone-capable `ARM_CM55/secure` alternative retains upstream
`secure_heap.c`; that file manages secure contexts and is part of the complete
portable alternative. It does not select the kernel task/application allocator
used by `pvPortMalloc` and `vPortFree`.

## Integrated source boundaries

The Apollo overlay currently ports fourteen reviewed `queue.c` entries, four
`list.c` entries, and three task-state query leaves from `tasks.c` without
modifying this pristine snapshot. The list tranche replaces stock
`[0x0045607C,0x0045609A)`, `[0x0045609A,0x004560B2)`, and
`[0x004560E8,0x0045610E)`. These integrations are independent of the G2 port
and TCB extension and are verified against separately compiled copies of this
V10.5.1 source.
The two existing timer consumers still call the stock `uxListRemove` Thumb
identity, which now reaches the generated source redirect; their direct-call
conversion is deferred to a complete timer-cluster relink.

The bounded `tasks.c` adaptation
`components/shared/freertos/runtime_freertos_task_lists_initialize.c` now
replaces the complete Apollo-main `prvInitialiseTaskLists` span
`[0x0045568C,0x004556E0)`. Its authenticated upstream operation is the exact
899-byte `tasks.c[150869:151768]` slice, SHA-256
`0908b0fb7a1b43d6d4fa2bd8212ba069ac6a8d4d036b4f973ae7f3baa6dd6e63`.
The production entry `open_cfw_freertos_task_lists_initialize` preserves the
recovered 56 ready lists, five optional/scheduler lists, and two selector-word
stores, and its six relocations bind directly to source-owned
`open_cfw_freertos_list_initialise`. The distinct bootloader homolog is not
registered or patched. G2 RAM bindings and configuration selections are
compatibility evidence, not upstream provenance.

The production overlay also source-assembles the released
`ARM_CM55_NTZ/non_secure` interrupt-mask pair from a sectionized,
Clang-syntax MIT adaptation in
`components/apollo_main/core_overlay/runtime_freertos_interrupt_mask.S`
(SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`).
The resulting byte-exact `ulSetInterruptMask` and `vClearInterruptMask`
sections replace the fixed official spans
`[0x005FA0A4,0x005FA0BA)` and `[0x005FA0BA,0x005FA0C8)`, whose SHA-256
values are respectively
`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`
and
`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`.
Independent relocation-free copies are also retained at
`[0x007B00D8,0x007B00EE)` and `[0x007B00EE,0x007B00FC)` so new source can
bind directly to either leaf without changing the fixed public entries.

## Offline verification

Run:

```sh
python3 openCFW/third_party/freertos-kernel/verify_snapshot.py
```

The verifier reads only this directory. It checks the exact subtree
inventory, provenance boundary, kernel/version markers, port alternatives,
license text, and every upstream file against its hard-coded byte count, Git
blob identity, and SHA-256. It performs no network access and does not execute
or link the kernel.

## License

FreeRTOS-Kernel V10.5.1 is distributed under the MIT license. The complete,
unchanged upstream license is retained as `LICENSE.md`, and the source and
header files retain their upstream notices.
