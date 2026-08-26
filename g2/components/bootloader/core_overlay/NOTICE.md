# Bootloader core-overlay notices

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
`runtime_nullable_strlen.c`, and `runtime_repeat_char.c` are openCFW
GPL-3.0-or-later clean-room source for the
bounded bootloader numeric-runtime entries. The implementations are derived
from independently recovered arithmetic, digit-counting, parsing, formatting,
string-length, and repeated-output behavior
in the authenticated G2 2.2.6.10 image; they do not incorporate or relicense
retained vendor bytes. Offline compilation and registration authorize no
signing, flashing, reset, boot, or hardware operation.
