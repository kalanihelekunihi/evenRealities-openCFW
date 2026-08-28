# Bootloader core-overlay notices

`runtime_format_core.c`, `runtime_log_dispatch.c`, `runtime_strstr.c`,
`runtime_critical_context.c`, `runtime_gate_acquire.c`, and
`runtime_gate_state.c`, `runtime_gate_release.c`, and
`runtime_context_value.c`, `runtime_dispatch_4160fe.c`, and
`runtime_value_4161c6.c`, `runtime_call_4161ce.c`, and
`runtime_action_416200.c`, `runtime_transfer_41623a.c`, and
`runtime_wait_4162c4.c`, `runtime_notify_416378.c`, and
`runtime_callback_41639a.c` and `runtime_register_4163b2.c` are
MIT
clean-room openCFW compatibility implementations of the recovered bootloader
logging formatter, variadic dispatch, substring-search, critical-context,
runtime-state gate-acquisition, state-mapping, release, context-value
dispatch, address-identified runtime-dispatch, retained-value forwarding, and
validated runtime-call, guarded runtime-action, two-phase runtime-transfer,
masked runtime-wait, optional runtime-notification, registered runtime-callback,
and registered runtime-object construction
ABIs. They do not incorporate or
relicense retained official bootloader bytes. Their authenticated stock
boundaries, SRAM bindings, caller topology, generated redirects, and compiler
profiles are recorded in the adjacent evidence and research documents.

The shared
`components/apollo_main/core_overlay/runtime_littlefs_util.c`,
`components/apollo_main/core_overlay/runtime_littlefs_util_bitops.c`, and
`components/apollo_main/core_overlay/runtime_littlefs_util_endian.c`, plus
`runtime_littlefs_scmp.c`, `runtime_littlefs_alloc_ckpoint.c`, and
`runtime_littlefs_alloc_drop.c` in this directory, together with the shared
`components/apollo_main/core_overlay/runtime_littlefs_disk_version.c`,
`components/apollo_main/core_overlay/runtime_littlefs_mlist_isopen.c`,
`components/apollo_main/core_overlay/runtime_littlefs_mlist_append.c`, and
`components/apollo_main/core_overlay/runtime_littlefs_mlist_remove.c`, plus
`components/apollo_main/core_overlay/runtime_littlefs_disk_version_parts.c`
and
`components/apollo_main/core_overlay/runtime_littlefs_alloc_lookahead.c`, are
bounded, freestanding ports of the exact `lfs_max`, `lfs_min`,
`lfs_aligndown`, `lfs_alignup`, `lfs_npw2`, `lfs_ctz`, `lfs_popc`,
`lfs_fromle32`, `lfs_tole32`,
`lfs_frombe32`, and `lfs_tobe32` utility leaves and private `lfs_scmp`,
`lfs_alloc_ckpoint`, `lfs_alloc_drop`, `lfs_fs_disk_version`,
`lfs_fs_disk_version_major`, `lfs_fs_disk_version_minor`,
`lfs_alloc_lookahead`, `lfs_mlist_isopen`, `lfs_mlist_append`, and
`lfs_mlist_remove` leaves from littlefs v2.10.1,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`.

Copyright (c) 2022, The littlefs authors.
Copyright (c) 2017, Arm Limited. All rights reserved.

Their BSD-3-Clause terms are retained in
`third_party/littlefs/LICENSE.md`; each source file retains the upstream
copyright and SPDX identifier.
The shared utility source has SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`.
The shared metadata-list predicate source has SHA-256
`7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c`.
The shared endian-conversion source has SHA-256
`830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac`.
The shared fallback-bitops source has SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
The shared disk-version-parts source has SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
The shared allocator-lookahead source has SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.

The bootloader also compiles
`components/shared/easylogger/runtime_easylogger_helpers.c` and
`runtime_easylogger_helpers.h`, source-equivalent bounded adaptations of
EasyLogger's `get_fmt_enabled`, argument-aware unsigned and pointer format
predicates, and `elog_strcpy` from authenticated commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. They are 4,975 and 6,505
bytes with SHA-256 values
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
Copyright (c) 2015-2019 Armink. Their MIT terms remain in
`third_party/easylogger/LICENSE` and the shared source files.

`components/shared/easylogger/runtime_easylogger_helper_seams.c` is a
7,068-byte MIT-licensed openCFW image-binding adapter with SHA-256
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It binds the shared algorithms to the recovered bootloader logger object and
assertion policy. Official assertion strings, hook globals,
diagnostic-output entries, and wait wrappers remain proprietary compatibility
seams and are not relicensed by this notice.

The bootloader overlay also compiles the complete, unmodified
`third_party/ambiqsuite-apollo510/mcu/apollo510/hal/mcu/am_hal_mspi.c`
translation unit from AmbiqSuite 5.1.0 commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. Section garbage collection
retains only the exact-upstream `am_hal_mspi_interrupt_clear` leaf and
discards unrelated code and private `g_MSPIState`.

Ambiq's BSD-3-Clause copyright and license terms are retained in
`third_party/ambiqsuite-apollo510/LICENSE`. The reached Arm CMSIS Core
headers are pinned at commit
`d23a6949a0331ca96853bcd98b0fdcc4db47184c`; their Apache-2.0 terms are
retained in `third_party/cmsis-core/LICENSE.txt`.

The source-equivalent MSPI command-queue pause and high-priority DMA adapters
in `runtime_mspi_cq_pause_423fb8.c` and `runtime_mspi_program_dma_42403e.c`
also carry the AmbiqSuite BSD-3-Clause SPDX designation. They preserve the
authenticated G2 ABI and exact target instruction bodies for the corresponding
AmbiqSuite 5.1.0 private helpers; the same complete BSD terms above apply.

The bootloader also compiles
`components/shared/littlefs/runtime_littlefs_tag_chunk.c` and its header, a
bounded altered BSD-3-Clause adaptation of private `lfs_tag_chunk` from the
authenticated littlefs v2.10.1 source-equivalent baseline at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The files retain the upstream
copyright and SPDX identifier; complete unchanged terms remain at
`third_party/littlefs/LICENSE.md`.

The recovered bootloader stock range, four callers, scalar ABI, overlay
placement, and generated full-span redirect are openCFW compatibility
evidence rather than proof of the precise historical vendor checkout. This
pure scalar leaf does not import a block-device port or authorize signing,
flashing, filesystem format or erase, or hardware operation.

The bootloader also compiles
`components/shared/littlefs/runtime_littlefs_tag_isvalid.c` and
`runtime_littlefs_tag_type1.c` with their headers. They are bounded altered
BSD-3-Clause adaptations of the private `lfs_tag_isvalid` and `lfs_tag_type1`
definitions from authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Upstream copyright and SPDX
notices are retained, and the unchanged terms remain at
`third_party/littlefs/LICENSE.md`.

The recovered stock ranges, scalar ABI, caller sets, placement, and generated
redirects are openCFW compatibility evidence. The selected commit is a
source-equivalent baseline, not proof of the precise historical vendor
checkout. These leaves import no block-device, mount, format, or erase path;
their offline registration does not authorize signing, flashing, reset, boot,
filesystem mutation, or hardware operation.

The bootloader also compiles
`components/shared/littlefs/runtime_littlefs_tag_type3.c` and its header, a
bounded altered BSD-3-Clause adaptation of private `lfs_tag_type3` from
authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The files retain the upstream
copyright and SPDX identifier; complete unchanged terms remain at
`third_party/littlefs/LICENSE.md`.

The complete stock range, 17-caller set, scalar ABI, placement, and generated
full-span redirect are openCFW compatibility evidence rather than proof of
the precise historical vendor checkout. This leaf imports no block-device,
mount, format, or erase path; its offline registration does not authorize
signing, flashing, reset, boot, filesystem mutation, or hardware operation.

The bootloader also compiles
`components/shared/littlefs/runtime_littlefs_tag_id.c` and its header, a
bounded altered BSD-3-Clause adaptation of private `lfs_tag_id` from
authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The files retain the upstream
copyright and SPDX identifier; complete unchanged terms remain at
`third_party/littlefs/LICENSE.md`.

The complete eight-byte boot stock range, 41-caller set, 32-bit scalar ABI,
placement, and generated full-span redirect are openCFW compatibility evidence
rather than proof of the precise historical vendor checkout. This mask-and-
shift leaf imports no filesystem object, block-device, mount, format, program,
or erase path; its offline registration does not authorize signing, flashing,
reset, boot, filesystem mutation, or hardware operation.

The bootloader's current BSD-3-Clause adaptation is
`components/shared/littlefs/runtime_littlefs_tag_size.c` and its header,
selected from private `lfs_tag_size` at authenticated littlefs v2.10.1 commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Complete unchanged terms remain
at `third_party/littlefs/LICENSE.md`.

The production compatibility evidence covers only the six-byte boot stock span
`[0x00410BC0,0x00410BC6)`, its 14 direct callers, the matching 15-caller main
homolog, and the pure unsigned low-ten-bit mask. Placement and aggregate pins
are closed in the explicit evidence ledgers; the tag-ID registration remains
the settled preceding milestone. This promotion imports no
filesystem object, block-device, mount, format, program, or erase path and
authorizes no signing, flashing, reset, boot, filesystem mutation, or hardware
operation.
`runtime_hw_register_services_4236ce.c` is a MIT clean-room
openCFW implementation of three authenticated per-instance register services
in `[0x004236CE,0x00423764)`. It incorporates no retained vendor implementation
bytes. Type identity, bank selection and register offsets are G2 compatibility
seams. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, register/MMIO
access, service invocation, or other hardware operation.
`runtime_hw_service_dispatch_42377c.c` is a MIT clean-room openCFW
implementation of the authenticated per-instance service dispatcher at
`[0x0042377C,0x0042382C)`. It incorporates no retained vendor implementation
bytes. Interrupt flags, register progress, callbacks and service state are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
interrupt/register/SRAM/MMIO access, callback invocation, or other hardware
operation.
`runtime_memory_exchange_423864.c` is a MIT clean-room openCFW
implementation of the authenticated bounded memory-exchange helpers at
`[0x00423864,0x00423928)`. It incorporates no retained vendor implementation
bytes. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, device, SRAM,
MMIO, or other hardware operation.
`runtime_memory_rotate_front_423928.c` is a MIT clean-room openCFW
implementation of the authenticated bounded rotate-to-front helper at
`[0x00423928,0x00423972)`. It incorporates no retained vendor implementation
bytes. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, device, SRAM,
MMIO, or other hardware operation.
`runtime_memory_sort3_423972.c` is a MIT clean-room openCFW
implementation of the authenticated three-element comparator/exchange helper
at `[0x00423972,0x004239C2)`. It incorporates no retained vendor implementation
bytes and authorizes no signing, flashing, reset, boot, or hardware operation.
`runtime_memory_heap_sift_4239c2.c` is a MIT clean-room openCFW
implementation of the authenticated Floyd max-heap sift helper at
`[0x004239C2,0x00423A48)`. It incorporates no retained vendor implementation
bytes and authorizes no signing, flashing, reset, boot, or hardware operation.
`runtime_memory_qsort_423a48.c` is a MIT clean-room openCFW
implementation of the authenticated introspective qsort core and public
wrapper at `[0x00423A48,0x00423D20)`. It incorporates no retained vendor
implementation bytes and authorizes no signing, flashing, reset, boot, or
hardware operation.
`runtime_hw_control_services_423d20.c` is a MIT clean-room
openCFW implementation of six authenticated global hardware-control services
in `[0x00423D20,0x00423E0C)`. It incorporates no retained vendor implementation
bytes. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, register,
interrupt, SRAM, MMIO, or other hardware operation.
`runtime_hw_control_state_423e14.c` is a MIT clean-room openCFW
implementation of the authenticated hardware-control state mapper at
`[0x00423E14,0x00423E40)`. It incorporates no retained vendor implementation
bytes. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, device, SRAM,
MMIO, interrupt, or other hardware operation.
`runtime_mspi_fifo_write_423e40.c` and
`runtime_mspi_fifo_read_423e8a.c` are MIT clean-room openCFW
implementations of the authenticated MSPI FIFO services at
`[0x00423E40,0x00423F28)`. `runtime_mspi_cq_init_423f28.c`,
`runtime_mspi_cq_term_423f54.c`, and `runtime_mspi_cq_control_423f8e.c` are
MIT clean-room implementations of the adjacent command-queue
lifecycle through `0x00423FB8`. They incorporate no retained vendor
implementation bytes. Their retained status-check and Ambiq command-queue
provider entries remain compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, FIFO, command-queue, clock, register, SRAM, MMIO, or
other hardware operation.
`runtime_hw_clock_divider_422e28.c` is a MIT clean-room openCFW
implementation of the authenticated per-instance clock-divider service at
`[0x00422E28,0x00422EE2)`. It incorporates no retained vendor implementation
bytes. The reference clocks, per-instance MMIO, divider effects and physical
rate accuracy are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, clock/MMIO access, service invocation, or other hardware
operation.
`runtime_hw_descriptor_init_422dc6.c` is a MIT clean-room
openCFW implementation of the authenticated per-instance dual-descriptor
initializer at `[0x00422DC6,0x00422E28)`. It incorporates no retained vendor
implementation bytes. The instance storage, retained descriptor constructor,
DMA/controller state, buffer ownership and timing are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, descriptor/DMA access,
service invocation, or other hardware operation.
`runtime_hw_fifo_4232c8.c` and `runtime_hw_fifo_drain_423342.c` are
MIT clean-room openCFW implementations of the authenticated
per-instance FIFO read, write and drain services at
`[0x004232C8,0x00423350)`. They incorporate no retained vendor implementation
bytes. FIFO flags/data, register banks and concurrent peripheral behavior are
G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, FIFO/MMIO access, service invocation, or other hardware operation.
`runtime_hw_fifo_adapters_423350.c` is a MIT clean-room openCFW
implementation of the authenticated critical-section FIFO snapshot and pump
adapters at `[0x00423350,0x004233E0)`. It incorporates no retained vendor
implementation bytes. FIFO flags/data, retained descriptors, interrupt state,
register banks and concurrent peripheral behavior are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, FIFO/MMIO/descriptor
access, service invocation, or other hardware operation.
`runtime_hw_progress_423524.c` is a MIT clean-room openCFW
implementation of the authenticated primary and secondary progress services at
`[0x00423524,0x004236CE)`. It incorporates no retained vendor implementation
bytes. FIFO, descriptor, interrupt, callback, DMA and progress-mirror behavior
are G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, FIFO/descriptor/SRAM/MMIO access, callback invocation, or other hardware
operation.
`runtime_hw_mode_dispatch_4233e8.c` and `runtime_hw_mode_wait_423444.c` are
MIT clean-room openCFW implementations of all five authenticated
mode-dispatch executable bodies at `[0x004233E8,0x00423524)`. They incorporate
no retained vendor implementation bytes. Instance state, timeout/delay units,
interrupt state, register banks and concurrent peripheral behavior are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
MMIO/timer/peripheral access, service invocation, or other hardware operation.
`runtime_hw_status_map_422d7e.c` is a MIT clean-room openCFW
implementation of the authenticated per-instance status mapper at
`[0x00422D7E,0x00422DC6)`. It incorporates no retained vendor implementation
bytes. The MMIO bank, status flags, result pools and controller timing are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot, MMIO
access, service invocation, or other hardware operation.
`runtime_hw_shutdown_422fde.c` is a MIT clean-room openCFW
implementation of the authenticated per-instance register-quiesce and hardware
shutdown service at `[0x00422FDE,0x0042308E)`. It incorporates no retained
vendor implementation bytes. Register banks, clock/peripheral state, delay and
retained shutdown-provider effects are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, MMIO/clock/peripheral access,
service invocation, or other hardware operation.
`runtime_hw_config_latch_secondary_422f4c.c` is a MIT clean-room
openCFW implementation of the authenticated secondary per-instance
configuration-latch service at `[0x00422F4C,0x00422FA2)`. It incorporates no
retained vendor implementation bytes. Interrupt state, secondary-instance
ownership, payload consumers and retained critical-section behavior are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
interrupt/SRAM/MMIO access, service invocation, or other hardware operation.
`runtime_hw_config_release_secondary_422fa2.c` is a MIT
clean-room openCFW implementation of the authenticated secondary per-instance
configuration release at `[0x00422FA2,0x00422FDE)`. It incorporates no retained
vendor implementation bytes. Interrupt state, secondary-instance ownership,
retained memset and downstream consumers are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, interrupt/SRAM/MMIO
access, service invocation, or other hardware operation.

`runtime_mspi_interrupt_power_426536.S` is a BSD-3-Clause, reviewable Thumb-2
mnemonic realization of the authenticated AmbiqSuite 5.1.0
`am_hal_mspi_interrupt_service` and `am_hal_mspi_power_control` bodies at
`[0x00426536,0x004267FE)` and `[0x00426808,0x00426BFE)`. Both reviewed
compilers emit identical sections; strict named provider relocations reproduce
the two installed bodies exactly. It contains no raw executable encoding
directives. The intervening and trailing literal/alignment pools remain
separately retained official compatibility data. Registration authorizes
offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, MMIO access, interrupt servicing, power-state changes, or other hardware
operation.
`runtime_hw_register_clear_422d20.c` is a MIT clean-room openCFW
implementation of two authenticated per-instance register-clear leaves at
`[0x00422D20,0x00422D7A)`. It incorporates no retained vendor implementation
bytes. The MMIO bank is a G2 compatibility seam. Registration authorizes
offline compilation and unsigned package assembly only; it authorizes no
signing, flashing, reset, boot, MMIO access, leaf invocation, or other hardware
operation.

`runtime_mode_service_4216d4.c` is a MIT clean-room openCFW
implementation of the complete authenticated mode/configuration transaction
at `[0x004216D4,0x004217D2)`. It incorporates no retained vendor
implementation bytes. Fixed instance, controller, default configuration,
bitmap selector, state cells, retained calls, status policy and publication
ordering are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, interrupt/register/mode access, or other hardware
operation.

`runtime_semaphore_create_416762.c` is the MIT clean-room openCFW
implementation of the complete authenticated semaphore-constructor entry at
`[0x00416762,0x00416816)`. Offline registration authorizes no hardware action.

`runtime_queue_create_416816.c` is the MIT clean-room openCFW
implementation of the complete authenticated message-queue constructor at
`[0x00416816,0x004168A2)`. Offline registration authorizes no hardware action.

`runtime_queue_put_4168a2.c` and `runtime_queue_get_416920.c` are bounded
Apache-2.0 adaptations of CMSIS-FreeRTOS v10.5.1 `osMessageQueuePut` and
`osMessageQueueGet`. They replace the complete authenticated entries
`[0x004168A2,0x00416920)` and `[0x00416920,0x0041699A)` while retaining the
reviewed FreeRTOS queue-provider seams. Offline registration authorizes no
hardware action.

`runtime_bit_width_4169a4.c`, `runtime_ctz_4169e2.c`, and
`runtime_log2_4169f2.c` are MIT clean-room openCFW source for the
three complete authenticated 32-bit bit helpers at
`[0x004169A4,0x004169FC)`. Offline registration authorizes no hardware action.

`runtime_tlsf_block_primitives_4169fc.c` is a bounded freestanding adaptation
of Matthew Conte TLSF v3.1 under BSD-3-Clause. It implements only the twelve
block-header and pointer primitives matching the complete authenticated G2
entries at `[0x004169FC,0x00416AAA)`. Offline registration authorizes no
signing, flashing, reset, boot, heap mutation, or hardware operation.

`runtime_tlsf_block_topology_416aaa.c` is a bounded freestanding adaptation of
Matthew Conte TLSF v3.1 under BSD-3-Clause. It implements only the eight
physical-block, state-propagation, and alignment helpers matching the complete
authenticated G2 entries at `[0x00416AAA,0x00416BCE)`. Offline registration
authorizes no signing, flashing, reset, boot, heap mutation, or hardware
operation.

`runtime_tlsf_mapping_416bce.c` is a bounded freestanding adaptation of
Matthew Conte TLSF v3.1 under BSD-3-Clause. It implements only the three
request-size and first/second-level class-mapping helpers matching the complete
authenticated G2 entries at `[0x00416BCE,0x00416C4E)`. Offline registration
authorizes no signing, flashing, reset, boot, heap mutation, or hardware
operation.

`runtime_tlsf_free_lists_416c4e.c` is a bounded freestanding BSD-3-Clause
adaptation of Matthew Conte's TLSF v3.1 free-list selection and mutation
helpers for the authenticated G2 ILP32 allocator ABI. It preserves the
24×32 bitmap/list topology, sentinel links, assertion identities, and three
complete entries at `[0x00416C4E,0x00416E04)`. Offline registration authorizes
no signing, flashing, reset, boot, heap mutation, or hardware operation.

`runtime_tlsf_allocator_416e04.c` is a bounded freestanding BSD-3-Clause
adaptation of Matthew Conte TLSF v3.1. It implements the ten complete
authenticated allocator-operation entries at `[0x00416E04,0x0041711C)`,
including request adjustment, block split/trim/absorb/coalescing, free-block
lookup, and used-block preparation. Offline registration authorizes no
signing, flashing, reset, boot, heap mutation, or hardware operation.

`runtime_tlsf_public_41711c.c` is a bounded freestanding BSD-3-Clause
adaptation of Matthew Conte TLSF v3.1. It implements the seven complete
authenticated public allocator entries at `[0x0041711C,0x004172DA)`: control
construction, pool overhead/addition, create/create-with-pool, malloc, and
free. Offline registration authorizes no signing, flashing, reset, boot, heap
mutation, or hardware operation.

`runtime_redirect_init.c` and `runtime_redirect_init.h` are openCFW
MIT clean-room source for the bounded S200 bootloader
`redirect_init` two-mutex initialization entry. The implementation is derived
from independently recovered functional behavior in the authenticated G2
2.2.6.10 image; it does not incorporate or relicense retained vendor bytes.
Its external compatibility seams are the existing CMSIS-RTOS2 `osMutexNew`
and EasyLogger `elog_output` entries plus the two recovered SRAM handle words.
The neighboring proprietary IAR `FILE` wrappers remain retained and outside
this notice. Offline compilation and registration authorize no signing,
flashing, reset, boot, or hardware operation.

`runtime_aeabi_memset.c` and `runtime_aeabi_memset.h` are openCFW
MIT clean-room source for the bounded bootloader Arm EABI
byte-fill entry. The implementation is derived from independently recovered
register and loop behavior in the authenticated G2 2.2.6.10 image; it does not
incorporate or relicense retained vendor bytes. Offline compilation and
registration authorize no signing, flashing, reset, boot, or hardware
operation.

`runtime_strcspn.c`, `runtime_strspn.c`, and `runtime_string_spans.h` are
openCFW MIT clean-room source for the bounded bootloader reject-
set and accept-set string-span entries. The implementations are derived from
independently recovered loop and return-value behavior in the authenticated G2
2.2.6.10 image; they do not incorporate or relicense retained vendor bytes.
Offline compilation and registration authorize no signing, flashing, reset,
boot, or hardware operation.

`runtime_crc32.c` and `runtime_crc32.h` are openCFW MIT
clean-room source for the bounded bootloader reflected CRC-32 update entry.
The implementation is derived from independently recovered update behavior
and authenticated polynomial/table identity in the G2 2.2.6.10 image; it does
not incorporate or relicense retained vendor bytes. Offline compilation and
registration authorize no signing, flashing, reset, boot, or hardware
operation.

`runtime_store_200270cc.c` and `runtime_store_200270cc.h` are openCFW
MIT clean-room source for the bounded bootloader word setter whose
authenticated target is SRAM address `0x200270CC`. The implementation is
derived from independently recovered store behavior and does not incorporate
or relicense retained vendor bytes. Offline compilation and registration
authorize no signing, flashing, reset, boot, or hardware operation.

`runtime_memcmp.c` and `runtime_memcmp.h` are openCFW MIT
clean-room source for the bounded bootloader byte-comparison entry. The
implementation is derived from independently recovered comparison behavior in
the authenticated G2 2.2.6.10 image; it does not incorporate or relicense
retained vendor bytes. Offline compilation and registration authorize no
signing, flashing, reset, boot, or hardware operation.

`runtime_aeabi_memcpy.c` and `runtime_aeabi_memcpy.h` are openCFW
MIT clean-room source for the bounded bootloader Arm EABI
forward-copy entry. The implementation is derived from independently recovered
register and copy behavior in the authenticated G2 2.2.6.10 image; it does not
incorporate or relicense retained vendor bytes. Offline compilation and
registration authorize no signing, flashing, reset, boot, or hardware
operation.

`runtime_udiv10.c`, `runtime_udiv10.h`, `runtime_numeric.h`,
`runtime_udec_digits.c`, `runtime_sdec_digits.c`, `runtime_hex_digits.c`,
`runtime_parse_dec.c`, `runtime_u64_to_dec.c`, `runtime_u64_to_hex.c`,
`runtime_nullable_strlen.c`, `runtime_repeat_char.c`,
`runtime_float_to_fixed.c`, and `runtime_format_core.c` are openCFW
MIT clean-room source for the
bounded bootloader numeric-runtime entries. The implementations are derived
from independently recovered arithmetic, digit-counting, parsing, formatting,
string-length, repeated-output, floating conversion, and variadic formatter
behavior
in the authenticated G2 2.2.6.10 image; they do not incorporate or relicense
retained vendor bytes. Offline compilation and registration authorize no
signing, flashing, reset, boot, or hardware operation.

`runtime_format_core.c` binds the MIT clean-room formatter body in
`components/apollo_main/core_overlay/log_format_core.c` to the bootloader's
independently recovered helper and CRLF-control ABI. That shared source is
openCFW code; its reuse does not relicense any retained vendor byte.

`runtime_submit_41649a.c`, `runtime_create_4164da.c`,
`runtime_flags_set_41652e.c`, `runtime_flags_wait_416590.c`,
`runtime_flags_create_416610.c`, `runtime_handle_acquire_4166aa.c`, and
`runtime_handle_release_416710.c` are MIT clean-room openCFW
implementations of the complete authenticated bootloader runtime/event-flags
entries at `[0x0041649A,0x00416762)`. They were recovered from observable
control flow and ABI behavior and do not incorporate or relicense retained
vendor bytes. Their registration authorizes offline compilation and package
assembly only; it authorizes no signing, flashing, reset, boot, or hardware
operation.

`runtime_easylogger_control_41733c.c`,
`runtime_easylogger_output_4176ce.c`, and
`runtime_easylogger_lock_enabled_417b7c.c`, and
`runtime_easylogger_port_41a648.c` are bounded freestanding MIT
adaptations of Armink EasyLogger commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. They implement the recovered G2
bootloader logger-state ABI, control/filter/lock behavior, interrupt-gated
formatted output, output-lock state reconciliation, mutex-backed boot-port
hooks, tick formatting, and RTOS task-name selection. G2-specific absolute
port and transport seams are compatibility bindings, not upstream code.
Offline compilation and package assembly authorize no signing, flashing,
reset, boot, output transmission, or hardware operation.

`runtime_easylogger_transport_41b854.c` is a MIT clean-room
implementation of the G2-specific EasyLogger channel-one output driver and
four-channel synchronous descriptor transport. It was recovered from the
authenticated control flow and ABI behavior and incorporates no retained
vendor implementation bytes. Its absolute channel-table, zeroing,
lower-transfer, and wait seams are compatibility bindings. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no output transmission, signing, flashing, reset, boot, or other
hardware operation.


`runtime_mspi_read_id_42059e.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G JEDEC-ID reader at
`[0x0042059E,0x004205F4)`. It incorporates no retained vendor implementation
bytes. The transaction and diagnostic entries are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, JEDEC/MSPI/XIP
mutation, or other hardware operation.

`runtime_mspi_read_transfer_4205f4.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G read-transfer
wrapper at `[0x004205F4,0x0042069E)`. It incorporates no retained vendor
implementation bytes. The handle word, blocking Ambiq MSPI transfer, and log
dispatch are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, external-flash/MSPI/XIP mutation, or other hardware
operation.

`runtime_mspi_write_transfer_42069e.c` is a MIT clean-room
openCFW implementation of the complete authenticated MX25U25643G
write-transfer wrapper at `[0x0042069E,0x0042074E)`. It incorporates no
retained vendor implementation bytes. The handle word, blocking Ambiq MSPI
transfer, and log dispatch are G2 compatibility seams. Registration authorizes
offline compilation and unsigned package assembly only; it authorizes no
signing, flashing, reset, boot, external-flash/MSPI/XIP mutation, or other
hardware operation.

`runtime_mspi_busy_status_42074e.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G busy-status reader
at `[0x0042074E,0x004207A2)`. It incorporates no retained vendor
implementation bytes. The source-routed read-transfer and logging entries are
G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, external-flash/MSPI/XIP mutation, or other hardware operation.

`runtime_mspi_wait_ready_4207a2.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G two-phase ready poll
and fixed-500 wrapper at `[0x004207A2,0x00420800)`. It incorporates no
retained vendor implementation bytes. Context, notification, delay, and busy
status entries are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, external-flash/MSPI/XIP mutation, or other hardware
operation.

`runtime_irq_services_41fdc0.c` is a MIT clean-room openCFW
implementation of the three complete authenticated IRQ-service entries at
`[0x0041FDC0,0x0041FE28)`. It incorporates no retained vendor implementation
bytes. NVIC/SCB register addresses, the MSPI handle word, and retained
AmbiqSuite MSPI status/clear/service entries are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, interrupt-controller or
MSPI mutation, or other hardware operation.

`runtime_mspi_control_41fe28.c` is a MIT clean-room openCFW
implementation of the complete authenticated MSPI enable/disable pair at
`[0x0041FE28,0x0041FE62)`. It incorporates no retained vendor implementation
bytes. The handle/active words and retained control entry are G2 compatibility
seams. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, MSPI mutation,
or other hardware operation.

`runtime_poll_delay_4216b2.c` is a MIT clean-room openCFW
implementation of the complete authenticated bounded poll-delay helper at
`[0x004216B2,0x004216D4)`. It incorporates no retained vendor implementation
bytes. The retained delay-provider address, duration, volatile flag/counter
contract, and ordering are G2 compatibility seams. Registration authorizes
offline compilation and unsigned package assembly only; it authorizes no
signing, flashing, reset, boot, timing/register access, or other hardware
operation.

`runtime_event_flags_service_41fe62.c` is a MIT clean-room
openCFW implementation of the complete authenticated event-flags service
initializer, acquire, and release cluster at `[0x0041FE62,0x0041FF08)`. It
incorporates no retained vendor implementation bytes. The SRAM handle, static
configuration, retained runtime service calls, and EasyLogger pointers are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot, RTOS
object mutation, logging, or other hardware operation.

`runtime_mspi_guard_41ff08.c` is a MIT clean-room openCFW
implementation of the complete authenticated paired MSPI guard wrappers at
`[0x0041FF08,0x0041FF34)`. It incorporates no retained vendor implementation
bytes. The event-flags entries, MSPI control entries, and `0x200271C5` bypass
byte are G2 compatibility seams. Registration authorizes offline compilation
and unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, RTOS or MSPI mutation, or other hardware operation.

`runtime_mspi_xip_config_41ff34.c` is a MIT clean-room openCFW
implementation of the complete authenticated MSPI XIP-config updater at
`[0x0041FF34,0x0041FF60)`. It incorporates no retained vendor implementation
bytes. The retained MSPI handle, configuration object, and control entry are
G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, XIP or MSPI mutation, or other hardware operation.

`runtime_bit_run_helpers_41ff60.c` is a MIT clean-room openCFW
implementation of the complete authenticated consecutive-one run-length and
center-selection helpers at `[0x0041FF60,0x00420002)`. It incorporates no
retained vendor implementation bytes. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, MSPI/training mutation, or other hardware operation.

`runtime_mspi_timing_scan_420002.c` is a MIT clean-room openCFW
implementation of the complete authenticated exhaustive MSPI timing scan at
`[0x00420002,0x004201BA)`. It incorporates no retained vendor implementation
bytes. The timing table, MSPI handle, control/read-ID entries, diagnostic
logger, and expected JEDEC ID are G2 compatibility seams; the two bit-run
helpers are separately source-owned. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, MSPI/XIP/timing mutation, or other hardware operation.

`runtime_mspi_timing_auto_4201ba.c` is a MIT clean-room openCFW
implementation of the complete authenticated automatic MSPI timing-selection
entry at `[0x004201BA,0x00420254)`. It incorporates no retained vendor
implementation bytes. The active timing object, diagnostic logger, and string
literals are G2 compatibility seams; the exhaustive timing scan is separately
source-owned. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, MSPI/XIP/timing
mutation, or other hardware operation.

`runtime_mspi_low_level_init_420254.c` is a MIT clean-room
openCFW implementation of the complete authenticated low-level MSPI
initializer at `[0x00420254,0x00420476)`. It incorporates no retained vendor
implementation bytes. The retained Ambiq-compatible HAL operations, MSPI
state/configuration objects, pin lookup, interrupt mask, and EasyLogger
pointers are G2 compatibility seams; XIP, pin-group, and NVIC helpers are
separately source-owned. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, MSPI/XIP/interrupt mutation, or other hardware operation.

`runtime_mspi_driver_init_420476.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G public initializer
at `[0x00420476,0x0042052A)`. It incorporates no retained vendor
implementation bytes. Retained device preparation, synchronization, JEDEC-ID
read, and final-mode helpers are G2 compatibility seams; low-level MSPI init,
delay, timing selection, event flags, and MSPI enable are separately
source-owned. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, JEDEC/MSPI/XIP
mutation, or other hardware operation.

`runtime_mspi_soft_reset_42052a.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G soft-reset sequence
at `[0x0042052A,0x0042059E)`. It incorporates no retained vendor
implementation bytes. The retained command helper and diagnostics are G2
compatibility seams; delays are separately source-owned. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, MSPI/XIP mutation, or other
hardware operation.

`runtime_boot_services_41f9d8.c` is a MIT clean-room openCFW
implementation of the complete authenticated delay-wrapper, initializer
priority-comparator, and bounded initializer-runner entries at
`[0x0041F9D8,0x0041FA40)`. It incorporates no retained vendor implementation
bytes. Its raw-delay, copy, sort, callback-table, and SRAM scratch addresses
are G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, callback execution, or other hardware operation.

`runtime_guarded_teardown_41fa98.c` is a MIT clean-room openCFW
implementation of the complete authenticated guarded teardown entry at
`[0x0041FA98,0x0041FAD0)`. It incorporates no retained vendor implementation
bytes. Its guard byte, two status stages, state-word setter, pin-configuration
word, and pin-configure entry are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, pin mutation, power transition,
or other hardware operation.

`runtime_platform_setup_41fa50.c` is a MIT clean-room openCFW
implementation of the complete authenticated boot platform-setup entry at
`[0x0041FA50,0x0041FA98)`. It incorporates no retained vendor implementation
bytes. Its guarded-teardown, reset, mode, VFP derive, copy, stock
configuration, submit, and channel entries are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, configuration submit,
channel mutation, or other hardware operation.

`runtime_pin_groups_41fadc.c` is a MIT clean-room openCFW
implementation of the complete authenticated two-bank pin-group dispatcher at
`[0x0041FADC,0x0041FCF6)`. It incorporates no retained vendor implementation
bytes. Its SRAM configuration table and pin-configure entry are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
pinmux/GPIO mutation, or other hardware operation.

`runtime_allocator_init_41fd70.c` is a MIT clean-room openCFW
implementation of the complete authenticated TLSF pool initializer at
`[0x0041FD70,0x0041FDA8)`. It incorporates no retained vendor implementation
bytes. Its pool, retained memory/TLSF/log entries, handle word, and diagnostic
pointers are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, SRAM mutation, allocator execution, logging, or other
hardware operation.
The clean-room MX25U25643G address-mode reader at
`[0x00420800,0x0042086C)` is also MIT first-party source and
incorporates no third-party implementation text.

The clean-room MX25U25643G enter-four-byte-mode service at
`[0x00420890,0x00420978)` is also MIT first-party source and
incorporates no third-party implementation text. Its fixed MSPI handle,
ready-poll, write-enable, command-transfer, address-mode, write-disable, and
logger entries are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, command submission, status-register mutation, or other
hardware operation.

The clean-room MX25U25643G write-enable and write-disable wrappers at
`[0x00420984,0x004209BE)` and `[0x004209C4,0x004209FC)` are also
MIT first-party source and incorporate no third-party
implementation text. Their command-transfer and logger entries are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
write-latch mutation, command submission, or other hardware operation.

`runtime_mspi_sector_erase_420a08.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G sector-erase service
at `[0x00420A08,0x00420ADA)`. It incorporates no retained vendor
implementation bytes. Its fixed handle, source-routed guard, serial/quad-mode,
ready-poll, write-latch, write-transfer, and diagnostic entries are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot, erase
command submission, external-flash mutation, or other hardware operation.

`runtime_mspi_program_420b0c.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G page-program service
at `[0x00420B0C,0x00420C14)`. It incorporates no retained vendor
implementation bytes. Its fixed handle, source-routed guard, serial/quad-mode,
ready-poll, write-latch, write-transfer, and diagnostic entries are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
program command submission, external-flash mutation, or other hardware
operation.

`runtime_mspi_quad_enable_420c5c.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G status-register-2
QE service at `[0x00420C5C,0x00420DFA)`. It incorporates no retained vendor
implementation bytes. Its fixed handle, ready-poll, read/write-transfer,
write-enable, logger, and diagnostic-string entries are G2 compatibility
seams. Registration authorizes offline compilation and unsigned package
assembly only; it authorizes no signing, flashing, reset, boot, status-register
mutation, external-flash command submission, or other hardware operation.

`runtime_mspi_device_reconfigure_420e08.c` is a MIT clean-room
openCFW implementation of the complete authenticated MSPI device
reconfiguration service at `[0x00420E08,0x00420E8C)`. It incorporates no
retained vendor implementation bytes. Its fixed handle/state cells, Ambiq HAL
disable/device-configure/enable entries, source-owned pin-group dispatcher,
logger, and diagnostic strings are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, pinmux or MSPI mutation, command
submission, or other hardware operation.

`runtime_littlefs_erase_421348.c` is a MIT clean-room openCFW
implementation of the complete authenticated LittleFS block-erase callback at
`[0x00421348,0x00421372)`. It incorporates no retained vendor implementation
bytes. Its partition mapping, source-owned MX25U25643G sector-erase service,
logger, diagnostic literal, and `LFS_ERR_IO` mapping are G2 compatibility
seams. The compiled leaf occupies separately authenticated generated NOP fill.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, erase, reset, boot, filesystem
mutation, external-flash command submission, or other hardware operation.

`runtime_mspi_read_420f70.c` is a MIT clean-room openCFW
implementation of the complete authenticated MX25U25643G guarded blocking-read
service at `[0x00420F70,0x00420FF2)`. It incorporates no retained vendor
implementation bytes. Its published handle, source-owned guard/mode/wait
services, read-descriptor ABI, and retained Ambiq HAL blocking-transfer entry
are G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, pinmux or MSPI mutation, external-flash command submission, or other
hardware operation.

`runtime_mspi_set_quad_mode_420e8c.c` is a MIT clean-room
openCFW implementation of the complete authenticated MX25U25643G quad-mode
selection service at `[0x00420E8C,0x00420F0C)`. It incorporates no retained
vendor implementation bytes. Its initialized-SRAM configuration template,
source-owned memcpy/reconfigure/XIP entries, retained Ambiq HAL control entry,
logger, and diagnostic strings are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, XIP/MSPI configuration, external
flash command submission, or other hardware operation.

`runtime_mspi_set_serial_mode_420f10.c` is a MIT clean-room
openCFW implementation of the complete authenticated MX25U25643G serial-mode
selection service at `[0x00420F10,0x00420F6A)`. It incorporates no retained
vendor implementation bytes. Its initialized-SRAM serial configuration,
source-owned reconfigure/XIP entries, retained Ambiq HAL control entry, logger,
and diagnostic strings are G2 compatibility seams. Registration authorizes
offline compilation and unsigned package assembly only; it authorizes no
signing, flashing, reset, boot, XIP/MSPI configuration, external-flash command
submission, or other hardware operation.

`runtime_fs_directories_4210c8.c` is a MIT clean-room openCFW
implementation of the complete authenticated LittleFS directory-bootstrap
service at `[0x004210C8,0x004211B0)`. It incorporates no retained vendor
implementation bytes. Its filesystem object, path table, LittleFS
directory-open/mkdir/close wrappers, and diagnostic literals are G2
compatibility seams; its logger call routes to source-owned EasyLogger.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, filesystem or
external-flash mutation, or other hardware operation.

`runtime_littlefs_format_4211b0.c` is a MIT clean-room openCFW
implementation of the complete authenticated LittleFS format, mount, and
directory-bootstrap orchestration service at `[0x004211B0,0x00421210)`. It
incorporates no retained vendor implementation bytes. Its filesystem object,
configuration, public LittleFS unmount/format/mount wrappers, and diagnostic
literals are G2 compatibility seams; its directory-bootstrap and logger calls
route to source-owned leaves. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, format,
erase, reset, boot, filesystem or external-flash mutation, or other hardware
operation.

`runtime_littlefs_init_421210.c` is a MIT clean-room openCFW
implementation of the complete authenticated LittleFS initializer, readiness,
and boot-counter service at `[0x00421210,0x004212D8)`. It incorporates no
retained vendor implementation bytes. Its filesystem/configuration/file
objects, public LittleFS wrappers, `boot_count` path, readiness word, and
diagnostic literals are G2 compatibility seams; its directory, recovery, and
logger calls route to source-owned leaves. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, format, erase, reset, boot, filesystem or external-flash mutation,
or other hardware operation.

`runtime_littlefs_read_4212d8.c` is a MIT clean-room openCFW
implementation of the complete authenticated LittleFS block-read callback at
`[0x004212D8,0x00421310)`. It incorporates no retained vendor implementation
bytes. Its fixed partition base, source-owned guarded MX25U25643G reader and
logging dispatcher, diagnostic literal, and `LFS_ERR_IO` mapping are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
filesystem read/write, external-flash command submission, or other hardware
operation.

`runtime_littlefs_program_421310.c` is a MIT clean-room openCFW
implementation of the complete authenticated LittleFS block-program callback
at `[0x00421310,0x00421348)`. It incorporates no retained vendor implementation
bytes. Its fixed partition base, source-owned MX25U25643G program service and
logging dispatcher, diagnostic literal, and `LFS_ERR_IO` mapping are G2
compatibility seams. The compiled leaf is placed only in authenticated
generated NOP fill inside a replaced stock body. Registration authorizes
offline compilation and unsigned package assembly only; it authorizes no
signing, flashing, reset, boot, filesystem write, external-flash command
submission, or other hardware operation.

`runtime_littlefs_sync_4213d4.c` is a MIT clean-room openCFW
implementation of the complete authenticated constant-success LittleFS sync
callback at `[0x004213D4,0x004213D8)`. It incorporates no retained vendor
implementation bytes. The compiled leaf occupies separately authenticated
generated NOP fill. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
filesystem mutation, external-flash command submission, or other hardware
operation.

`runtime_address_map_4213d8.c` is a MIT clean-room openCFW
implementation of the complete authenticated identity and thresholded
address-index helper bodies at `[0x004213D8,0x004213E6)`. It incorporates no
retained vendor implementation bytes. Both compiled leaves reproduce the
stock instruction bytes exactly at their authenticated addresses. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, memory mutation, or other
hardware operation.

`runtime_memory_select_copy_4213e6.c` is a MIT clean-room
openCFW implementation of the complete authenticated mapped-memory selector,
copy service, and odd-selector wrapper at `[0x004213E6,0x0042156E)`. It
incorporates no retained vendor implementation bytes. Mapped-memory roots,
control/security register addresses, selector values, capacity rules, status
codes, and retained copy-provider binding are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, register or mapped-
memory access, or other hardware operation.

`runtime_popcount_421584.c` is a MIT clean-room openCFW
implementation of the complete authenticated 32-bit population-count helper
at `[0x00421584,0x004215AE)`. It incorporates no retained vendor implementation
bytes, and both reviewed compilers reproduce the exact stock instruction body.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, register access, or
other hardware operation.

`runtime_bitmap_helpers_4215ae.c` is a MIT clean-room openCFW
implementation of the complete authenticated two-word bitmap nonempty,
membership, and population-count helpers at `[0x004215AE,0x00421632)`. It
incorporates no retained vendor implementation bytes, and both reviewed
compilers reproduce the exact installed stock instruction bodies. The table
root, low-byte selectors, two-word layout, and call to the population-count
helper are G2 compatibility seams. Registration authorizes offline compilation
and unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, table/register access, or other hardware operation.

`runtime_bitmap_update_421632.c` is a MIT clean-room openCFW
implementation of the complete authenticated validated bitmap update helper
at `[0x00421632,0x004216B2)`. It incorporates no retained vendor
implementation bytes, and both reviewed compilers reproduce the exact stock
instruction body. The table root, low-byte inputs, validation bounds, status
mapping, and read-modify-write behavior are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, table/register access,
or other hardware operation.

`runtime_dual_mode_service_4217d2.c` is a MIT clean-room openCFW
implementation of the complete authenticated dual-controller mode transaction
at `[0x004217D2,0x00421978)`. It incorporates no retained vendor
implementation bytes, and both reviewed compilers reproduce the exact stock
instruction body. Fixed instance/controller addresses, default configuration,
bitmap and state cells, status mapping, and retained provider bindings are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
controller/register access, mode transition, or other hardware operation.

`runtime_bitmap_clients_421978.c` is a MIT clean-room openCFW
implementation of the complete authenticated bitmap-client configuration and
row-mutation cluster at `[0x00421978,0x00421B08)`. It incorporates no retained
vendor implementation bytes, and both reviewed compilers reproduce the exact
stock instruction bodies. Controller-table, publication-cell, bitmap-row,
status and retained-provider bindings are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, controller/register or bitmap
access, client activation, or other hardware operation.

`runtime_mode1_services_421b08.c` is a MIT clean-room openCFW
implementation of the complete authenticated mode-one enable, last-client
disable and poll/state cleanup cluster at `[0x00421B08,0x00421BD2)`. It
incorporates no retained vendor implementation bytes, and both reviewed
compilers reproduce the exact stock instruction bodies. Controller-table,
control-word, bitmap-row, active/state-cell and retained-provider bindings are
G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, controller/register or bitmap access, mode activation, or other hardware
operation.

`runtime_mode0_enable_421bd2.c` is a MIT clean-room openCFW
implementation of the complete authenticated mode-zero client-enable
transaction at `[0x00421BD2,0x00421CCE)`. It incorporates no retained vendor
implementation bytes, and both reviewed compilers reproduce the exact stock
instruction body. Controller-table, row-two bitmap, active/state cells,
timeout, state-query/control and retained-provider bindings are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
controller/register or bitmap access, mode activation, or other hardware
operation.

`runtime_mode0_disable_421cce.c` is a MIT clean-room openCFW
implementation of the complete authenticated mode-zero client-disable and
poll/completion cleanup pair at `[0x00421CCE,0x00421D5E)`. It incorporates no
retained vendor implementation bytes, and both reviewed compilers reproduce
the exact stock instruction bodies. Row-two bitmap, control request,
active/completion/state cells and retained-provider bindings are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
controller/register or bitmap access, mode shutdown, or other hardware
operation.

`runtime_row4_enable_421d5e.c` is a MIT clean-room openCFW
implementation of the complete authenticated row-four client-enable
transaction at `[0x00421D5E,0x00421E4A)`. It incorporates no retained vendor
implementation bytes, and both reviewed compilers reproduce the exact stock
instruction body. Row-four bitmap, readiness, active/completion/state cells,
timeout and retained switch/apply bindings are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, controller/register or
bitmap access, mode activation, or other hardware operation.

`runtime_row4_disable_421e4a.c` is a MIT clean-room openCFW
implementation of the complete authenticated row-four client-disable and
poll/state cleanup pair at `[0x00421E4A,0x00421EBA)`. It incorporates no
retained vendor implementation bytes, and both reviewed compilers reproduce
the exact stock instruction bodies. Row-four bitmap, active/state cells and
retained switch-provider bindings are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, controller/register or bitmap
access, mode shutdown, or other hardware operation.

`runtime_row5_services_421eba.c` is a MIT clean-room openCFW
implementation of the complete authenticated row-five client enable/disable
pair at `[0x00421EBA,0x004220B2)`. It incorporates no retained vendor
implementation bytes, and both reviewed compilers reproduce the exact stock
instruction bodies. Bitmap, ready/selector/pending/active/state cells and
retained dual-provider bindings are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, controller/register or bitmap
access, mode activation/shutdown, or other hardware operation.

`runtime_mode_routes_4222f0.c` is a MIT clean-room openCFW
implementation of the authenticated seven-kind enable/disable routers,
selective all-row cleanup helper, and fixed configuration-copy body in
`[0x004222F0,0x00422430)`. It incorporates no retained vendor implementation
bytes; adjacent padding/literal pools stay separately retained official data,
and both reviewed compilers reproduce all four exact executable bodies. Row
bitmaps, row-service providers, the fixed configuration object, and retained
memcpy binding are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, controller/register or bitmap access, configuration
mutation, mode activation/shutdown, or other hardware operation.

`runtime_debug_services_422468.c` is a BSD-3-Clause implementation derived
from the public AmbiqSuite SDK 5.1.0 `am_hal_debug.c` behavior, copyright (c)
2025 Ambiq Micro, Inc., for the authenticated debug-disable, debug-power and
trace-disable bodies in `[0x00422468,0x00422574)`. Both reviewed compilers
reproduce all three exact executable bodies; adjacent literal pools remain
separately retained official data. Debug-domain power state, MCUCTRL/DCB
registers and retained HAL providers are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, power/register/trace access, or
other hardware operation.

`runtime_row6_services_4220b2.c` is a MIT clean-room openCFW
implementation of the authenticated row-six client enable/disable and
mode-family dispatcher bodies in `[0x004220B2,0x004222D2)`. It incorporates no
retained vendor implementation bytes; the two intervening literal seams stay
separately retained official data, and both reviewed compilers reproduce the
exact executable bodies. Bitmap, ready/selector/pending/handle cells and
retained lifecycle-provider bindings are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, controller/register or bitmap
access, mode activation/shutdown, or other hardware operation.
`runtime_constraint_memchr_422590.c` is a MIT clean-room openCFW
implementation of the authenticated constraint dispatcher and optimized
`memchr` bodies in `[0x00422590,0x00422628)`. It incorporates no retained vendor
implementation bytes; the intervening handler-address/message pool stays
separately retained official data, and both reviewed compilers reproduce the
exact executable bodies. The handler registration cell and retained default
handler are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, memory probing, handler invocation, or other hardware
operation.
`runtime_double_helpers_422628.c` is a MIT clean-room openCFW
implementation of thirteen authenticated IAR-compatible double-runtime bodies
in `[0x00422628,0x00422872)`. It incorporates no retained vendor
implementation bytes; the two-byte inter-function alignment stays separately
retained official data, and both reviewed compilers reproduce every executable
body exactly. The retained range-error tail, VFP state and soft-float caller
ABI are G2 compatibility seams. Registration authorizes offline compilation
and unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, VFP-state mutation, range-error invocation, or other hardware operation.
`runtime_thread_pointer_422874.c` is a MIT clean-room openCFW
implementation of the authenticated eight-byte IAR-compatible thread-pointer
body and runtime-anchor literal at `[0x00422874,0x0042287C)`. It incorporates
no retained vendor implementation bytes. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, SRAM access, or other hardware operation.
`runtime_u64_divmod_42287c.c` is a MIT clean-room openCFW
implementation of the authenticated 560-byte IAR-compatible unsigned 64-bit
divide/modulo runtime at `[0x0042287C,0x00422AAC)`. It incorporates no retained
vendor implementation bytes. The retained divide-by-zero tail and
four-register caller ABI are G2 compatibility seams. Registration authorizes
offline compilation and unsigned package assembly only; it authorizes no
signing, flashing, reset, boot, trap invocation, or other hardware operation.
`runtime_atomic_wrappers_422aac.c` is a MIT clean-room openCFW
implementation of the authenticated atomic snapshot, no-op and retained-query
bodies in `[0x00422AAC,0x00422AD2)`. It incorporates no retained vendor
implementation bytes. Interrupt state, volatile source and retained provider
are G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, interrupt mutation, provider invocation, or other hardware operation.
`runtime_hw_instance_init_422ad4.c` is a MIT clean-room openCFW
implementation of the authenticated four-instance hardware-service initializer
at `[0x00422AD4,0x00422BA8)`. It incorporates no retained vendor implementation
bytes. The SRAM pool, type words and lifecycle are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, SRAM/peripheral access,
initializer invocation, or other hardware operation.
`runtime_hw_instance_service_422ba8.c` is a MIT clean-room
openCFW implementation of the authenticated instance register-transfer and
lifecycle service at `[0x00422BA8,0x00422D20)`. It incorporates no retained
vendor implementation bytes. MMIO, revision, clock, mode-routing, teardown and
resource providers are G2 compatibility seams. Registration authorizes offline
compilation and unsigned package assembly only; it authorizes no signing,
flashing, reset, boot, MMIO/clock access, service invocation, or other hardware
operation.
`runtime_hw_config_latch_422ee2.c` is a MIT clean-room openCFW
implementation of the authenticated per-instance configuration-latch service
at `[0x00422EE2,0x00422F4C)`. It incorporates no retained vendor
implementation bytes. Interrupt state, instance ownership, payload consumers
and retained critical-section behavior are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, interrupt/SRAM/MMIO
access, service invocation, or other hardware operation.
