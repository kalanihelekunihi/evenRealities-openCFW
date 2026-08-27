# Bootloader core-overlay notices

`runtime_format_core.c`, `runtime_log_dispatch.c`, `runtime_strstr.c`,
`runtime_critical_context.c`, `runtime_gate_acquire.c`, and
`runtime_gate_state.c`, `runtime_gate_release.c`, and
`runtime_context_value.c`, `runtime_dispatch_4160fe.c`, and
`runtime_value_4161c6.c`, `runtime_call_4161ce.c`, and
`runtime_action_416200.c`, `runtime_transfer_41623a.c`, and
`runtime_wait_4162c4.c`, `runtime_notify_416378.c`, and
`runtime_callback_41639a.c` and `runtime_register_4163b2.c` are
GPL-3.0-or-later
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

`runtime_semaphore_create_416762.c` is the GPL-3.0-or-later clean-room openCFW
implementation of the complete authenticated semaphore-constructor entry at
`[0x00416762,0x00416816)`. Offline registration authorizes no hardware action.

`runtime_queue_create_416816.c` is the GPL-3.0-or-later clean-room openCFW
implementation of the complete authenticated message-queue constructor at
`[0x00416816,0x004168A2)`. Offline registration authorizes no hardware action.

`runtime_queue_put_4168a2.c` and `runtime_queue_get_416920.c` are bounded
Apache-2.0 adaptations of CMSIS-FreeRTOS v10.5.1 `osMessageQueuePut` and
`osMessageQueueGet`. They replace the complete authenticated entries
`[0x004168A2,0x00416920)` and `[0x00416920,0x0041699A)` while retaining the
reviewed FreeRTOS queue-provider seams. Offline registration authorizes no
hardware action.

`runtime_bit_width_4169a4.c`, `runtime_ctz_4169e2.c`, and
`runtime_log2_4169f2.c` are GPL-3.0-or-later clean-room openCFW source for the
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
GPL-3.0-or-later clean-room source for the bounded S200 bootloader
`redirect_init` two-mutex initialization entry. The implementation is derived
from independently recovered functional behavior in the authenticated G2
2.2.6.10 image; it does not incorporate or relicense retained vendor bytes.
Its external compatibility seams are the existing CMSIS-RTOS2 `osMutexNew`
and EasyLogger `elog_output` entries plus the two recovered SRAM handle words.
The neighboring proprietary IAR `FILE` wrappers remain retained and outside
this notice. Offline compilation and registration authorize no signing,
flashing, reset, boot, or hardware operation.

`runtime_aeabi_memset.c` and `runtime_aeabi_memset.h` are openCFW
GPL-3.0-or-later clean-room source for the bounded bootloader Arm EABI
byte-fill entry. The implementation is derived from independently recovered
register and loop behavior in the authenticated G2 2.2.6.10 image; it does not
incorporate or relicense retained vendor bytes. Offline compilation and
registration authorize no signing, flashing, reset, boot, or hardware
operation.

`runtime_strcspn.c`, `runtime_strspn.c`, and `runtime_string_spans.h` are
openCFW GPL-3.0-or-later clean-room source for the bounded bootloader reject-
set and accept-set string-span entries. The implementations are derived from
independently recovered loop and return-value behavior in the authenticated G2
2.2.6.10 image; they do not incorporate or relicense retained vendor bytes.
Offline compilation and registration authorize no signing, flashing, reset,
boot, or hardware operation.

`runtime_crc32.c` and `runtime_crc32.h` are openCFW GPL-3.0-or-later
clean-room source for the bounded bootloader reflected CRC-32 update entry.
The implementation is derived from independently recovered update behavior
and authenticated polynomial/table identity in the G2 2.2.6.10 image; it does
not incorporate or relicense retained vendor bytes. Offline compilation and
registration authorize no signing, flashing, reset, boot, or hardware
operation.

`runtime_store_200270cc.c` and `runtime_store_200270cc.h` are openCFW
GPL-3.0-or-later clean-room source for the bounded bootloader word setter whose
authenticated target is SRAM address `0x200270CC`. The implementation is
derived from independently recovered store behavior and does not incorporate
or relicense retained vendor bytes. Offline compilation and registration
authorize no signing, flashing, reset, boot, or hardware operation.

`runtime_memcmp.c` and `runtime_memcmp.h` are openCFW GPL-3.0-or-later
clean-room source for the bounded bootloader byte-comparison entry. The
implementation is derived from independently recovered comparison behavior in
the authenticated G2 2.2.6.10 image; it does not incorporate or relicense
retained vendor bytes. Offline compilation and registration authorize no
signing, flashing, reset, boot, or hardware operation.

`runtime_aeabi_memcpy.c` and `runtime_aeabi_memcpy.h` are openCFW
GPL-3.0-or-later clean-room source for the bounded bootloader Arm EABI
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
GPL-3.0-or-later clean-room source for the
bounded bootloader numeric-runtime entries. The implementations are derived
from independently recovered arithmetic, digit-counting, parsing, formatting,
string-length, repeated-output, floating conversion, and variadic formatter
behavior
in the authenticated G2 2.2.6.10 image; they do not incorporate or relicense
retained vendor bytes. Offline compilation and registration authorize no
signing, flashing, reset, boot, or hardware operation.

`runtime_format_core.c` binds the GPL-3.0-only clean-room formatter body in
`components/apollo_main/core_overlay/log_format_core.c` to the bootloader's
independently recovered helper and CRLF-control ABI. That shared source is
openCFW code; its reuse does not relicense any retained vendor byte.

`runtime_submit_41649a.c`, `runtime_create_4164da.c`,
`runtime_flags_set_41652e.c`, `runtime_flags_wait_416590.c`,
`runtime_flags_create_416610.c`, `runtime_handle_acquire_4166aa.c`, and
`runtime_handle_release_416710.c` are GPL-3.0-or-later clean-room openCFW
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

`runtime_easylogger_transport_41b854.c` is a GPL-3.0-or-later clean-room
implementation of the G2-specific EasyLogger channel-one output driver and
four-channel synchronous descriptor transport. It was recovered from the
authenticated control flow and ABI behavior and incorporates no retained
vendor implementation bytes. Its absolute channel-table, zeroing,
lower-transfer, and wait seams are compatibility bindings. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no output transmission, signing, flashing, reset, boot, or other
hardware operation.

`runtime_boot_services_41f9d8.c` is a GPL-3.0-or-later clean-room openCFW
implementation of the complete authenticated delay-wrapper, initializer
priority-comparator, and bounded initializer-runner entries at
`[0x0041F9D8,0x0041FA40)`. It incorporates no retained vendor implementation
bytes. Its raw-delay, copy, sort, callback-table, and SRAM scratch addresses
are G2 compatibility seams. Registration authorizes offline compilation and
unsigned package assembly only; it authorizes no signing, flashing, reset,
boot, callback execution, or other hardware operation.

`runtime_guarded_teardown_41fa98.c` is a GPL-3.0-or-later clean-room openCFW
implementation of the complete authenticated guarded teardown entry at
`[0x0041FA98,0x0041FAD0)`. It incorporates no retained vendor implementation
bytes. Its guard byte, two status stages, state-word setter, pin-configuration
word, and pin-configure entry are G2 compatibility seams. Registration
authorizes offline compilation and unsigned package assembly only; it
authorizes no signing, flashing, reset, boot, pin mutation, power transition,
or other hardware operation.

`runtime_platform_setup_41fa50.c` is a GPL-3.0-or-later clean-room openCFW
implementation of the complete authenticated boot platform-setup entry at
`[0x0041FA50,0x0041FA98)`. It incorporates no retained vendor implementation
bytes. Its guarded-teardown, reset, mode, VFP derive, copy, stock
configuration, submit, and channel entries are G2 compatibility seams.
Registration authorizes offline compilation and unsigned package assembly
only; it authorizes no signing, flashing, reset, boot, configuration submit,
channel mutation, or other hardware operation.

`runtime_pin_groups_41fadc.c` is a GPL-3.0-or-later clean-room openCFW
implementation of the complete authenticated two-bank pin-group dispatcher at
`[0x0041FADC,0x0041FCF6)`. It incorporates no retained vendor implementation
bytes. Its SRAM configuration table and pin-configure entry are G2
compatibility seams. Registration authorizes offline compilation and unsigned
package assembly only; it authorizes no signing, flashing, reset, boot,
pinmux/GPIO mutation, or other hardware operation.
