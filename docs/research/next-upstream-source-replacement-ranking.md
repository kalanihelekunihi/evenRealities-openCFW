# Next authenticated upstream source-replacement ranking

Status: research-only recommendation; no production overlay, manifest,
release pin, shared coverage document, or firmware artifact changed

Scope: official G2 `2.2.6.10` Apollo-main and bootloader images after the
FreeRTOS queue-creation cluster and AmbiqSuite
`am_hal_mspi_interrupt_clear`; offline authenticated-source comparison,
existing focused disassembly evidence, and source-candidate tests only

## Subsequent production status

This ranking is a historical planning snapshot. The queue wrappers and
FreeRTOS interrupt-mask wave have since entered production; `pcTaskGetName`
remains unintegrated, although its source-mask dependency is no longer a
blocker. The exact MIT-licensed FreeRTOS-Kernel V10.5.1 mask pair is assembled
from the sectionized Clang-syntax source
`runtime_freertos_interrupt_mask.S` (SHA-256
`28f16b37970b5529fe63cf250365b955b0c65fe2a016efda1ba718ee3b768de5`).
Its byte-exact in-place ranges are `[0x005FA0A4,0x005FA0BA)`
(`f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323`)
and `[0x005FA0BA,0x005FA0C8)`
(`97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a`),
and independent copies occupy `[0x007B00D8,0x007B00EE)` and
`[0x007B00EE,0x007B00FC)`.

## Decision

The next ten small functions do not need algorithm decompilation. Their
implementations are unequivocally available from authenticated upstream
source. Focused disassembly is still required at the integration boundary:
it proves exact stock spans, selected compile-time branches, ABI offsets,
outgoing dependencies, caller topology, and safe redirect ownership.

The recommended production waves are:

1. `xQueueCreateMutexStatic` plus the four-function littlefs scalar tranche;
2. both counting-semaphore creation wrappers;
3. the FreeRTOS interrupt-mask pair; and
4. `pcTaskGetName`, after its source assertion relocation can bind directly
   to the source-owned set-mask leaf.

This order retires the functions with no mutable private state or unresolved
configuration first. It also keeps source-closed pairs together:
`lfs_alignup -> lfs_aligndown`, the two counting wrappers, and the
task-name/assertion port boundary.

Across the official images, the ten functions occupy 276 stock bytes:
126 bytes of queue wrappers, 80 bytes for the four littlefs functions
duplicated in main and boot, and 70 bytes for the task-name/mask group.
Generated overlay sizes may differ and must be pinned by the production
build rather than inferred from these stock sizes.

## Ranked functions

| Rank | Function | Authenticated upstream | Official range(s) | Stock bytes | Readiness and remaining focused check |
|---:|---|---|---|---:|---|
| 1 | `xQueueCreateMutexStatic` | FreeRTOS-Kernel V10.5.1 `queue.c` | main `[0x004416F0,0x00441710)` | 32 | Ready. Both callees are source-owned; verify its two target relocations bind directly to the source static creator and mutex initializer, not through stock redirects. |
| 2 | `lfs_max` | littlefs v2.10.1-equivalent `lfs_util.h` | main `[0x004CA6F8,0x004CA700)`; boot `[0x00410400,0x00410408)` | 8 each | Ready. Pure unsigned scalar selector; recheck the two complete-image entry/interior scans after redirects are registered. |
| 3 | `lfs_min` | littlefs v2.10.1-equivalent `lfs_util.h` | main `[0x004CA700,0x004CA708)`; boot `[0x00410408,0x00410410)` | 8 each | Ready. Pure unsigned scalar selector; no configuration, literal, state, or relocation. |
| 4 | `lfs_aligndown` | littlefs v2.10.1-equivalent `lfs_util.h` | main `[0x004CA708,0x004CA714)`; boot `[0x00410410,0x0041041C)` | 12 each | Ready. Confirm production target uses 32-bit unsigned division and retains the upstream nonzero-alignment precondition. |
| 5 | `lfs_alignup` | littlefs v2.10.1-equivalent `lfs_util.h` | main `[0x004CA714,0x004CA720)`; boot `[0x0041041C,0x00410428)` | 12 each | Ready only with rank 4 in the same source tranche. Inspect the sole branch relocation and require it to resolve to source `lfs_aligndown`. |
| 6 | `xQueueCreateCountingSemaphoreStatic` | FreeRTOS-Kernel V10.5.1 `queue.c` | main `[0x00441790,0x004417C2)` | 50 | Ready with rank 7. Verify unsigned `initial <= maximum`, queue type `2`, item size `0`, successful-result store at `Queue_t + 0x38`, and the reviewed assertion seam. |
| 7 | `xQueueCreateCountingSemaphore` | FreeRTOS-Kernel V10.5.1 `queue.c` | main `[0x004417C2,0x004417EE)` | 44 | Ready with rank 6. Confirm allocation failure returns null before the `+0x38` store and bind the creator call directly to the current source implementation. |
| 8 | `ulSetInterruptMask` | FreeRTOS-Kernel V10.5.1 IAR `ARM_CM55_NTZ/non_secure/portasm.s` | main `[0x005FA0A4,0x005FA0BA)` | 22 | Source candidate is byte-exact. Before redirecting 181 callers, preserve `BASEPRI=0x30`, DSB/ISB order, return of the old mask in `r0`, and measure the added redirect latency or prefer an exact source-generated in-place body. |
| 9 | `vClearInterruptMask` | same authenticated FreeRTOS port | main `[0x005FA0BA,0x005FA0C8)` | 14 | Source candidate is byte-exact. Preserve the independently callable entry at `0x005FA0BA` and confirm all 12 callers pass the saved mask in `r0`. |
| 10 | `pcTaskGetName` | FreeRTOS-Kernel V10.5.1 `tasks.c` | main `[0x00454F16,0x00454F38)` | 34 | Ready after rank 8. Recheck fixed `pxCurrentTCB=0x20074A20`, `pcTaskName=+0x34`, 32-byte name extent, vendor stack-depth word at `+0x54`, and source-bind the fatal assertion call to rank 8. |

Ranks indicate review and integration risk, not doubt about source identity.
Ranks 2 through 5 should be one dual-image release even though the pure
call-free selectors can be reviewed independently. Ranks 6 and 7 share one
validation and assertion policy and should not be split without a concrete
size constraint. Ranks 8 and 9 are listed late because they have broad
caller fan-in and are timing-sensitive, not because their code is uncertain.

## Upstream identity, version, and license

| Library | Reusable pin | Authentication qualification | License |
|---|---|---|---|
| FreeRTOS-Kernel | V10.5.1, commit `def7d2df2b0506d3d249334974f51e427c17a41c`, tree `7496dfa815c3cea2f45a090c6e92d113f494b930` | Official annotated tag, commit, tree, selected Git blobs, and copied SHA-256 values are pinned. The tag is not cryptographically signed. | MIT |
| littlefs | v2.10.1 source-equivalent release, commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`, tree `06dd0162169d3cb550cd24a3e34d0e4d02983ad3` | The complete assertion fingerprint identifies the release generation, and the selected helper expressions match exactly. The stripped binary cannot prove which of three object-equivalent historical source states Even used, so the pin is a source-equivalent baseline rather than a historical-checkout claim. | BSD-3-Clause |

The relevant authenticated file hashes are:

| File | Bytes | SHA-256 |
|---|---:|---|
| `third_party/freertos-kernel/queue.c` | 125,614 | `5cdf4fa35fe059446effff5bf20deaf83ddffb08921bc198fda106b1d17dd894` |
| `third_party/freertos-kernel/tasks.c` | 223,695 | `14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463` |
| `third_party/freertos-kernel/portable/IAR/ARM_CM55_NTZ/non_secure/portasm.s` | 11,686 | `eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f` |
| `third_party/littlefs/lfs_util.h` | 7,954 | `f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e` |

No new library needs to be imported for this tranche. The license files,
provenance records, offline snapshot verifiers, bounded candidate sources,
and focused target/host tests are already present.

## Exact stock-body authentication

| Function | Stock SHA-256 |
|---|---|
| `xQueueCreateMutexStatic` | `2977000da7aab5b87abce1270dca6518785de04a1e72d08082802713d478fd28` |
| `xQueueCreateCountingSemaphoreStatic` | `a46100f23dd51b8276a4c2ebafa1ba96c6813114810ae0f5297764c20368eb62` |
| `xQueueCreateCountingSemaphore` | `ed30ebca04b655b1ec31e60296d977382d0712057db88f99b205a555b374120f` |
| `lfs_max` | `3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464` |
| `lfs_min` | `7ec81166f84c44a60f4ecf93ad37d93f52ec00c77bb5db5a7dda659b1319c8a3` |
| `lfs_aligndown` | `d0d7407bcf93abaef33623047467d1230d2176ce9b4a4e93bfcd8adde884f349` |
| `lfs_alignup` | `18874b0eb5cf5c7bd6f20b2b29f787157294b9e9be16d14ab0d9064d44a97c37` |
| `ulSetInterruptMask` | `f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323` |
| `vClearInterruptMask` | `97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a` |
| `pcTaskGetName` | `a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817` |

The four littlefs body hashes are identical between main and boot. Their
complete 274-byte utility clusters are also identical, which independently
supports the shared upstream identity and compiler-configuration reading.

## Configuration and ABI gaps

No unresolved parameter blocks ranks 1 through 7.

The recovered queue configuration is sufficient for the three wrappers:
static and dynamic allocation are enabled, mutexes and counting semaphores
are enabled, `StaticQueue_t` and `Queue_t` are 80 bytes, the current count is
at `+0x38`, the counting queue type is `2`, and trace/coverage creation hooks
are empty. The counting wrappers retain the already reviewed G2
`configASSERT` fail-stop entry at `0x005FA0A4`.

The four littlefs helpers have no `lfs_t`, `lfs_config`, disk-format, block
device, allocation, callback, or global-state dependency. They do not need
the later utility tranche's explicit `LFS_NO_INTRINSICS` selection. Only
the upstream nonzero-alignment precondition applies to the two alignment
helpers; all retained callers use validated geometry or fixed nonzero
values.

The mask leaves have one recovered port parameter: the maximum syscall
interrupt mask is `BASEPRI=0x30`. The official binary selects the
`ARM_CM55_NTZ/non_secure` port shape. Their source candidate emits the exact
36 official bytes under both reviewed target profiles, so the remaining
question is redirect timing and placement, not semantics or configuration.

`pcTaskGetName` deliberately preserves two fixed compatibility seams until
the complete kernel is source-linked: the current-TCB word at `0x20074A20`
and the G2-extended 112-byte TCB layout. Its required prefix is independently
proven by the task initializer, including the 32-byte name at
`+0x34...+0x53` and the vendor stack-depth word at `+0x54`.

## Focused disassembly and integration checks

Do not decompile the upstream algorithms. Use focused disassembly only for
these target-specific checks:

1. Re-run complete-image `BL`, `B.W`, narrow-branch, stored-pointer, and
   interior-entry scans immediately before registering each stock redirect.
2. For the queue wrappers, inspect the linked relocations and require calls
   to resolve directly to source-owned queue creators/initializers. Confirm
   queue type, unsigned comparisons, null handling, and the `+0x38` write in
   the emitted target instructions.
3. For littlefs, build both current image profiles. Require no undefined
   symbols or data relocations and only the internal
   `lfs_alignup -> lfs_aligndown` text relocation.
4. For the mask pair, compare the complete 36 generated bytes with the
   official pair, preserve both public entries, audit all 181 set and 12
   clear callers, and quantify the critical-section latency added by any
   out-of-line redirect.
5. For `pcTaskGetName`, authenticate its sole direct caller, its
   `pxCurrentTCB` literal, the TCB-name writer, and its only outgoing call.
   Reject any build that leaves that call bound through a
   source-to-stock-to-source trampoline.
6. After each atomic wave, run target relocation review, aggregate ownership,
   package verification, offline flash-layout inspection, three-lane
   reproducibility, and the full regression suite.

## Evidence and focused validation

The underlying detailed audits remain:

- `docs/research/freertos-queue-wrapper-tranche-source-boundary-audit.md`;
- `docs/research/littlefs-next-closed-leaves-audit.md`;
- `docs/research/freertos-task-name-mask-production-readiness-audit.md`;
- `docs/research/freertos-pc-task-get-name-source-boundary-audit.md`; and
- `docs/research/freertos-g2-config-port-audit.md`.

Focused validation run for this ranking:

```text
python3 -m unittest -v \
  tests.test_analyze_g2_freertos_queue_wrapper_tranche \
  tests.test_freertos_queue_wrapper_tranche_candidate \
  tests.test_analyze_g2_freertos_task_name_mask_closure \
  tests.test_freertos_pc_task_get_name_candidate \
  tests.test_freertos_interrupt_mask_pair_candidate \
  tests.test_littlefs_util_cluster_candidate

Ran 36 tests in 29.869s
OK
```

These tests authenticate the official images and upstream snapshots, reject
mutated inputs, pin exact boundaries and complete reference topology, compare
host behavior with upstream, compile the bounded target candidates, and
inspect function bodies, relocations, undefined symbols, and configuration
seams. They do not sign, flash, connect to, or mutate hardware.
