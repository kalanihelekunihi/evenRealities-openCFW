# G2 first-pass firmware and flash map

This map distinguishes confirmed target addresses from inferred or unresolved
ones. It is generated into each profile's `build/*/flash-plan.json`; this
document explains the evidence and the installation model.

## Outer package

EVENOTA is a transport container, not a flat flash image. Its entry offsets
begin at file offset `0x000000B0` and change when a preceding component changes
size. The build recomputes those offsets and the non-reflected CRC-32C stored in
both the TOC and each 128-byte component header.

The reviewed order is:

1. codec (`type 4`)
2. EM9305 Bluetooth (`type 5`)
3. touch (`type 3`)
4. charging case / box (`type 6`)
5. Apollo bootloader (`type 1`)
6. Apollo main (`type 0`)

## Apollo510B internal MRAM — each temple

| Start | End exclusive | Size | Owner / function | Status |
|---:|---:|---:|---|---|
| `0x00400000` | `0x00410000` | 64 KiB | Ambiq secure bootloader | Confirmed; absent from EVENOTA and protected |
| `0x00410000` | `0x00410400` | 1,024 B | Even bootloader before littlefs utilities | Official compatibility bytes retained |
| `0x00410400` | `0x00410408` | 8 B | Source-replaced bootloader littlefs v2.10.1 `lfs_max` | Complete upstream scalar leaf |
| `0x00410408` | `0x00410410` | 8 B | Source-replaced bootloader littlefs v2.10.1 `lfs_min` | Complete upstream scalar leaf |
| `0x00410410` | `0x0041041C` | 12 B | Source-replaced bootloader littlefs v2.10.1 `lfs_aligndown` | Complete upstream unsigned alignment leaf |
| `0x0041041C` | `0x00410428` | 12 B | Source-replaced bootloader littlefs v2.10.1 `lfs_alignup` | Complete upstream leaf; source-linked to `lfs_aligndown` |
| `0x00410428` | `0x00410482` | 90 B | Source-replaced bootloader littlefs v2.10.1 `lfs_npw2` | Exact `LFS_NO_INTRINSICS` fallback body |
| `0x00410482` | `0x00410492` | 16 B | Source-replaced bootloader littlefs v2.10.1 `lfs_ctz` | Exact fallback body; source-linked to `lfs_npw2` |
| `0x00410492` | `0x004104BA` | 40 B | Source-replaced bootloader littlefs v2.10.1 `lfs_popc` | Exact `LFS_NO_INTRINSICS` fallback body |
| `0x004104BA` | `0x004104BE` | 4 B | Source-replaced bootloader littlefs v2.10.1 `lfs_scmp` | Exact upstream leaf; generated `B.W` entry redirect |
| `0x004104BE` | `0x004104E0` | 34 B | Source-replaced bootloader littlefs v2.10.1 `lfs_fromle32` | Complete upstream endian leaf; generated `B.W` plus NOP fill |
| `0x004104E0` | `0x004104E8` | 8 B | Source-replaced bootloader littlefs v2.10.1 `lfs_tole32` | Complete upstream endian leaf; generated `B.W` plus NOP fill |
| `0x004104E8` | `0x0041050A` | 34 B | Source-replaced bootloader littlefs v2.10.1 `lfs_frombe32` | Complete upstream endian leaf; generated `B.W` plus NOP fill |
| `0x0041050A` | `0x00410512` | 8 B | Source-replaced bootloader littlefs v2.10.1 `lfs_tobe32` | Complete upstream endian leaf; generated `B.W` plus NOP fill |
| `0x00410512` | `0x00410B72` | 1,632 B | Even bootloader before littlefs tag-validity | Official compatibility bytes retained |
| `0x00410B72` | `0x00410B7C` | 10 B | Source-replaced littlefs v2.10.1 `lfs_tag_isvalid` | Complete generated redirect and NOP fill |
| `0x00410B7C` | `0x00410B90` | 20 B | Even bootloader between tag-validity and tag-type1 | Official compatibility bytes retained |
| `0x00410B90` | `0x00410B98` | 8 B | Source-replaced littlefs v2.10.1 `lfs_tag_type1` | Complete generated redirect and NOP fill |
| `0x00410B98` | `0x00410BA0` | 8 B | Even bootloader between tag-type1 and tag-type3 | Official compatibility bytes retained |
| `0x00410BA0` | `0x00410BA8` | 8 B | Source-replaced littlefs v2.10.1 `lfs_tag_type3` | Complete generated redirect and NOP fill |
| `0x00410BA8` | `0x00410BAE` | 6 B | Source-replaced littlefs v2.10.1 `lfs_tag_chunk` | Complete generated redirect and NOP fill |
| `0x00410BAE` | `0x00410BB8` | 10 B | Even bootloader between tag-chunk and tag-ID leaves | Official compatibility bytes retained |
| `0x00410BB8` | `0x00410BC0` | 8 B | Source-replaced littlefs v2.10.1 `lfs_tag_id` | Complete generated redirect and NOP fill |
| `0x00410BC0` | `0x00410D8A` | 458 B | Even bootloader between tag-ID and metadata-list leaves | Official compatibility bytes retained |
| `0x00410D8A` | `0x00410DA8` | 30 B | Source-replaced bootloader littlefs v2.10.1 `lfs_mlist_isopen` | Exact upstream metadata-list membership predicate |
| `0x00410DA8` | `0x00410DC4` | 28 B | Source-replaced bootloader littlefs v2.10.1 `lfs_mlist_remove` | Exact upstream metadata-list removal leaf |
| `0x00410DC4` | `0x00410DCC` | 8 B | Source-replaced bootloader littlefs v2.10.1 `lfs_mlist_append` | Exact upstream metadata-list append leaf |
| `0x00410DCC` | `0x00410DD2` | 6 B | Source-replaced bootloader littlefs v2.10.1 `lfs_fs_disk_version` | Exact upstream disk-version getter |
| `0x00410DD2` | `0x00410DDE` | 12 B | Source-replaced bootloader littlefs v2.10.1 `lfs_fs_disk_version_major` | Exact complete stock span redirected to source |
| `0x00410DDE` | `0x00410DE8` | 10 B | Source-replaced bootloader littlefs v2.10.1 `lfs_fs_disk_version_minor` | Exact complete stock span redirected to source |
| `0x00410DE8` | `0x00410DEE` | 6 B | Source-replaced bootloader littlefs v2.10.1 `lfs_alloc_ckpoint` | Exact upstream leaf; generated `B.W` plus NOP fill |
| `0x00410DEE` | `0x00410DFE` | 16 B | Source-replaced bootloader littlefs v2.10.1 `lfs_alloc_drop` | Exact upstream allocator-state restore leaf |
| `0x00410DFE` | `0x00410E36` | 56 B | Source-replaced bootloader littlefs v2.10.1 `lfs_alloc_lookahead` | Exact complete callback span redirected to source |
| `0x00410E36` | `0x00415590` | 18,266 B | Even bootloader before the S200 redirect initializer | Official compatibility bytes retained |
| `0x00415590` | `0x004155E8` | 88 B | Source-replaced S200 bootloader `redirect_init` | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x004155E8` | `0x0041560C` | 36 B | Even bootloader literal/alignment pool after `redirect_init` | Official compatibility bytes retained |
| `0x0041560C` | `0x00415672` | 102 B | Source-replaced Arm EABI byte-fill primitive | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x00415672` | `0x0041568C` | 26 B | Unreferenced bootloader buffered-byte writer | Official compatibility bytes retained; zero authenticated ingress |
| `0x0041568C` | `0x00415732` | 166 B | Source-replaced Arm EABI forward-copy primitive | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x00415732` | `0x00415758` | 38 B | Bootloader semihost/runtime seam before byte comparison | Official compatibility bytes retained |
| `0x00415758` | `0x004157C0` | 104 B | Source-replaced bounded byte comparison | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x004157C0` | `0x004157F8` | 56 B | Source-replaced reflected CRC-32 updater | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x004157F8` | `0x0041581A` | 34 B | Source-replaced reject-set string span (`strcspn`) | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x0041581A` | `0x0041583C` | 34 B | Source-replaced accept-set string span (`strspn`) | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x0041583C` | `0x00415844` | 8 B | Source-replaced SRAM-word setter for `0x200270CC` | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x00415844` | `0x00415900` | 188 B | Source-replaced unsigned 64-bit divide-by-ten helper | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x00415900` | `0x00415924` | 36 B | Source-replaced unsigned decimal digit count | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x00415924` | `0x00415936` | 18 B | Source-replaced signed-magnitude decimal digit count | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x00415936` | `0x0041595C` | 38 B | Source-replaced hexadecimal digit count | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x0041595C` | `0x004159A0` | 68 B | Source-replaced optional-minus wrapping decimal parser | Generated redirect and NOP fill over the authenticated complete stock entry |
| `0x004159A0` | `0x00415A08` | 104 B | Source-replaced unsigned 64-bit decimal output helper | Complete authenticated entry |
| `0x00415A08` | `0x00415A7C` | 116 B | Source-replaced unsigned 64-bit hexadecimal output helper | Complete authenticated entry |
| `0x00415A7C` | `0x00415A94` | 24 B | Source-replaced nullable string-length helper | Complete authenticated entry |
| `0x00415A94` | `0x00415AB6` | 34 B | Source-replaced repeated-character output helper | Complete authenticated entry |
| `0x00415AB6` | `0x00415BF6` | 320 B | Source-replaced fixed-point float converter | Complete authenticated entry |
| `0x00415BF6` | `0x00415FAE` | 952 B | Source-replaced bootloader formatter core | Complete authenticated entry |
| `0x00415FAE` | `0x00415FDA` | 44 B | Source-replaced bootloader variadic logging dispatch wrapper | Complete authenticated entry; 57 direct callers |
| `0x00415FDA` | `0x00415FFA` | 32 B | Retained authenticated logging literal pool/data | Non-executable boundary; not treated as a C-body gap |
| `0x00415FFA` | `0x00416026` | 44 B | Source-replaced bootloader substring-search primitive | Complete authenticated entry; six direct callers |
| `0x00416026` | `0x0041602A` | 4 B | Retained authenticated two-byte self-loop and no-op return stubs | Separate non-redirectable compatibility boundaries |
| `0x0041602A` | `0x00416058` | 46 B | Source-replaced bootloader critical-context predicate | Complete authenticated entry; 21 direct callers |
| `0x00416058` | `0x00416088` | 48 B | Source-replaced bootloader runtime-state gate acquisition wrapper | Complete authenticated entry; one direct caller |
| `0x00416088` | `0x004160B0` | 40 B | Source-replaced bootloader runtime-state and SRAM-gate mapper | Complete authenticated entry; one direct caller |
| `0x004160B0` | `0x004160E8` | 56 B | Source-replaced bootloader runtime-state gate release wrapper | Complete authenticated entry; one direct caller |
| `0x004160E8` | `0x004160FE` | 22 B | Source-replaced bootloader critical-context value dispatcher | Complete authenticated entry; three direct callers |
| `0x004160FE` | `0x004161C6` | 200 B | Source-replaced bootloader address-identified runtime dispatcher | Complete authenticated entry; three direct callers, 28-byte option ABI, two retained dispatch seams |
| `0x004161C6` | `0x004161CE` | 8 B | Source-replaced bootloader address-identified retained-value wrapper | Complete authenticated entry; two direct callers and one retained getter seam |
| `0x004161CE` | `0x00416200` | 50 B | Source-replaced bootloader address-identified validated runtime-call wrapper | Complete authenticated entry; two direct callers, critical-context guard, selector range, and one retained call seam |
| `0x00416200` | `0x0041623A` | 58 B | Source-replaced bootloader address-identified guarded runtime-action wrapper | Complete authenticated entry; three direct callers, critical/null guards, retained predicate, and retained action seam |
| `0x0041623A` | `0x004162C4` | 138 B | Source-replaced bootloader address-identified two-phase runtime-transfer wrapper | Complete authenticated entry; two direct callers, invalid-argument guards, retained critical/normal backends, result propagation, and conditional PendSV request |
| `0x004162C4` | `0x00416378` | 180 B | Source-replaced bootloader address-identified masked runtime-wait wrapper | Complete authenticated entry; three direct callers, wait-any/wait-all accumulation, clear-mask option, and wrap-safe timeout recomputation |
| `0x00416378` | `0x0041639A` | 34 B | Source-replaced bootloader address-identified optional runtime-notification wrapper | Complete authenticated entry; two direct callers, critical-context rejection, null no-op, and retained-backend forwarding |
| `0x0041639A` | `0x004163B2` | 24 B | Source-replaced bootloader address-identified registered runtime-callback adapter | Complete authenticated entry; unique Thumb literal and two registration-load ingress paths, low-bit record flag clearing, and exact indirect callback dispatch |
| `0x004163B2` | `0x0041649A` | 232 B | Source-replaced bootloader address-identified registered runtime-object constructor | Complete authenticated entry; one direct caller, embedded/dynamic callback-record ownership, exact static/dynamic backend selection, tag clearing, and failure cleanup |
| `0x0041649A` | `0x004164DA` | 64 B | Source-replaced guarded runtime submission wrapper | Complete authenticated entry; one direct caller |
| `0x004164DA` | `0x0041652E` | 84 B | Source-replaced runtime object creation wrapper | Complete authenticated entry; one direct caller and exact static/dynamic storage contract |
| `0x0041652E` | `0x0041658C` | 94 B | Source-replaced event-flags set wrapper | Complete authenticated entry; task/ISR split and conditional PendSV request |
| `0x0041658C` | `0x00416590` | 4 B | Event-flags SRAM literal | Authenticated retained data (`0x200270D4`) |
| `0x00416590` | `0x00416610` | 128 B | Source-replaced event-flags wait wrapper | Complete authenticated entry; wait-any/all, clear, and timeout mapping |
| `0x00416610` | `0x004166AA` | 154 B | Source-replaced event-flags creation wrapper | Complete authenticated entry; six callers and static/dynamic tagged constructors |
| `0x004166AA` | `0x00416710` | 102 B | Source-replaced tagged-handle acquire wrapper | Complete authenticated entry; nine callers and timeout mapping |
| `0x00416710` | `0x00416762` | 82 B | Source-replaced tagged-handle release wrapper | Complete authenticated entry; nine callers and zero-argument plain release |
| `0x00416762` | `0x00416816` | 180 B | Source-replaced semaphore creation wrapper | Complete authenticated entry; binary/counting and static/dynamic paths |
| `0x00416816` | `0x004168A2` | 140 B | Source-replaced message-queue creation wrapper | Complete authenticated entry; two callers and static/dynamic storage contracts |
| `0x004168A2` | `0x00416920` | 126 B | Source-replaced message-queue put wrapper | Complete authenticated entry; task/ISR paths, timeout mapping, and conditional PendSV |
| `0x00416920` | `0x0041699A` | 122 B | Source-replaced message-queue get wrapper | Complete authenticated entry; task/ISR paths, timeout mapping, and conditional PendSV |
| `0x0041699A` | `0x004169A4` | 10 B | Queue-wrapper alignment and SCB ICSR literal pool | Authenticated retained data (`0xE000ED04`) |
| `0x004169A4` | `0x004169E2` | 62 B | Source-replaced unsigned bit-width helper | Complete authenticated entry; zero and 1–32 bit-width contract |
| `0x004169E2` | `0x004169F2` | 16 B | Source-replaced trailing-zero helper | Complete authenticated entry; zero wraps to `0xFFFFFFFF` |
| `0x004169F2` | `0x004169FC` | 10 B | Source-replaced unsigned floor-log2 helper | Complete authenticated entry; zero wraps to `0xFFFFFFFF` |
| `0x004169FC` | `0x00416AAA` | 174 B | Source-replaced TLSF v3.1 block-header primitive cluster | Twelve complete authenticated entries; size/status flags, block/user-pointer conversion, and offset arithmetic |
| `0x00416AAA` | `0x00416BCE` | 292 B | Source-replaced TLSF v3.1 physical-block and alignment cluster | Eight complete authenticated entries; neighbor/link/state propagation, alignment, and recovered assertions |
| `0x00416BCE` | `0x00416C4E` | 128 B | Source-replaced TLSF v3.1 request-size and class-mapping cluster | Three complete authenticated entries; size bounds, insertion mapping, and rounded search mapping |
| `0x00416C4E` | `0x00416E04` | 438 B | Source-replaced TLSF v3.1 free-list cluster | Three complete authenticated entries; suitable-class selection, exhaustion, sentinel links, removal/insertion, and bitmap transitions |
| `0x00416E04` | `0x0041711C` | 792 B | Source-replaced TLSF v3.1 allocator-operation cluster | Ten complete authenticated entries; request adjustment, split/trim/absorb/coalescing, lookup, and allocation preparation |
| `0x0041711C` | `0x004172DA` | 446 B | Source-replaced TLSF v3.1 public allocator cluster | Seven complete authenticated entries; control construction, pool overhead/addition, create/create-with-pool, malloc, and free |
| `0x004172DA` | `0x0041733C` | 98 B | TLSF/EasyLogger transition literals and alignment | Authenticated retained non-entry data |
| `0x0041733C` | `0x004176CE` | 914 B | Source-replaced EasyLogger control cluster | Ten complete authenticated entries: init/start, setters, lock transitions, and tag-level query/reset |
| `0x004176CE` | `0x00417AD0` | 1,026 B | Source-replaced EasyLogger `elog_output` | Complete interrupt-gated filtering, formatting, keyword, color, truncation, and sink contract |
| `0x00417AD0` | `0x00417AD4` | 4 B | EasyLogger CSI-start literal/alignment | Authenticated retained non-executable data |
| `0x00417AD4` | `0x00417B3E` | 106 B | Source-replaced EasyLogger `get_fmt_enabled` | Generated redirect and NOP fill |
| `0x00417B3E` | `0x00417B48` | 10 B | EasyLogger punctuation/alignment gap | Official compatibility bytes retained |
| `0x00417B48` | `0x00417B62` | 26 B | Source-replaced EasyLogger unsigned-argument predicate | Generated redirect and NOP fill |
| `0x00417B62` | `0x00417B7C` | 26 B | Source-replaced EasyLogger pointer-argument predicate | Generated redirect and NOP fill |
| `0x00417B7C` | `0x00417BB8` | 60 B | Source-replaced EasyLogger output-lock enable transition | Complete authenticated entry; saved lock-state reconciliation |
| `0x00417BB8` | `0x0041A648` | 10,896 B | Even bootloader before the EasyLogger boot port | Official compatibility bytes retained; includes remaining service software gaps |
| `0x0041A648` | `0x0041A6DA` | 146 B | Source-replaced EasyLogger boot-port cluster | Nine complete entries: mutex lifecycle, initialization, output/lock forwarding, time, and task name |
| `0x0041A6DA` | `0x0041A6F0` | 22 B | EasyLogger boot-port format/literal island | Authenticated retained non-executable data |
| `0x0041A6F0` | `0x0041A700` | 16 B | Source-replaced EasyLogger process/thread info wrappers | Two complete entries sharing the task-name helper |
| `0x0041A700` | `0x0041B158` | 2,648 B | Even bootloader between EasyLogger port and bounded copy | Official compatibility bytes retained; includes remaining driver/transport software gaps |
| `0x0041B158` | `0x0041B1FA` | 162 B | Source-replaced EasyLogger `elog_strcpy` | Generated redirect and NOP fill |
| `0x0041B1FA` | `0x0041B854` | 1,626 B | Even bootloader before the EasyLogger output driver | Official compatibility bytes retained |
| `0x0041B854` | `0x0041B862` | 14 B | Source-replaced EasyLogger channel-one output driver | Complete authenticated level-dropping wrapper |
| `0x0041B862` | `0x0041F918` | 16,566 B | Even bootloader before the four-channel transfer routine | Official compatibility bytes retained |
| `0x0041F918` | `0x0041F9B6` | 158 B | Source-replaced four-channel descriptor transport | Complete validation, lower start, completion polling, and timeout entry |
| `0x0041F9B6` | `0x0041F9D8` | 34 B | Boot-service vector/literal island | Authenticated retained non-executable data |
| `0x0041F9D8` | `0x0041F9E6` | 14 B | Source-replaced millisecond boot delay | Wrapping ×1,000 conversion and raw-delay forwarding |
| `0x0041F9E6` | `0x0041F9EE` | 8 B | Source-replaced raw boot delay | Complete scalar forwarding wrapper |
| `0x0041F9EE` | `0x0041F9F0` | 2 B | Boot-service alignment | Authenticated retained non-executable bytes |
| `0x0041F9F0` | `0x0041F9F8` | 8 B | Source-replaced initializer priority comparator | Complete eight-byte record comparator; stored Thumb ingress retained |
| `0x0041F9F8` | `0x0041FA40` | 72 B | Source-replaced boot initializer runner | Bounded table copy, sort, null skip, and callback dispatch |
| `0x0041FA40` | `0x0041FA50` | 16 B | Boot initializer pointer/alignment data | Official initializer pointers, alignment, and stored comparator pointer retained |
| `0x0041FA50` | `0x0041FA98` | 72 B | Source-replaced boot platform setup | Guarded teardown, reset/mode, VFP derive, 20-byte configuration submit, and channels four/five setup |
| `0x0041FA98` | `0x0041FAD0` | 56 B | Source-replaced guarded boot teardown | Two fail-stop status stages, state clear, pin reconciliation, and guard clear |
| `0x0041FAD0` | `0x0041FADC` | 12 B | Guarded-teardown literal pool | Official guard/configuration pointers retained |
| `0x0041FADC` | `0x0041FCF6` | 538 B | Source-replaced pin-group dispatcher | Two banks, cumulative subtype groups, SRAM configuration words, and ordered pin configuration |
| `0x0041FCF6` | `0x0041FD70` | 122 B | Pin/allocator literal pool | Authenticated retained non-executable data |
| `0x0041FD70` | `0x0041FDA8` | 56 B | Source-replaced TLSF pool initializer | Pool clear, TLSF creation, handle publication, diagnostic record, and zero return |
| `0x0041FDA8` | `0x0041FDC0` | 24 B | Allocator/IRQ literal pool | Authenticated retained non-executable data |
| `0x0041FDC0` | `0x0041FDDE` | 30 B | Source-replaced NVIC interrupt-enable entry | Signed IRQ guard, bank derivation, and set-enable write |
| `0x0041FDDE` | `0x0041FE06` | 40 B | Source-replaced NVIC priority entry | External IRQ and system-handler priority-byte selection |
| `0x0041FE06` | `0x0041FE28` | 34 B | Source-replaced MSPI ISR wrapper | Status get, clear, and service through the retained HAL |
| `0x0041FE28` | `0x0041FE48` | 32 B | Source-replaced MSPI enable | Idempotent active-state check and retained control call |
| `0x0041FE48` | `0x0041FE62` | 26 B | Source-replaced MSPI disable | Retained control call and active-state clear |
| `0x0041FE62` | `0x0041FE9C` | 58 B | Source-replaced event-flags service init | Idempotent static creation, handle publication, and failure diagnostic |
| `0x0041FE9C` | `0x0041FED4` | 56 B | Source-replaced event-flags acquire | Null-handle guard, wait-forever acquire, and failure diagnostic |
| `0x0041FED4` | `0x0041FF08` | 52 B | Source-replaced event-flags release | Null-handle guard, release, and failure diagnostic |
| `0x0041FF08` | `0x0041FF1E` | 22 B | Source-replaced MSPI guard enter | Event lock followed by bypass-gated MSPI disable |
| `0x0041FF1E` | `0x0041FF34` | 22 B | Source-replaced MSPI guard exit | Bypass-gated MSPI enable followed by event unlock |
| `0x0041FF34` | `0x0041FF60` | 44 B | Source-replaced MSPI XIP-config updater | Low-byte selector mutates retained config byte five and submits control request 16 |
| `0x0041FF60` | `0x0041FF74` | 20 B | Source-replaced longest consecutive-one run helper | Complete word-load and `value &= value << 1` loop |
| `0x0041FF74` | `0x00420002` | 142 B | Source-replaced longest-one run center selector | Complete bit scan, first-longest selection, midpoint bias, and boundary adjustments |
| `0x00420002` | `0x004201BA` | 440 B | Source-replaced exhaustive MSPI timing scan | 36 coarse rows × 32 fine delays, JEDEC-ID pass masks, first-longest row selection, centered result, and diagnostics |
| `0x004201BA` | `0x00420254` | 154 B | Source-replaced automatic MSPI timing selection | Zeroed scan object, success publication, failure preservation, and retained diagnostics |
| `0x00420254` | `0x00420476` | 546 B | Source-replaced low-level MSPI initializer | HAL setup, XIP/pin/interrupt configuration, cleanup, state publication, and diagnostics |
| `0x00420476` | `0x0042052A` | 180 B | Source-replaced MX25U25643G public initializer | Low-level init, timing selection, JEDEC-ID read, final service setup, and diagnostics |
| `0x0042052A` | `0x0042059E` | 116 B | Source-replaced MX25U25643G soft reset | Reset-enable/reset commands, ordered delays, and failure-only diagnostics |
| `0x0042059E` | `0x004205F4` | 86 B | Source-replaced MX25U25643G JEDEC-ID reader | Command `0x9F`, three-byte receive, failure diagnostic, and big-endian identifier packing |
| `0x004205F4` | `0x0042069E` | 170 B | Source-replaced MX25U25643G read-transfer wrapper | Handle/argument validation, 24-byte transfer descriptor, blocking HAL call, and failure diagnostic |
| `0x0042069E` | `0x0042074E` | 176 B | Source-replaced MX25U25643G write-transfer wrapper | Address/length validation, exact write descriptor, blocking HAL call, and failure diagnostic |
| `0x0042074E` | `0x004207A2` | 84 B | Source-replaced MX25U25643G busy-status reader | Command `0x05`, one-byte read, bit-7 decode, raw failure return, and diagnostic |
| `0x004207A2` | `0x004207F4` | 82 B | Source-replaced MX25U25643G ready poll | 200 fast polls, caller-bounded context-aware slow phase, and timeout result |
| `0x004207F4` | `0x00420800` | 12 B | Source-replaced MX25U25643G fixed ready-poll wrapper | Calls the two-phase poll with a 500-iteration slow bound |
| `0x00420800` | `0x0042086C` | 108 B | Source-replaced MX25U25643G address-mode reader | Reads command `0x15`, preserves raw errors, decodes bit 5, and reports three-byte mode |
| `0x0042086C` | `0x00420890` | 36 B | Retained MX25U25643G literal region | Authenticated non-executable compatibility data preceding enter-four-byte-mode |
| `0x00420890` | `0x00420978` | 232 B | Source-replaced MX25U25643G enter-four-byte-mode service | Ready checks, write-enable, command `0xB7`, address-mode verification, write-disable, and exact status policy |
| `0x00420978` | `0x00420984` | 12 B | Retained MX25U25643G literal region | Authenticated non-executable compatibility data preceding write-enable |
| `0x00420984` | `0x004209BE` | 58 B | Source-replaced MX25U25643G write-enable wrapper | Command `0x06`, zeroed transfer fields, raw status, and failure-only diagnostic |
| `0x004209BE` | `0x004209C4` | 6 B | Retained MX25U25643G literal/alignment region | Authenticated non-executable compatibility data preceding write-disable |
| `0x004209C4` | `0x004209FC` | 56 B | Source-replaced MX25U25643G write-disable wrapper | Command `0x04`, zeroed transfer fields, raw status, and failure-only diagnostic |
| `0x004209FC` | `0x00420A08` | 12 B | Retained MX25U25643G literal region | Authenticated non-executable compatibility data preceding sector erase |
| `0x00420A08` | `0x00420ADA` | 210 B | Source-replaced MX25U25643G sector-erase service | 4-KiB validation, guarded serial-mode command `0x20`, ready polls, write-latch sequencing, cleanup, and exact status/diagnostic policy |
| `0x00420ADA` | `0x00420B0C` | 50 B | Retained MX25U25643G literal/alignment region | Authenticated non-executable compatibility data preceding page program |
| `0x00420B0C` | `0x00420C14` | 264 B | Source-replaced MX25U25643G page-program service | Handle/buffer/length validation, 256-byte page splitting, guarded command `0x02`, per-page ready/write-latch sequencing, cleanup, and exact status/diagnostic policy |
| `0x00420C14` | `0x00420C5C` | 72 B | Retained MX25U25643G literal/alignment region | Authenticated non-executable compatibility data preceding QE configuration |
| `0x00420C5C` | `0x00420DFA` | 414 B | Source-replaced MX25U25643G status-register-2 QE service | Fixed-handle check, QE/protection-bit policy, commands `0x05`/`0x01`, raw failures, verification, and exact diagnostics |
| `0x00420DFA` | `0x00420E08` | 14 B | Retained MSPI device-reconfiguration literal pool | Authenticated non-executable compatibility data |
| `0x00420E08` | `0x00420E8C` | 132 B | Source-replaced MSPI device-reconfiguration service | Disable, device configure, enable, published-instance/device pin-group selection, collapsed error status, and exact diagnostics |
| `0x00420E8C` | `0x00420F0C` | 128 B | Source-replaced MX25U25643G quad-mode selector | Template clone, exact field overrides, reconfiguration, XIP enable, HAL request `0x18`, and diagnostics |
| `0x00420F0C` | `0x00420F10` | 4 B | Authenticated literal pool | Non-executable compatibility data retained |
| `0x00420F10` | `0x00420F6A` | 90 B | Source-replaced MX25U25643G serial-mode selector | Reconfiguration, XIP disable, HAL request `0x18` with mode byte zero, and diagnostics |
| `0x00420F6A` | `0x00420F70` | 6 B | Authenticated successor gap | Non-executable literal/alignment bytes retained |
| `0x00420F70` | `0x00420FF2` | 130 B | Source-replaced MX25U25643G guarded blocking read | Validation, guard, quad-mode selection, ready wait, exact read descriptor, blocking HAL transfer, and guard release |
| `0x00420FF2` | `0x004210C8` | 214 B | Retained predecessor literal/alignment pool | Authenticated non-executable compatibility data preceding directory bootstrap |
| `0x004210C8` | `0x004211B0` | 232 B | Source-replaced LittleFS directory bootstrap | Checks or creates `/firmware`, `/ota`, `/user`, and `/log` with exact open/mkdir/close and error policy |
| `0x004211B0` | `0x00421210` | 96 B | Source-replaced LittleFS format/bootstrap service | Unmount, format, mount, directory bootstrap, diagnostics, and exact status mapping |
| `0x00421210` | `0x004212D8` | 200 B | Source-replaced LittleFS initializer and boot-counter service | Mount/format retry, directory recovery, readiness publication, and persisted `boot_count` increment |
| `0x004212D8` | `0x00421310` | 56 B | Source-replaced LittleFS block-read callback | Partition address mapping, guarded flash read, diagnostic, and `LFS_ERR_IO` mapping |
| `0x00421310` | `0x00421348` | 56 B | Source-replaced LittleFS block-program callback | Entry redirects to a 60-byte fixed-address leaf in authenticated reclaimed initializer body space; partition address mapping, guarded page program, diagnostic, and `LFS_ERR_IO` mapping |
| `0x00421348` | `0x00421372` | 42 B | Source-replaced LittleFS block-erase callback | Entry redirects to a 48-byte fixed-address leaf in authenticated reclaimed initializer body space; partition address mapping, guarded sector erase, diagnostic, and `LFS_ERR_IO` mapping |
| `0x00421372` | `0x004213D4` | 98 B | Authenticated LittleFS callback literal/alignment gap | Official non-executable compatibility bytes retained |
| `0x004213D4` | `0x004213D8` | 4 B | Source-replaced LittleFS sync callback | Redirects to the four-byte fixed source cave at `0x00421280` and returns zero |
| `0x004213D8` | `0x004213DA` | 2 B | Exact in-place source identity helper | Apple/Linux C compilation reproduces the complete stock body |
| `0x004213DA` | `0x004213E6` | 12 B | Exact in-place source thresholded address mapper | Values below `0x200` pass through; other values add `0x280` with 32-bit wrap |
| `0x004213E6` | `0x004213EC` | 6 B | Mapped-memory selector entry replacement | Generated branch and alignment to the authenticated source cave |
| `0x004213EC` | `0x004214C8` | 220 B | Mapped-memory selector/copy source cave | Compiled clean-room C with strict calls to the index helpers and copy provider |
| `0x004214C8` | `0x004214E6` | 30 B | Odd-selector wrapper source cave | Compiled clean-room C with strict tail branch to the primary selector |
| `0x004214E6` | `0x00421548` | 98 B | Mapped-memory selector generated tail | Authenticated generated NOP fill |
| `0x00421548` | `0x0042156E` | 38 B | Odd-selector wrapper entry replacement | Generated backward branch and NOP fill |
| `0x0042156E` | `0x00421584` | 22 B | Mapped-memory literal/alignment pool | Authenticated non-executable compatibility data retained |
| `0x00421584` | `0x004215AE` | 42 B | Exact in-place source population-count helper | Apple/Linux C compilation reproduces the complete stock body |
| `0x004215AE` | `0x004215DC` | 46 B | Exact in-place source bitmap nonempty helper | Tests the two words selected by the low selector byte |
| `0x004215DC` | `0x004215FE` | 34 B | Exact in-place source bitmap membership helper | Tests one narrowed bit in the selected two-word row |
| `0x004215FE` | `0x00421632` | 52 B | Exact in-place source bitmap population-count helper | Sums both words through the source-owned helper at `0x00421584` |
| `0x00421632` | `0x004216B2` | 128 B | Exact in-place source bitmap update helper | Validates selector/bit, then sets or clears one bit in the two-word row |
| `0x004216B2` | `0x004216D4` | 34 B | Exact in-place source bounded poll-delay helper | Delays by 10 and decrements while activity and remaining count are nonzero |
| `0x004216D4` | `0x004217D2` | 254 B | Exact in-place source mode/configuration service | Query/default merge, critical section, bitmap-state policy, apply/disable fallback, copy and publication |
| `0x004217D2` | `0x00426506` | 19,764 B | Even bootloader before MSPI interrupt clear | Official compatibility bytes retained; next authenticated executable body begins at `0x004217D2` |
| `0x00426506` | `0x00426536` | 48 B | Source-replaced AmbiqSuite 5.1.0 `am_hal_mspi_interrupt_clear` | Generated redirect over the authenticated complete stock body |
| `0x00426536` | `0x004267FE` | 712 B | Source-owned AmbiqSuite 5.1.0 `am_hal_mspi_interrupt_service` | Reviewable BSD-3-Clause Thumb-2 mnemonics; exact after 8 named call relocations |
| `0x004267FE` | `0x00426808` | 10 B | MSPI interrupt-service literal pool | Official compatibility data retained |
| `0x00426808` | `0x00426BFE` | 1,014 B | Source-owned AmbiqSuite 5.1.0 `am_hal_mspi_power_control` | Reviewable BSD-3-Clause Thumb-2 mnemonics; exact after 12 named call relocations |
| `0x00426BFE` | `0x00426C10` | 18 B | MSPI power-control literal pool | Official compatibility data retained |
| `0x00426C10` | `0x00434477` | 55,399 B | Remaining classified bootloader frontier | 249-span typed executable/mixed/data ledger; official compatibility bytes retained |
| `0x00434477` | `0x00434478` | 1 B | Bootloader source-overlay alignment | Generated zero byte |
| `0x00434478` | `0x004344D2` | 90 B | Bootloader littlefs source overlay | Ten Clang-built exact upstream leaves |
| `0x004344D2` | `0x0043450A` | 56 B | Bootloader littlefs v2.10.1 `lfs_npw2` | Mini-linked fallback body |
| `0x0043450A` | `0x0043451A` | 16 B | Bootloader littlefs v2.10.1 `lfs_ctz` | Mini-linked fallback body; internal call to `lfs_npw2` resolved |
| `0x0043451A` | `0x00434544` | 42 B | Bootloader littlefs v2.10.1 `lfs_popc` | Mini-linked fallback body |
| `0x00434544` | `0x00434574` | 48 B | AmbiqSuite 5.1.0 `am_hal_mspi_interrupt_clear` | Complete authenticated upstream translation unit, section-GC retained leaf |
| `0x00434574` | `0x00434586` | 18 B | Bootloader littlefs v2.10.1 `lfs_mlist_isopen` | Relocation-free isolated source leaf |
| `0x00434586` | `0x00434588` | 2 B | Bootloader littlefs v2.10.1 `lfs_fromle32` | Relocation-free identity source leaf |
| `0x00434588` | `0x0043458A` | 2 B | Bootloader littlefs v2.10.1 `lfs_tole32` | Relocation-free identity source leaf |
| `0x0043458A` | `0x0043458E` | 4 B | Bootloader littlefs v2.10.1 `lfs_frombe32` | Relocation-free byte-swap source leaf |
| `0x0043458E` | `0x00434592` | 4 B | Bootloader littlefs v2.10.1 `lfs_tobe32` | Relocation-free byte-swap source leaf |
| `0x00434592` | `0x0043459C` | 10 B | Bootloader littlefs v2.10.1 `lfs_fs_disk_version_major` | Relocated source leaf; direct call to source disk-version provider |
| `0x0043459C` | `0x004345A6` | 10 B | Bootloader littlefs v2.10.1 `lfs_fs_disk_version_minor` | Relocated source leaf; direct call to source disk-version provider |
| `0x004345A6` | `0x004345D6` | 48 B | Bootloader littlefs v2.10.1 `lfs_alloc_lookahead` | Relocation-free source leaf with recovered `lfs_t` offsets |
| `0x004345D6` | `0x004345D8` | 2 B | EasyLogger seam-provider alignment | Generated zero padding |
| `0x004345D8` | `0x004345E0` | 8 B | Bootloader EasyLogger logger-object provider | Source compiled |
| `0x004345E0` | `0x00434664` | 132 B | Bootloader EasyLogger assertion-policy provider | Source compiled; official strings/output/wait remain explicit seams |
| `0x00434664` | `0x0043468A` | 38 B | EasyLogger `get_fmt_enabled` | Relocated source leaf |
| `0x0043468A` | `0x0043469E` | 20 B | EasyLogger unsigned-argument predicate | Relocated source leaf |
| `0x0043469E` | `0x004346B2` | 20 B | EasyLogger pointer-argument predicate | Relocated source leaf |
| `0x004346B2` | `0x004346E6` | 52 B | EasyLogger `elog_strcpy` | Relocated source leaf |
| `0x004346E6` | `0x004346EC` | 6 B | littlefs v2.10.1 `lfs_tag_chunk` | Relocation-free scalar source leaf |
| `0x004346EC` | `0x004346F2` | 6 B | littlefs v2.10.1 `lfs_tag_isvalid` | Relocation-free scalar source leaf |
| `0x004346F2` | `0x004346FC` | 10 B | littlefs v2.10.1 `lfs_tag_type1` | Relocation-free scalar source leaf |
| `0x004346FC` | `0x00434702` | 6 B | littlefs v2.10.1 `lfs_tag_type3` | Relocation-free scalar source leaf |
| `0x00434702` | `0x00434708` | 6 B | littlefs v2.10.1 `lfs_tag_id` | Relocation-free scalar source leaf |
| `0x00434708` | `0x0043470E` | 6 B | littlefs v2.10.1 `lfs_tag_size` | Relocation-free scalar source leaf |
| `0x0043470E` | `0x00434710` | 2 B | S200 redirect-initializer alignment | Generated zero padding |
| `0x00434710` | `0x00434794` | 132 B | S200 bootloader `redirect_init` | Clean-room two-mutex initializer; strict calls to retained CMSIS/EasyLogger providers |
| `0x00434794` | `0x00434823` | 143 B | S200 bootloader `redirect_init` diagnostic strings | Source-owned authenticated read-only-data closure |
| `0x00434823` | `0x00434824` | 1 B | Arm EABI byte-fill alignment | Generated zero padding |
| `0x00434824` | `0x00434830` | 12 B | Arm EABI byte-fill primitive | Clean-room relocation-free C leaf |
| `0x00434830` | `0x00434840` | 16 B | Arm EABI forward-copy primitive | Clean-room relocation-free C leaf |
| `0x00434840` | `0x0043485C` | 28 B | Bounded byte comparison | Clean-room relocation-free C leaf |
| `0x0043485C` | `0x0043487A` | 30 B | Reject-set string span (`strcspn`) | Clean-room relocation-free C leaf |
| `0x0043487A` | `0x00434896` | 28 B | Accept-set string span (`strspn`) | Clean-room relocation-free C leaf |
| `0x00434896` | `0x00434898` | 2 B | Reflected CRC-32 leaf alignment | Generated zero padding |
| `0x00434898` | `0x004348C4` | 44 B | Reflected CRC-32 updater | Clean-room relocation-free bitwise C leaf |
| `0x004348C4` | `0x004348D0` | 12 B | SRAM-word setter for `0x200270CC` | Clean-room relocation-free C leaf with inline address literal |
| `0x004348D0` | `0x0043493A` | 106 B | Unsigned 64-bit divide-by-ten helper | Clean-room shift/add/correction C leaf; relocation-free |
| `0x0043493A` | `0x00434956` | 28 B | Unsigned decimal digit count | Clean-room C leaf; strict call to source-owned divide-by-ten helper |
| `0x00434956` | `0x0043496A` | 20 B | Signed-magnitude decimal digit count | Clean-room C leaf; strict tail call to unsigned counter |
| `0x0043496A` | `0x00434982` | 24 B | Hexadecimal digit count | Clean-room relocation-free C leaf |
| `0x00434982` | `0x004349B2` | 48 B | Optional-minus wrapping decimal parser | Clean-room relocation-free C leaf |
| `0x004349B2` | `0x004349FC` | 74 B | Unsigned 64-bit decimal output helper | Clean-room C leaf; strict call to divide-by-ten helper |
| `0x004349FC` | `0x00434A44` | 72 B | Unsigned 64-bit hexadecimal output helper | Clean-room relocation-free C leaf |
| `0x00434A44` | `0x00434A58` | 20 B | Nullable string-length helper | Clean-room relocation-free C leaf |
| `0x00434A58` | `0x00434A78` | 32 B | Null-output-aware repeated-character helper | Clean-room relocation-free C leaf |
| `0x00434A78` | `0x00434BB8` | 320 B | Fixed-point float converter | Clean-room hard-float C leaf |
| `0x00434BB8` | `0x00434F80` | 968 B | Bootloader formatter core | Clean-room C leaf; 15 strict internal calls |
| `0x00434F80` | `0x00434FBC` | 60 B | Bootloader variadic logging dispatch wrapper | Clean-room C leaf; one strict call to formatter core |
| `0x00434FBC` | `0x00434FEA` | 46 B | Bootloader substring-search primitive | Clean-room relocation-free C leaf |
| `0x00434FEA` | `0x00435018` | 46 B | Bootloader critical-context predicate | Clean-room C leaf; one strict retained-state-query call |
| `0x00435018` | `0x00435048` | 48 B | Bootloader runtime-state gate acquisition wrapper | Clean-room C leaf; strict calls to the context predicate and retained-state query |
| `0x00435048` | `0x0043506C` | 36 B | Bootloader runtime-state and SRAM-gate mapper | Clean-room C leaf; one strict retained-state-query call |
| `0x0043506C` | `0x004350A4` | 56 B | Bootloader runtime-state gate release wrapper | Clean-room C leaf; four strict reviewed calls |
| `0x004350A4` | `0x004350BC` | 24 B | Bootloader critical-context value dispatcher | Clean-room C leaf; three strict reviewed calls/jumps |
| `0x004350BC` | `0x00438000` | 12,100 B | Free bootloader-partition headroom before Apollo main | Confirmed non-overlap |
| `0x00438000` | `0x00794324` | 3,523,364 B | Even main application blob | Confirmed by OTA preamble and bootloader installer |

The canonical Ghidra discovery manifest tiles this entire half-open range into
64 contiguous halfword-aligned chunks. Its 32-byte OTA staging preamble is
mapped immediately before the installed image at `[0x00437FE0,0x00438000)`.
Current whole-image analysis discovers 7,370 functions in chunks 0–33; chunks
34–63, beginning at `0x00600FAA`, contain no Ghidra-discovered function entry
and remain classified as data/resource-or-unresolved rather than being dropped
from the map.

An authenticated retained-path overlay adds module anchors without changing
segment ownership: 357 C source paths and 712 pointer cells map 314 paths to
1,760 discovered functions (530 third-party, 1,230 project/first-party).
The baseline has 43 paths without decompiler-token anchors and 5,610 functions
without a path anchor. A second raw recovery pass independently adds eight
call/table-backed entries across `[0x0043C400,0x0043C758)` and
the WSF timer cluster `[0x0052A474,0x0052A614)`, for a reviewed effective
count of 7,378; the
intervening AgingTest body `[0x0043C450,0x0043C496)` remains candidate-only.
No range is reclassified solely from literal adjacency, and exact
source/generated/opaque status remains governed by the production manifest.
See the [source-path census](research/apollo-embedded-source-path-census.md)
and [recovery audit](research/apollo-embedded-source-path-recovery.md).

The focused Cordio timer recovery maps the complete code cluster
`[0x0052A3FC,0x0052A614)` (536 bytes), its decoded literal table
`[0x0052A614,0x0052A63C)`, and dispatcher `[0x0052B9D0,0x0052BAB8)`.
SRAM ownership is now explicit: queue `[0x200741B0,0x200741B8)`, FreeRTOS
timer handle `[0x20074EF4,0x20074EF8)`, last tick
`[0x20074EF8,0x20074EFC)`, and WSF CS nesting byte `0x20075045`. These remain
stock-retained. All eleven code functions now have production-excluded
behavioral source; the literal table is fully decoded data, while exact IAR
placement/relocation remains pending. See the
[timer audit](research/cordio-wsf-timer-source-recovery.md).

The adjacent WSF OS module `[0x0052B8A4,0x0052BAB8)` is 532 bytes / 12
functions; the linked queue module `[0x00538C24,0x00538D16)` is 242 bytes /
six functions. Both are fully bounded and behaviorally recreated but remain
stock-retained. The OS literal table `[0x0052BAB8,0x0052BACC)` maps the CS
nesting byte `0x20075045`, event-group handle `0x20074EF0`, SCB ICSR
`0xE000ED04`, 64-byte task `[0x20073230,0x20073270)`, and embedded queue
`[0x20073264,0x2007326C)`. The task contains ten handlers and ten byte masks;
the queue contains two 32-bit pointers. See the
[OS/queue audit](research/cordio-wsf-os-queue-source-recovery.md).

The WSF buffer code `[0x00530364,0x00530512)` contains three bounded
functions / 430 bytes. Its four 12-byte pool records occupy
`[0x2004FA98,0x2004FAC8)`, followed by buffer pools
`[0x2004FAC8,0x200523C8)`: 8×16, 4×32, 10×64, and 20×480-byte blocks.
The complete allocation consumes `0x2930` bytes and leaves 16 bytes of the
supplied `0x2940` region. Descriptor input is initialized SRAM
`[0x200003B0,0x200003C0)`; globals are the memory pointer at `0x20074EEC`,
used-length halfword at `0x20074F4A`, and pool-count byte at `0x20075044`.
The linked WSF message cluster `[0x004BF990,0x004BFA0E)` is seven functions /
126 bytes and uses an eight-byte intrusive header before each public payload.
All remain stock-retained. See the
[buffer/message audit](research/cordio-wsf-buffer-message-source-recovery.md).

The linked WSF trace function `[0x0052A63C,0x0052A672)` is 54 bytes and uses
a transient 1,024-byte stack formatting buffer. Its associated newline/path
data occupies `[0x0052A672,0x0052A67C)`. The downstream-extended `WsfAssert`
body is `[0x00569A44,0x00569ADE)` (154 bytes), followed by its NOP/literal
table `[0x00569ADE,0x00569B04)`. The mutable EasyLogger assertion-hook pointer
is at `0x2007456C`. These spans and the hook remain stock-retained. See the
[assert/trace audit](research/cordio-wsf-assert-trace-source-recovery.md).

The linked WSF utility interval `[0x0056D8C4,0x0056D93A)` contains
`WStrReverseCpy` (44 bytes) followed by `WStrReverse` (74 bytes). Both are leaf
code with no literal table, global storage, function pointers, or opaque
interior bytes. They remain stock-retained. See the
[string-helper audit](research/cordio-wstr-source-recovery.md).

The ATT client-supported-features translation unit occupies the enclosing
interval `[0x0052C6C0,0x0052DA0C)`: ten linked functions contribute 4,814
code bytes and six intervening literal/string/data pools contribute 126 bytes.
Its BSS control block begins at `0x20073E04`: three two-byte `{csf,state}`
records occupy `+0..+5`, padding is `+6..+7`, the write callback is `+8`, and
the hash-update flag is `+0x0C`. `AttsCsfInit` is dead-stripped because BSS
zeroing already supplies its two defaults. All code/data and SRAM remain
stock-retained. See the
[ATT CSF audit](research/cordio-atts-csf-source-recovery.md).

The Cordio SMP pairing database occupies `[0x00541E34,0x005429F2)`: eleven
linked bodies contribute 2,952 bytes and the remaining 54 bytes are
literal/alignment data. Its BSS control block begins at `0x200708EC` and is
exactly `0x100` bytes: ten 24-byte records at `+0x00..+0xEF`, followed by a
16-byte WSF timer at `+0xF0`. The timer event is at `+0xFA` (`0x20`), handler
ID at `+0xFC`, and started flag at `+0xFD`. `pSmpCfg` is the pointer global at
`0x200004B8`; it initially selects `0x007759A4` and normal product init later
selects `0x00774D44`. Code/data and SRAM remain stock-retained. See the
[SMP DB audit](research/cordio-smp-db-source-recovery.md).

The complete ATT CCC translation unit occupies
`[0x0052BB64,0x0052C6C0)`: fourteen linked bodies contribute 2,770 bytes and
138 bytes are inline strings, alignment, and literal data. Its 24-byte BSS
control block begins at `0x20073B00`; three connection-table pointers occupy
`+0,+4,+8`, the settings pointer is `+0x0C`, application callback `+0x10`,
and setting count `+0x14`. Six 6-byte settings live at `0x007518C0`.
`attsCccMainCback` is registered through literal `0x0052C6A4` into
`attsCb+0x26C` (`0x2006E85C`). All code/data and SRAM remain stock-retained.
See the [ATT CCC audit](research/cordio-atts-ccc-source-recovery.md).

The complete ATT client-discovery translation unit occupies
`[0x0056B7EC,0x0056C3B0)`: fifteen linked bodies contribute 2,908 bytes and
four literal/alignment gaps contribute 104 bytes. The module owns no mutable
global; callers provide the 20-byte discovery control block containing three
list pointers, two list lengths, service bounds, and two state indices. All
code/data remains stock-retained. See the
[ATT discovery audit](research/cordio-attc-disc-source-recovery.md).

The legacy advertising executable interval `[0x004B9A80,0x004BAC4E)`
contains seventeen linked bodies / 4,396 bytes and 162 inline data bytes. Its
TU-owned 100-byte literal pool is `[0x004BAC64,0x004BACC8)`, separated by the
foreign vendor state accessor `[0x004BAC4E,0x004BAC64)`. Shared `dmAdvCb`
begins at `0x20073394` and carries two advertising sets; the legacy type byte
is at `0x20074FB3`. The action and component interfaces are at `0x0075F550`
and `0x0078A808`. All remain stock-retained. See the
[legacy advertising audit](research/cordio-dm-adv-leg-source-recovery.md).

The common advertising translation unit occupies
`[0x004B3098,0x004B32D4)`: nine linked bodies contribute 562 bytes and the
tailing literal/alignment pool contributes ten bytes. Shared `dmAdvCb` begins
at `0x20073394`, `dmCb` is at `0x20073B78`, and `DmAdvSetData` lays copied
payload immediately after its eight-byte message header. All code/data and
SRAM remain stock-retained. See the
[common advertising audit](research/cordio-dm-adv-source-recovery.md).

The Cordio DM connection manager occupies `[0x004B5B24,0x004B7478)`.
Fifty-seven linked bodies contribute 6,216 bytes, interstitial literal and
alignment data contributes 186 bytes through `0x004B7426`, and the trailing
literal pool contributes 82 bytes. `dmConnCb` occupies
`[0x200712A4,0x20071368)` (196 bytes): three 48-byte CCBs, five callback
pointers at `+0x90`, two connection specifications at `+0xA4`, scan interval
at `+0xBC`, and scan window at `+0xC0`. The main/update action-set cells are
at `0x20073FE4` / `0x20073FD8`. All remain stock-retained. See the
[DM connection-manager audit](research/cordio-dm-conn-source-recovery.md).

| `0x0043D260` | `0x0043D2CE` | 110 B | Source-replaced EasyLogger output-enabled setter | Complete upstream-equivalent control function replaced |
| `0x0043D2CE` | `0x0043D33C` | 110 B | Source-replaced EasyLogger text-color setter | Complete upstream-equivalent control function replaced |
| `0x0043D33C` | `0x0043D3A6` | 106 B | Source-replaced EasyLogger per-level format setter | Recovered logger-object ABI and assertion behavior preserved |
| `0x0043D3A6` | `0x0043D406` | 96 B | Source-replaced EasyLogger filter-level setter | Recovered logger-object ABI and assertion behavior preserved |
| `0x0043D406` | `0x0043D416` | 16 B | Source-replaced EasyLogger filter-tag setter | Stock 30-byte `strncpy` seam retained |
| `0x0043D416` | `0x0043D438` | 34 B | Source-replaced EasyLogger output lock | G2 port-lock seam retained |
| `0x0043D438` | `0x0043D45A` | 34 B | Source-replaced EasyLogger output unlock | G2 port-unlock seam retained |
| `0x0043D45A` | `0x0043D4B0` | 86 B | Source-replaced EasyLogger tag-level default initializer | Five 33-byte slots and 31-byte source-owned clearing preserved |
| `0x0043D4B0` | `0x0043D574` | 196 B | Source-replaced EasyLogger tag-level getter | First-match five-slot scan and 30-byte source-owned comparison preserved |
| `0x0043D97C` | `0x0043D9E6` | 106 B | Source-replaced EasyLogger `get_fmt_enabled` | Complete authenticated stock span redirected to shared source |
| `0x0043D9F0` | `0x0043DA0A` | 26 B | Source-replaced EasyLogger unsigned-argument predicate | Direct source call to `get_fmt_enabled` |
| `0x0043DA0A` | `0x0043DA24` | 26 B | Source-replaced EasyLogger pointer-argument predicate | Direct source call to `get_fmt_enabled` |
| `0x0043DA24` | `0x0043DA60` | 60 B | Source-replaced EasyLogger lock-enable transition | Complete upstream-equivalent control function replaced |
| `0x004416D6` | `0x004416F0` | 26 B | Source-replaced FreeRTOS V10.5.1 mutex creator | Complete public function replaced; stock generic-create and private initializer ABI retained |
| `0x004416F0` | `0x00441710` | 32 B | Source-replaced FreeRTOS V10.5.1 static mutex creator | Public wrapper links to the source-owned static generic creator and mutex initializer |
| `0x00441710` | `0x00441750` | 64 B | Source-replaced FreeRTOS V10.5.1 recursive mutex give | Current-owner recursion unwind preserved; final give links directly to the source queue-send implementation |
| `0x00441750` | `0x00441790` | 64 B | Source-replaced FreeRTOS V10.5.1 recursive mutex take | Current-owner recursion preserved; first take materializes patched odd public entry `0x00441C45` and calls it with `BLX` |
| `0x00441790` | `0x004417C2` | 50 B | Source-replaced FreeRTOS V10.5.1 static counting-semaphore creator | Public wrapper links to the source-owned static generic creator |
| `0x004417C2` | `0x004417EE` | 44 B | Source-replaced FreeRTOS V10.5.1 dynamic counting-semaphore creator | Public wrapper links to the source-owned dynamic generic creator |
| `0x004417EE` | `0x00441952` | 356 B | Source-replaced FreeRTOS V10.5.1 generic queue send | Complete public function replaced for mutex, semaphore, memory-pool, and real message-queue callers |
| `0x00441C44` | `0x00441DA6` | 354 B | Source-replaced FreeRTOS V10.5.1 semaphore/mutex take | Complete public function redirects to the authenticated upstream leaf; blocking, timeout, priority inheritance, and source-linked timeout disinheritance preserved |
| `0x00441EA2` | `0x00441EC4` | 34 B | Source-replaced FreeRTOS V10.5.1 `vQueueDelete` | Complete stock entry redirected to source heap-free and interrupt-mask dependencies |
| `0x00441EC4` | `0x00441ED8` | 20 B | Retained stock `prvGetDisinheritPriorityAfterTimeout` | Exact bytes remain opaque but assembled-image branch/pointer closure proves the body unreachable after its sole caller was promoted |
| `0x00441FF6` | `0x00442012` | 28 B | Source-replaced FreeRTOS V10.5.1 private queue-empty predicate | Semaphore take reaches the patched stock entry compatibility seam |
| `0x00442012` | `0x00442030` | 30 B | Source-replaced FreeRTOS V10.5.1 private queue-full predicate | Public queue source calls this predicate directly |
| `0x007B1AA8` | `0x007B1ABA` | 18 B | Appended FreeRTOS timeout-disinherit source helper | Apple canonical placement; relocation-free and sole target of the semaphore leaf's source call |
| `0x007B1ABA` | `0x007B1ABC` | 2 B | Generated alignment | Four-byte alignment before the semaphore leaf |
| `0x007B1ABC` | `0x007B1D16` | 602 B | Appended FreeRTOS `xQueueSemaphoreTake` source leaf | Apple canonical placement; sole relocation resolves to the preceding source helper |
| `0x0044228A` | `0x00442456` | 460 B | Source-replaced UI-module targeted event dispatcher | Complete stock function replaced |
| `0x00442456` | `0x00442524` | 206 B | Source-replaced UI-module mode-1 broadcast-close helper | Complete stock function replaced |
| `0x00442524` | `0x004425A6` | 130 B | Source-replaced UI-module common-data dispatcher | Complete stock function replaced |
| `0x004425A6` | `0x00442618` | 114 B | Source-replaced UI-module registry initializer | Complete stock function replaced |
| `0x00442618` | `0x0044264E` | 54 B | Source-replaced UI-module mode lookup | Complete stock function replaced |
| `0x0044264E` | `0x00442BA8` | 1,370 B | Source-replaced UI display-mode transition state machine | Complete stock function replaced |
| `0x00442BA8` | `0x00442CC8` | 288 B | Source-replaced UI startup application-ID policy | Complete stock function replaced |
| `0x00442CC8` | `0x00442D64` | 156 B | Shared UI display literal pool | Official bytes retained for stock consumers |
| `0x00442D64` | `0x00442D86` | 34 B | Source-replaced UI onboarding-state gate | Complete stock function replaced |
| `0x00442D86` | `0x0044347A` | 1,780 B | Source-replaced packed UI input-event handler | Complete stock function replaced; ring source calls linked internally |
| `0x0044347A` | `0x004437E0` | 870 B | Display input-handler literal pool | Official bytes retained |
| `0x004437E0` | `0x004441DE` | 2,558 B | Source-replaced registered main display-thread command loop | Complete stock function replaced; stored Thumb entry preserved |
| `0x004441DE` | `0x00444684` | 1,190 B | Display-thread literal/data pool before callback | Official bytes retained |
| `0x00444684` | `0x00444690` | 12 B | Source-replaced dynamic display callback wrapper | Complete stock function replaced |
| `0x00444690` | `0x00444694` | 4 B | Callback literal word | Official bytes retained |
| `0x00444694` | `0x004446A6` | 18 B | Source-replaced display preparation helper | Complete stock function replaced |
| `0x004446A6` | `0x004446B4` | 14 B | Inter-helper literal/data gap | Official bytes retained |
| `0x004446B4` | `0x004446FE` | 74 B | Source-replaced persistent input preparation helper | Complete stock function replaced |
| `0x004446FE` | `0x00444720` | 34 B | Post-helper literal/data gap | Official bytes retained |
| `0x00444720` | `0x0044484C` | 300 B | Source-replaced display-subsystem initializer | Complete stock function replaced; source thread registered directly |
| `0x0044484C` | `0x0044971C` | 20,176 B | Initializer literal/data pool and stock application before CMSIS mutex creation | Official bytes retained |
| `0x0044971C` | `0x004497B6` | 154 B | Source-replaced CMSIS-FreeRTOS v10.5.1 `osMutexNew` | Complete stock entry redirected to source |
| `0x004497B6` | `0x0044989A` | 228 B | Stock application between CMSIS mutex and semaphore creation | Official bytes retained |
| `0x0044989A` | `0x0044994E` | 180 B | Source-replaced CMSIS-FreeRTOS v10.5.1 `osSemaphoreNew` | Complete stock entry redirected to source queue and cleanup closure |
| `0x0044994E` | `0x00449A32` | 228 B | Stock application between CMSIS semaphore and message-queue creation | Official bytes retained |
| `0x00449A32` | `0x00449ABE` | 140 B | Source-replaced CMSIS-FreeRTOS v10.5.1 `osMessageQueueNew` | Complete stock entry redirected to the source leaf |
| `0x00449ABE` | `0x0044A43C` | 2,430 B | Stock application between CMSIS message-queue creation and string length | Official bytes retained |
| `0x0044A43C` | `0x0044A472` | 54 B | Source-replaced shared string-length primitive | Complete stock function replaced; 88 direct references preserved through entry redirect |
| `0x0044A472` | `0x0044B668` | 4,598 B | Stock application between string length and EasyLogger bounded copy | Official bytes retained |
| `0x0044B668` | `0x0044B70A` | 162 B | Source-replaced EasyLogger `elog_strcpy` | Complete authenticated stock span redirected to shared source |
| `0x0044B70A` | `0x0044F718` | 16,398 B | Stock application between EasyLogger bounded copy and the public heap wrappers | Official bytes retained |
| `0x0044F718` | `0x0044F730` | 24 B | Source-replaced public heap-allocation veneer | Zero-size sentinel and direct source-adapter call preserved |
| `0x0044F730` | `0x0044F758` | 40 B | Inter-wrapper stock application | Official bytes retained |
| `0x0044F758` | `0x0044F76A` | 18 B | Source-replaced public heap-free veneer | Null/sentinel no-op and direct source-adapter call preserved |
| `0x0044F76A` | `0x00454770` | 20,486 B | Stock application between the heap wrappers and bounded string length | Official bytes retained |
| `0x00454770` | `0x00454778` | 8 B | Source-replaced bounded string-length veneer | Complete stock function replaced |
| `0x00454778` | `0x00454EFE` | 1,926 B | Stock application before the FreeRTOS tick getters | Official bytes retained |
| `0x00454EFE` | `0x00454F06` | 8 B | Source-replaced FreeRTOS V10.5.1 `xTaskGetTickCount` | Complete stock entry redirected to the source getter |
| `0x00454F06` | `0x00454F10` | 10 B | Source-replaced FreeRTOS V10.5.1 `xTaskGetTickCountFromISR` | Corrected complete entry begins at `0x00454F06`; `0x00454F08` is interior |
| `0x00454F10` | `0x00454F16` | 6 B | Source-replaced FreeRTOS V10.5.1 `uxTaskGetNumberOfTasks` | Exact upstream getter bound to the recovered current-task-count word at `0x20074A30` |
| `0x00454F16` | `0x004555E6` | 1,744 B | Stock application before the FreeRTOS missed-yield setter | Official bytes retained |
| `0x004555E6` | `0x004555F0` | 10 B | Source-replaced FreeRTOS V10.5.1 `vTaskMissedYield` | Exact upstream store to recovered `xYieldPending` at `0x20074A44` |
| `0x004555F0` | `0x0045589C` | 684 B | Stock application between missed-yield and current-task getters | Official bytes retained |
| `0x0045589C` | `0x004558A4` | 8 B | Source-replaced FreeRTOS V10.5.1 `xTaskGetCurrentTaskHandle` | Exact upstream getter bound to `pxCurrentTCB` at `0x20074A20` |
| `0x004558A4` | `0x004558C4` | 32 B | Source-replaced FreeRTOS V10.5.1 `xTaskGetSchedulerState` | Exact upstream scheduler-state policy bound to the recovered scheduler globals at `0x20074A3C` and `0x20074A58` |
| `0x004558C4` | `0x00455ACA` | 518 B | Stock application before the FreeRTOS event-item reset leaf | Official bytes retained |
| `0x00455ACA` | `0x00455AE0` | 22 B | Source-replaced FreeRTOS V10.5.1 `uxTaskResetEventItemValue` | Exact upstream event-item reset preserving three volatile `pxCurrentTCB` evaluations |
| `0x00455AE0` | `0x00455AF6` | 22 B | Source-replaced FreeRTOS V10.5.1 `pvTaskIncrementMutexHeldCount` | Exact upstream held-mutex increment under `configUSE_MUTEXES=1` |
| `0x00455AF6` | `0x0045607C` | 1,414 B | Stock application before FreeRTOS list initialization | Official bytes retained |
| `0x0045607C` | `0x0045609A` | 30 B | Source-replaced FreeRTOS V10.5.1 `vListInitialise` | Exact upstream algorithm with recovered 32-bit list ABI |
| `0x0045609A` | `0x004560B2` | 24 B | Source-replaced FreeRTOS V10.5.1 `vListInsertEnd` | Exact upstream algorithm with recovered 32-bit list ABI |
| `0x004560B2` | `0x004560E8` | 54 B | Source-replaced FreeRTOS V10.5.1 `vListInsert` | Exact upstream sorted insertion with recovered 32-bit list ABI |
| `0x004560E8` | `0x0045610E` | 38 B | Source-replaced FreeRTOS V10.5.1 `uxListRemove` | Exact upstream algorithm with recovered 32-bit list ABI |
| `0x0045610E` | `0x00456110` | 2 B | Alignment gap before FreeRTOS heap | Official bytes retained |
| `0x00456110` | `0x00456210` | 256 B | Source-replaced FreeRTOS V10.5.1 `pvPortMalloc` | Complete stock entry redirected to bounded `heap_4` source |
| `0x00456210` | `0x00456280` | 112 B | Source-replaced FreeRTOS V10.5.1 `vPortFree` | Complete stock entry redirected to bounded `heap_4` source |
| `0x00456280` | `0x004562DA` | 90 B | Source-replaced FreeRTOS V10.5.1 `prvHeapInit` | Complete private stock body redirected to source |
| `0x004562DA` | `0x00456338` | 94 B | Source-replaced FreeRTOS V10.5.1 `prvInsertBlockIntoFreeList` | Complete private stock body redirected to source |
| `0x00456338` | `0x0045A568` | 16,944 B | Stock application between FreeRTOS heap and lens-side accessors | Official bytes retained |
| `0x0045A568` | `0x0045A570` | 8 B | Source-replaced lens-side accessor entry | Complete stock function replaced |
| `0x0045A570` | `0x0045A578` | 8 B | Source-replaced duplicate lens-side accessor entry | Complete stock function replaced |
| `0x0045A578` | `0x0045A6D0` | 344 B | Source-replaced five-read lens-side initializer | Complete stock function replaced |
| `0x00472C7C` | `0x00472C84` | 8 B | Source-replaced dynamic display-handler setter | Complete stock function replaced |
| `0x00472C84` | `0x00472D40` | 188 B | Source-replaced unsigned 64-bit divide-by-ten logging runtime | Complete stock function replaced; two historical callers preserved |
| `0x00472D40` | `0x00472EF6` | 438 B | Source-replaced non-floating logging formatter helper cluster | Eight complete stock functions replaced; formatter and float-helper callers preserved |
| `0x00472EF6` | `0x00473036` | 320 B | Source-replaced bounded floating-point logging converter | Complete stock function replaced; hard-float caller ABI preserved |
| `0x00473036` | `0x004733EE` | 952 B | Source-replaced application logging conversion parser and formatter core | Complete stock function replaced; two executable callers preserved |
| `0x004733EE` | `0x0047341A` | 44 B | Source-replaced application-wide variadic logging dispatcher | Complete stock function replaced; 731 direct callers preserved |
| `0x0047341A` | `0x00473474` | 90 B | Logging-dispatch literal/data pool | Official bytes retained |
| `0x00473474` | `0x00473482` | 14 B | Source-replaced LVGL tick increment helper | Complete stock function replaced; sole caller preserved |
| `0x00473482` | `0x004734A0` | 30 B | Source-replaced LVGL tick getter | Complete stock function replaced; ten executable callers preserved |
| `0x004734A0` | `0x004734BC` | 28 B | Source-replaced wrap-safe LVGL elapsed-time helper | Complete stock function replaced; five executable callers preserved |
| `0x004734BC` | `0x004734C0` | 4 B | LVGL tick-state SRAM literal | Official word `0x2006F600` retained |
| `0x004734C0` | `0x004734CC` | 12 B | Source-replaced LVGL zero-fill wrapper | Complete stock function replaced; sole caller preserved |
| `0x004734CC` | `0x00473548` | 124 B | Source-replaced LVGL global-state initializer | Complete stock function replaced; sole caller and retained LVGL list/finalize ABIs preserved |
| `0x00473548` | `0x00473626` | 222 B | Source-replaced LVGL subsystem initializer | Complete stock function replaced; sole caller and 17 retained subsystem ABIs preserved |
| `0x0047366C` | `0x004736F4` | 136 B | Source-replaced full-screen LVGL buffer synchronizer | Complete stock function replaced; sole caller and four retained display-port ABIs preserved |
| `0x004736F4` | `0x00473782` | 142 B | Source-replaced installed LVGL display synchronization callback | Complete stock function replaced; installed Thumb pointer and retained display ABIs preserved |
| `0x00473782` | `0x0047381E` | 156 B | Source-replaced LVGL display setup sequence | Complete stock function replaced; sole caller, callback registration, buffer allocation, and failure diagnostic preserved |
| `0x0047381E` | `0x0047386A` | 76 B | Source-replaced LVGL display-buffer lock | Complete stock function replaced; five callers and both diagnostics preserved |
| `0x0047386A` | `0x004738A8` | 62 B | Source-replaced LVGL display-buffer unlock | Complete stock function replaced; three callers and task/IRQ release paths preserved |
| `0x004738A8` | `0x004738DE` | 54 B | Source-replaced LVGL display-buffer mutex initializer | Complete executable body replaced; create diagnostic and unconditional initial release preserved |
| `0x004738DE` | `0x00473928` | 74 B | Inactive LVGL display synchronization literal pool | Official data retained after all consumers became source-owned |
| `0x00473928` | `0x00473934` | 12 B | Source-replaced LVGL display-port initializer | Complete stock function replaced; source-links mutex and display setup |
| `0x00473934` | `0x00473940` | 12 B | Source-replaced PRIMASK-read and IRQ-enable primitive | Complete stock span replaced; three callers preserved |
| `0x00473940` | `0x0047394C` | 12 B | Source-replaced PRIMASK-read and IRQ-disable primitive | Complete stock span replaced; 91 callers preserved |
| `0x0047394C` | `0x00473952` | 6 B | Source-replaced display-task attribute accessor | Complete stock function replaced; four callers and retained data pointer preserved |
| `0x00473952` | `0x004739FC` | 170 B | Source-replaced display-driver thread initializer | Complete stock function replaced; retained thread entry, attributes, handle publication, and logging policy preserved |
| `0x004739FC` | `0x00473AA4` | 168 B | Source-replaced display-driver message-queue initializer | Complete stock function replaced; sole direct caller, queue dimensions, handle publication, and logging policy preserved |
| `0x00473AA4` | `0x00473ABC` | 24 B | Source-replaced display-driver thread teardown | Complete stock function replaced; null gate and terminate-before-clear ordering preserved |
| `0x00473ABC` | `0x00473AC6` | 10 B | Source-replaced display resource-acquire wrapper | Complete stock function replaced; resource ID 12 preserved |
| `0x00473AC6` | `0x00473AD0` | 10 B | Source-replaced display resource-release wrapper | Complete stock function replaced; resource ID 12 preserved |
| `0x00473AD0` | `0x00473B34` | 100 B | Source-replaced display timer initializer | Complete stock function replaced; callback, attributes, publication, and failure diagnostics preserved |
| `0x00473B34` | `0x00473B46` | 18 B | Source-replaced display timer starter | Complete stock function replaced; 2,000-tick interval preserved |
| `0x00473B46` | `0x00473B54` | 14 B | Source-replaced display timer stopper | Complete stock function replaced |
| `0x00473B54` | `0x00473BC4` | 112 B | Source-replaced display timer callback | Complete stock function replaced; zeroed command-6 queue message and diagnostics preserved |
| `0x00473BC4` | `0x00473C44` | 128 B | Source-replaced byte-valued display queue command 8 | Complete stock function replaced; byte truncation, return normalization, and diagnostics preserved |
| `0x00473C44` | `0x00473E2E` | 490 B | Source-replaced display-driver manager thread | Complete receive/retry loop and commands 0–6/8 replaced; active/gate state, timer, forwarding, query, and diagnostics preserved |
| `0x00473E2E` | `0x00473EA0` | 114 B | Source-replaced asynchronous display clear-screen sender | Complete command-2 message and diagnostics preserved |
| `0x00473EA0` | `0x00473F12` | 114 B | Source-replaced asynchronous display initializer sender | Complete command-1 message and diagnostics preserved |
| `0x00473F12` | `0x00473F84` | 114 B | Source-replaced asynchronous display power-up sender | Complete command-0 message and diagnostics preserved |
| `0x00473F84` | `0x00473FF6` | 114 B | Source-replaced asynchronous display power-down sender | Complete command-5 message and diagnostics preserved |
| `0x00473FF6` | `0x00474066` | 112 B | Source-replaced asynchronous brightness-control sender | Complete command-4 word-seven payload and diagnostics preserved |
| `0x00474066` | `0x00474100` | 154 B | Source-replaced asynchronous reflash sender | Complete command-3 six-word payload, result ABI, four callers, and diagnostics preserved |
| `0x00474100` | `0x004742F8` | 504 B | Source-replaced forced display initializer | Complete active/running gates, command 0/1/3 sequence, return ABI, and diagnostics preserved |
| `0x004742F8` | `0x0047432C` | 52 B | Retained display lifecycle literal pool | Shared manager, attributes, file, tag, and diagnostic pointers remain stock |
| `0x0047432C` | `0x00474474` | 328 B | Source-replaced forced display deinitializer | Complete inactive gate, command 2/5 sequence, return ABI, and diagnostics preserved |
| `0x00474474` | `0x00474550` | 220 B | Retained display/file diagnostic and literal pool | Byte-exact official compatibility data |
| `0x00474550` | `0x004745F4` | 164 B | Source-replaced shared file-open wrapper | Allocation, mode flags, mutex, backend open, and cleanup ordering preserved |
| `0x004745F4` | `0x00474634` | 64 B | Source-replaced shared file-close wrapper | Mutex, backend close, unconditional free-after-close, and result normalization preserved |
| `0x00474634` | `0x00474682` | 78 B | Source-replaced shared file-read wrapper | Element-to-byte conversion, mutex, backend result, and element-count ABI preserved |
| `0x00474682` | `0x00474804` | 386 B | Source-replaced shared file-write wrapper | Complete mutex/backend path and null, timeout, error, and short-write diagnostics preserved |
| `0x00474804` | `0x00474814` | 16 B | Retained file-mode literal pool | Single-character `r`, `w`, `a`, and `+` strings remain stock between write and seek |
| `0x00474814` | `0x00474870` | 92 B | Source-replaced shared file-seek wrapper | Origin validation, signed offset, mutex/backend sequence, and zero/minus-one ABI preserved |
| `0x00474870` | `0x004748B4` | 68 B | Source-replaced shared file-tell wrapper | Null gate, mutex/backend sequence, position result, and negative normalization preserved |
| `0x004748B4` | `0x00474910` | 92 B | Source-replaced shared file-size wrapper | Null/mutex/backend failure errno mapping and successful size preservation retained |
| `0x00474910` | `0x0047498C` | 124 B | Source-replaced shared file-flush wrapper | Null/standard-stream no-op, mutex/backend sequence, errno mapping, and zero/minus-one ABI preserved |
| `0x0047498C` | `0x00474A02` | 118 B | Source-replaced shared path-removal wrapper | Runtime-ready gate, null validation, mutex/backend sequence, already-absent success, and errno mapping preserved |
| `0x00474A02` | `0x00474A76` | 116 B | Source-replaced shared path-rename wrapper | Runtime-ready gate, both-path validation, mutex/backend sequence, errno mapping, and zero/minus-one ABI preserved |
| `0x00474A76` | `0x00474B02` | 140 B | Source-replaced shared directory-create wrapper | Runtime-ready gate, ignored mode, mutex/backend sequence, and `EEXIST`/`ENOENT`/`EIO` mapping preserved |
| `0x00474B02` | `0x00474BB8` | 182 B | Source-replaced shared directory-open wrapper | 0x240-byte object, bounded path mirror, backend sequence, cleanup, and errno mapping preserved |
| `0x00474BB8` | `0x00474C66` | 174 B | Source-replaced shared directory-read wrapper | Global dirent ABI, end-of-directory result, bounded name copy, and type mapping preserved |
| `0x00474C66` | `0x00474CD2` | 108 B | Source-replaced shared directory-close wrapper | Runtime-ready no-op, validation, backend/free ordering, and errno mapping preserved |
| `0x00474CD2` | `0x00474D16` | 68 B | Source-replaced synchronized allocation wrapper | Separate mutex/heap handles, backend result, and timeout diagnostics preserved |
| `0x00474D16` | `0x00474D54` | 62 B | Source-replaced synchronized free wrapper | Separate mutex/heap handles, backend ordering, and timeout diagnostics preserved |
| `0x00474D54` | `0x00474D9C` | 72 B | Source-replaced synchronized reallocation wrapper | One direct caller, separate mutex/heap handles, backend result, and timeout diagnostics preserved |
| `0x00474D9C` | `0x00474E3C` | 160 B | Source-replaced file-runtime initializer | Both mutex creations/publications, success/failure ABI, and recovered diagnostics preserved |
| `0x00474E3C` | `0x00474EB4` | 120 B | Retained file-runtime literal pool | Heap, mutex, logging, and diagnostic pointers remain official compatibility data |
| `0x00474EB4` | `0x00474EFA` | 70 B | Source-replaced instruction-cache enable | Cache-power gate, invalidation, control-bit update, barriers, and status preserved |
| `0x00474EFA` | `0x00474F32` | 56 B | Source-replaced instruction-cache disable | Cache-power gate, control-bit clear, invalidation, barriers, and status preserved |
| `0x00474F32` | `0x00475014` | 226 B | Source-replaced data-cache enable | Prefetch configuration, set/way invalidation, optional clean, barriers, and status preserved |
| `0x00475014` | `0x0047510E` | 250 B | Source-replaced data-cache invalidate | Disabled-cache barriers, whole/range operations, optional clean, and low-byte selector preserved |
| `0x0047510E` | `0x00475194` | 134 B | Source-replaced data-cache clean | Disabled-cache barriers and whole/range clean operations preserved |
| `0x00475194` | `0x004751C8` | 52 B | Retained cache-controller literal pool | Power, SCB, maintenance-register, prefetch, and configuration addresses remain official data |
| `0x004751C8` | `0x00475230` | 104 B | Source-replaced application memory comparator | All 64 raw callers retain the stock byte-difference and aligned-word normalized-sign ABI |
| `0x00475230` | `0x00475286` | 86 B | Source-replaced Apollo510 secure-OTA addition | Sole caller retains MRAM validation, descriptor programming, status, and OTA-pointer ABI |
| `0x00475286` | `0x00475290` | 10 B | Retained secure-OTA literal pool | State address and OTA pointer register remain official data |
| `0x00475290` | `0x00475308` | 120 B | Source-replaced BLE message-transmit thread entry | Stored entry pointer, lifecycle order, flag dispatch, diagnostics, and retry loop preserved |
| `0x00475308` | `0x0047530A` | 2 B | Source-replaced BLE message-transmit application hook | Intentional `BX LR` no-op assembled exactly in place |
| `0x0047530A` | `0x00475332` | 40 B | Source-replaced BLE message-transmit queue initializer | 150×4-byte queue contract and fatal allocation failure preserved |
| `0x00475332` | `0x00475334` | 2 B | Source-replaced BLE message-transmit thread hook | Intentional `BX LR` no-op assembled exactly in place |
| `0x00475334` | `0x0047533E` | 10 B | Source-replaced BLE message-transmit stage-enter adapter | Retained stage backend and index 8 preserved |
| `0x0047533E` | `0x00475348` | 10 B | Source-replaced BLE message-transmit stage-leave adapter | Retained stage backend and index 8 preserved |
| `0x00475348` | `0x00475374` | 44 B | Source-replaced BLE message-transmit thread creator | CMSIS entry, argument, attributes, handle publication, and failure path preserved |
| `0x00475374` | `0x0047538C` | 24 B | Source-replaced BLE message-transmit thread destructor | Null-handle behavior, termination, and handle clearing preserved |
| `0x0047538C` | `0x004754BA` | 302 B | Source-replaced BLE message-transmit queue drain | Nonblocking polling, four command layouts, diagnostics, and message freeing preserved |
| `0x004754BA` | `0x004754D0` | 22 B | Source-replaced BLE message-transmit thread-flag router | Queue bit before wait bit and both handler calls preserved |
| `0x004754D0` | `0x00475524` | 84 B | Source-replaced BLE message-transmit wait handler | Stage index, diagnostics, and indefinite retained-backend wait preserved |
| `0x00475524` | `0x0047564E` | 298 B | Source-replaced BLE message-transmit queue clear | Null-handle behavior, queue depths, zero-timeout drain/free loop, and freed count preserved |
| `0x0047564E` | `0x00475A38` | 1,002 B | Source-replaced BLE message-transmit enqueue core | Four message layouts, source allocation/copy, stream reset, backpressure, queue submission, cleanup, and thread wakeup preserved |
| `0x00475A38` | `0x00475AA6` | 110 B | Source-replaced direct protobuf-over-BLE transmitter | OTA gate, argument truncation, enqueue forwarding, diagnostics, and return policy preserved |
| `0x00475AA6` | `0x00475B14` | 110 B | Source-replaced direct protobuf-notification-over-BLE transmitter | Subtype one, OTA gate, argument truncation, distinct diagnostics, and return policy preserved |
| `0x00475B14` | `0x00475C1A` | 262 B | Source-replaced guarded protobuf-over-BLE transmitter | OTA and left-lens rejection gates, exact diagnostics/statuses, argument truncation, enqueue forwarding, and return policy preserved across 76 callers |
| `0x00475C1A` | `0x00475D5E` | 324 B | Source-replaced guarded protobuf-notification transmitter | OTA, left-lens, and command-role gates, exact diagnostics/statuses, subtype-one forwarding, and return policy preserved across 39 callers |
| `0x00475D5E` | `0x00475D78` | 26 B | Retained BLE message-transmit literal pool | Shared module/file/state/thread-attribute pointers remain official data |
| `0x00475D78` | `0x00475DD8` | 96 B | Source-replaced streaming BLE notification wrapper | Two callers preserve OTA diagnostics/zero return, transport-one subtype-one forwarding, length truncation, and enqueue result |
| `0x00475DD8` | `0x00475DE0` | 8 B | Retained queue-diagnostic pointer pool | Two official diagnostic pointers remain separately mapped data |
| `0x00475DE0` | `0x00475DFA` | 26 B | Source-replaced transport-three BLE sender | Six callers preserve the ungated four-register forwarding ABI and enqueue result |
| `0x00475DFA` | `0x00475E62` | 104 B | Source-replaced EFS BLE sender | Five callers preserve OTA diagnostics/zero return, transport-two subtype zero, truncation, and enqueue result |
| `0x00475E62` | `0x00475E6C` | 10 B | Retained EFS-send literal pool | Alignment plus two official pointer literals remain separately mapped data |
| `0x00475E6C` | `0x00475ED4` | 104 B | Source-replaced EFS BLE notification wrapper | Sole caller preserves OTA diagnostics/status eight, transport-two subtype one, truncation, and enqueue result |
| `0x00475ED4` | `0x00475FC0` | 236 B | Retained BLE message-transmit pointer table | Shared dependency and diagnostic pointers remain official data |
| `0x00475FC0` | `0x00475FE2` | 34 B | Source-replaced variadic string-scanner adapter | Seven callers preserve AAPCS variadic forwarding, retained scan-engine ABI, return value, and source reader callback semantics |
| `0x00475FE2` | `0x00475FE8` | 6 B | Retained scanner-callback literal pool | Alignment and the now-inactive stock callback displacement remain separately mapped official data |
| `0x00475FE8` | `0x004761D2` | 490 B | Source-replaced littlefs directory check | Four-path existence/create/close loop and diagnostics preserved |
| `0x004761D2` | `0x0047627E` | 172 B | Source-replaced littlefs format helper | Unmount, format, remount, directory recovery, statuses, and diagnostics preserved |
| `0x0047627E` | `0x004763B8` | 314 B | Source-replaced littlefs initializer | Mount recovery, readiness publication, and boot-count persistence preserved |
| `0x004763B8` | `0x004763F0` | 56 B | Source-replaced littlefs flash-read callback | External-flash address calculation, status mapping, and diagnostics preserved |
| `0x004763F0` | `0x00476428` | 56 B | Source-replaced littlefs flash-program callback | External-flash address calculation, status mapping, and diagnostics preserved |
| `0x00476428` | `0x00476452` | 42 B | Source-replaced littlefs flash-erase callback | Block address calculation, status mapping, and diagnostics preserved |
| `0x00476452` | `0x004764DC` | 138 B | Retained littlefs dependency pool | Path, diagnostic, state, configuration, and boot-count pointers remain official data |
| `0x004764DC` | `0x004764E0` | 4 B | Source-replaced littlefs sync callback | Exact source-assembled constant-zero callback |
| `0x004764E0` | `0x0047667E` | 414 B | Source-replaced event-loop initializer | Queue, timer, mutex, and worker creation plus existing-worker replacement preserved |
| `0x0047667E` | `0x00476680` | 2 B | Retained event-loop alignment | Zero alignment before worker entry remains official data |
| `0x00476680` | `0x004766EC` | 108 B | Source-replaced event-loop worker | Blocking queue receive, callback invocation, error diagnostics, and continuation preserved |
| `0x004766EC` | `0x004767A8` | 188 B | Source-replaced event-loop queue push | Worker/queue guards, event layout, priority, caller timeout, and diagnostics preserved |
| `0x004767A8` | `0x0047697E` | 470 B | Source-replaced event-loop timer callback | 64-slot delay update/expiry, callback queueing, minimum selection, and timer/tick state preserved |
| `0x0047697E` | `0x00476ACE` | 336 B | Source-replaced delayed insertion | Worker wait, immediate path, first-free insertion, and timer rescheduling preserved |
| `0x00476ACE` | `0x00476BF0` | 290 B | Source-replaced delayed removal | All-match clearing, byte result, elapsed calculation, and timer rescheduling preserved |
| `0x00476BF0` | `0x00476CBC` | 204 B | Retained event-loop dependency pool | CMSIS handles/attributes, delayed state, and diagnostics remain official data |
| `0x00476CBC` | `0x00476DB8` | 252 B | Source-replaced BLE connection-parameter scheduler | Immediate update, retry state, diagnostics, and 2/4-second delayed scheduling preserved |
| `0x00476DB8` | `0x00476FE2` | 554 B | Source-replaced primary connection-mode selector | Interval/latency/timeout diagnostics and 25-unit `0xA3`/`0xA4` threshold preserved |
| `0x00476FE2` | `0x0047720C` | 554 B | Source-replaced secondary connection-mode selector | Interval/latency/timeout diagnostics and 72-unit `0xA3`/`0xA4` threshold preserved |
| `0x0047720C` | `0x0047761C` | 1,040 B | Source-replaced BLE connection-mode coordinator | Context validation, selector policy, pending state, delayed retry, command packet, and diagnostics preserved |
| `0x0047761C` | `0x0047773E` | 290 B | Source-replaced BLE connection delayed callback | Controller/context/role gates, `0xB9` packet, endpoint send, diagnostics, and return-register ABI preserved |
| `0x0047773E` | `0x00477774` | 54 B | Retained BLE connection callback literal pool | Official dependency and diagnostic pointers remain separately mapped data |
| `0x00477774` | `0x00477A6A` | 758 B | Source-replaced BLE remote connection-parameter handler | Received parameters, diagnostics, secondary-mode selection, state publication, and role-gated 60-second retry preserved |
| `0x00477A6A` | `0x00477ADC` | 114 B | Retained BLE remote-parameter literal pool | Official dependency, diagnostic, state, and callback pointers remain separately mapped data |
| `0x00477ADC` | `0x004780D8` | 1,532 B | Source-replaced BLE connection-update event state machine | Status policy, 25/72-unit thresholds, state publication, and 2/4/10/30/60-second retry paths preserved |
| `0x004780D8` | `0x004780DC` | 4 B | Retained BLE connection-event literal | Official diagnostic pointer remains separately mapped data |
| `0x004780DC` | `0x004780F8` | 28 B | Source-replaced BLE connection-global initializer | Endpoint, connection/state pointers, and fixed defaults-table pointer preserved |
| `0x004780F8` | `0x0047810C` | 20 B | Source-replaced BLE stream-readiness helper | Current-mode `0xA3` predicate preserved |
| `0x0047810C` | `0x00478110` | 4 B | Retained BLE readiness literal | Official diagnostic pointer remains separately mapped data |
| `0x00478110` | `0x0047814C` | 60 B | Source-replaced BLE short-mode scheduler | Optional 60-second long-mode restoration and immediate short mode preserved |
| `0x0047814C` | `0x00478160` | 20 B | Retained BLE short-mode literal pool | Official diagnostic pointers remain separately mapped data |
| `0x00478160` | `0x004781F0` | 144 B | Source-replaced BLE stream-reset helper | Retry timestamp and 30-second holdoff behavior preserved |
| `0x004781F0` | `0x004781F4` | 4 B | Retained BLE stream-reset literal | Official diagnostic pointer remains separately mapped data |
| `0x004781F4` | `0x00478252` | 94 B | Source-replaced BLE remote-mode reset | Diagnostics, remote-active clearing, and immediate short mode preserved |
| `0x00478252` | `0x0047826C` | 26 B | Source-replaced BLE long-mode scheduler | Caller-provided delay and callback replacement preserved |
| `0x0047826C` | `0x004782DC` | 112 B | Retained BLE control literal pool | Official state, callback, and diagnostic pointers remain separately mapped data |
| `0x004782DC` | `0x004786B4` | 984 B | Source-replaced BLE connection-event dispatcher | Seven recovered message classes, state/default mapping, dependency calls, and diagnostics preserved |
| `0x004786B4` | `0x004787A4` | 240 B | Retained BLE dispatcher dependency pool | Official state, profile-default, diagnostic, callback, and dependency pointers remain separately mapped data |
| `0x004787A4` | `0x00478860` | 188 B | Source-replaced MRAM zero-region programmer | Cache invalidation, byte zeroing, word-count truncation, protected programming, PRIMASK restoration, and diagnostics preserved |
| `0x00478860` | `0x00478966` | 262 B | Source-replaced protected update-flag setter | Idempotence, four-word template, `0x55555555`/`0xFFFFFFFF` selectors, MRAM programming, and diagnostics preserved |
| `0x00478966` | `0x004789B0` | 74 B | Retained MRAM persistence literal pool | Official size, buffer, destination, key, template, and diagnostic pointers remain separately mapped data |
| `0x004789B0` | `0x004793EA` | 2,618 B | Source-replaced protected-MRAM record diagnostic dump | Byte-index selection, all record fields, sparse tables, hex ranges, labels, and diagnostic gates preserved |
| `0x004793EA` | `0x00479418` | 46 B | Retained MRAM diagnostic front-literal pool | Official record base, selector labels, and initial diagnostic pointers remain separately mapped data |
| `0x00479418` | `0x0047956C` | 340 B | Source-replaced protected-MRAM record synchronizer | Two-pass filtering, pointer reload, record mutation, ordered publication, final marker, batch commit, diagnostics, and register preservation retained |
| `0x0047956C` | `0x004795DC` | 112 B | Retained shared MRAM record diagnostic literal pool | Official function, module, file, label, hex-tag, and identity pointers remain separately mapped data |
| `0x004795DC` | `0x00479982` | 934 B | Source-replaced protected-MRAM-to-RAM record-list loader | Ten-slot loading, sentinel stop, key-mask repair, persistence, validity filtering, destination clearing/copy, counts, and diagnostics preserved |
| `0x00479982` | `0x004799A8` | 38 B | Retained MRAM record diagnostic continuation pool | Official protected-record labels and identities remain separately mapped data |
| `0x004799A8` | `0x00479AB4` | 268 B | Source-replaced protected-MRAM single-record programmer | Two 128-byte program transactions, thread-mode yield, status aggregation, and diagnostics preserved |
| `0x00479AB4` | `0x00479B74` | 192 B | Retained MRAM single-record programmer literal pool | Official destination, key, diagnostic identity, module, file, function, and dependency pointers remain separately mapped data |
| `0x00479B74` | `0x0047A462` | 2,286 B | Source-replaced protected-MRAM application record-database updater | Existing/empty selection, full-table replacement priorities, programming, verification, and diagnostics preserved |
| `0x0047A462` | `0x0047A47C` | 26 B | Retained MRAM application record-database updater literal pool | Official record base, type labels, diagnostic identities, and dependency pointers remain separately mapped data |
| `0x0047A47C` | `0x0047A49C` | 32 B | Source-replaced protected-MRAM record-deactivation adapter | Both activity flags, database persistence, NVM verification, call order, and verifier result preserved |
| `0x0047A49C` | `0x0047A5B6` | 282 B | Source-replaced protected-MRAM record-activation adapter | Mask diagnostics/truncation, ordered flag mutation, monotonic timestamp, database persistence, verification, exact-success diagnostic, and full-width return preserved |
| `0x0047A5B6` | `0x0047A5C0` | 10 B | Retained MRAM record-activation padding/literal pool | Official compatibility bytes remain separately mapped data |
| `0x0047A5C0` | `0x0047A5D0` | 16 B | Source-replaced protected-MRAM conditional deactivation adapter | Confirmation byte `0x30` gate, same-pointer deactivation call, and no-op path preserved |
| `0x0047A5D0` | `0x0047A600` | 48 B | Source-replaced protected-MRAM active-record membership query | Ten-record bounds, both activity flags, and exact pointer identity preserved |
| `0x0047A600` | `0x0047A62C` | 44 B | Source-replaced protected-MRAM untyped-record presence query | Allocated flag and zero type preserved; confirmation remains irrelevant |
| `0x0047A62C` | `0x0047A630` | 4 B | Retained MRAM query literal | Official record-table pointer remains separately mapped data |
| `0x0047A630` | `0x0047A676` | 70 B | Source-replaced protected-MRAM next-active-record traversal | Null-base and arbitrary-pointer traversal semantics preserved |
| `0x0047A676` | `0x0047A6AC` | 54 B | Source-replaced protected-MRAM active-type counter | Low-byte type matching and confirmation independence preserved |
| `0x0047A6AC` | `0x0047A6B4` | 8 B | Retained MRAM query literal pool | Official record-table and diagnostic pointers remain separately mapped data |
| `0x0047A6B4` | `0x0047A700` | 76 B | Source-replaced protected-MRAM oldest-active-type selector | Low-byte type, both flags, strict first minimum, and `UINT32_MAX` exclusion preserved |
| `0x0047A700` | `0x0047A71C` | 28 B | Retained MRAM query trailing literal pool | Official record-table and allocator pointers remain separately mapped data |
| `0x0047A71C` | `0x0047A856` | 314 B | Source-replaced protected-MRAM record allocator | Type threshold eviction, first-free selection, zero/init order, low-byte fields, timestamping, and diagnostics preserved |
| `0x0047A856` | `0x0047A85C` | 6 B | Retained MRAM allocator alignment/literal gap | Official compatibility bytes remain separately mapped data |
| `0x0047A85C` | `0x0047A892` | 54 B | Source-replaced protected-MRAM record initialization wrapper | Cache invalidation, record loading, synchronization, and all ten diagnostic dumps preserved |
| `0x0047A892` | `0x0047A8C4` | 50 B | Retained MRAM initialization literal pool | Official record-table and dependency pointers remain separately mapped data |
| `0x0047A8C4` | `0x0047AB4E` | 650 B | Source-replaced Cordio application-database address resolver | Null rejection, RPA/IRK submission, owner mapping, paired-record matching, and diagnostics preserved |
| `0x0047AB4E` | `0x0047AB6C` | 30 B | Retained address-resolver diagnostic pointer pool | Official compatibility bytes remain separately mapped data |
| `0x0047AB6C` | `0x0047ACEA` | 382 B | Source-replaced Cordio resolved-address callback | Record validation, resolved-address diagnostics, and LTK-valid return preserved |
| `0x0047ACEA` | `0x0047ACF8` | 14 B | Retained resolved-address callback diagnostic pointer pool | Official compatibility bytes remain separately mapped data |
| `0x0047ACF8` | `0x0047AD6A` | 114 B | Source-replaced Cordio application-database delete-all adapter | Per-record flag/address clearing, diagnostics, and protected-database persistence preserved |
| `0x0047AD6A` | `0x0047AD74` | 10 B | Retained delete-all adapter record-table and diagnostic pointer pool | Official compatibility bytes remain separately mapped data |
| `0x0047AD74` | `0x0047ADC6` | 82 B | Source-replaced Cordio application-database address lookup | Owner normalization, first active address match, and timestamp refresh preserved |
| `0x0047ADC6` | `0x0047ADD4` | 14 B | Retained address-lookup compatibility pointer pool | Official compatibility bytes remain separately mapped data |
| `0x0047ADD4` | `0x0047AE26` | 82 B | Source-replaced Cordio security-database LTK-request lookup | Diversifier/random matching, first-match selection, and timestamp refresh preserved |
| `0x0047AE26` | `0x0047AE78` | 82 B | Retained shared Cordio compatibility pointer pool | Official compatibility bytes remain separately mapped data |
| `0x0047AE78` | `0x0047AEC0` | 72 B | Source-replaced Cordio application-database key accessor | Four key classes, valid-mask gating, security-level outputs, and unsupported-type behavior preserved |
| `0x0047AEC0` | `0x0047AEC8` | 8 B | Source-replaced peer-address accessor | Record-base address and null contract preserved |
| `0x0047AEC8` | `0x0047AED4` | 12 B | Source-replaced peer-address-type accessor | Offset-six byte and null sentinel `0xFF` preserved |
| `0x0047AED4` | `0x0047B3AE` | 1,242 B | Source-replaced Cordio application-database key writer | Local/peer LTK, IRK, CSRK, diagnostics, mask updates, and exact-one persistence preserved |
| `0x0047B3AE` | `0x0047B3CC` | 30 B | Source-replaced peer database-hash setter | Exact 16-byte copy, persistence, and verification preserved |
| `0x0047B3CC` | `0x0047B3E2` | 22 B | Source-replaced cache-by-hash setter | Record flag update, persistence, and verification preserved |
| `0x0047B3E2` | `0x0047B40C` | 42 B | Source-replaced CCC-table setter | Low-16-bit index, low-byte connection ID, conditional persistence, and helper order preserved |
| `0x0047B40C` | `0x0047B418` | 12 B | Source-replaced client-supported-features getter | State and record-byte pointer outputs preserved |
| `0x0047B418` | `0x0047B438` | 32 B | Source-replaced client-supported-features setter | Null contracts and two-byte record mutation preserved |
| `0x0047B438` | `0x0047B45A` | 34 B | Source-replaced client change-aware-state setter | One-record and all-ten-record behavior preserved |
| `0x0047B45A` | `0x0047B460` | 6 B | Source-replaced device database-hash getter | Fixed protected-MRAM hash address preserved |
| `0x0047B460` | `0x0047B468` | 8 B | Retained database-hash getter literal/alignment pool | Official compatibility bytes remain separately mapped data |
| `0x0047B468` | `0x0047B47E` | 22 B | Source-replaced device database-hash setter | Null no-op and exact 16-byte copy preserved |
| `0x0047B47E` | `0x0047B488` | 10 B | Retained database-hash setter literal/alignment pool | Official compatibility bytes remain separately mapped data |
| `0x0047B488` | `0x0047B48E` | 6 B | Source-replaced discovery-status setter | Exact record byte preserved |
| `0x0047B48E` | `0x0047B4AC` | 30 B | Source-replaced handle-list setter | Exact 42-byte copy, persistence, and verification preserved |
| `0x0047B4AC` | `0x0047B4C8` | 28 B | Retained record-metadata helper literal pool | Official compatibility bytes remain separately mapped data |
| `0x0047B4C8` | `0x0047B4CE` | 6 B | Source-replaced peer sign-counter setter | Exact 32-bit record field preserved |
| `0x0047B4CE` | `0x0047B4D4` | 6 B | Source-replaced peer address-resolution setter | Exact record byte preserved |
| `0x0047B4D4` | `0x0047B568` | 148 B | Source-replaced Cordio resolving-list reload wrapper | Before/after diagnostics, retained reload request, and source-owned MRAM synchronization preserved |
| `0x0047B568` | `0x0047B59C` | 52 B | Retained resolving-list reload literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047B59C` | `0x0047B6DC` | 320 B | Source-replaced Cordio record clearing by MAC address | Null/miss/success diagnostics, source-owned lookup/deactivation, and retained record release preserved |
| `0x0047B6DC` | `0x0047B730` | 84 B | Retained record-clearing literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047B730` | `0x0047BBF8` | 1,224 B | Source-replaced protected-MRAM write verifier | Cache invalidation, first persisted-record match, flags, selected keys, diagnostics, and hex dumps preserved |
| `0x0047BBF8` | `0x0047BC30` | 56 B | Retained write-verifier literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047BC30` | `0x0047C06A` | 1,082 B | Source-replaced protected-MRAM record-status reporter | Slot classifications, timestamps, masks, device identifiers, strict oldest/newest selection, and diagnostics preserved |
| `0x0047C06A` | `0x0047C084` | 26 B | Retained record-status literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047C084` | `0x0047C14A` | 198 B | Source-replaced Cordio record timestamp-update wrapper | Null guard, overflow reset, counter increment, record write, diagnostics, persistence, and verification preserved |
| `0x0047C14A` | `0x0047C164` | 26 B | Retained timestamp-update literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047C164` | `0x0047C276` | 274 B | Source-replaced Cordio record timestamp-renumbering routine | Counter reset, ten-slot allocation/activity scan, slot-ordered timestamp assignment, diagnostics, and persistence preserved |
| `0x0047C276` | `0x0047C2BC` | 70 B | Retained timestamp-renumbering literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047C2BC` | `0x0047C504` | 584 B | Source-replaced Cordio persistent-record status reporter | Cache clean/invalidation, ten-slot filtering, address/key display, counts, geometry, and diagnostics preserved |
| `0x0047C504` | `0x0047C568` | 100 B | Retained persistent-record status literal pool | Official diagnostic and dependency pointers remain separately mapped data |
| `0x0047C568` | `0x0047C8A2` | 826 B | Source-replaced Cordio pairing-failure handler | NVM report, connection lookup, record qualification, SMP reason handling, clearing policy, and diagnostics preserved |
| `0x0047C8A2` | `0x0047C8CC` | 42 B | Retained alignment and diagnostic pointer data | Official compatibility bytes remain separately mapped data |
| `0x0047C8CC` | `0x0047CA98` | 460 B | Source-replaced Cordio connection-indexed pairing-record clearer | Handle lookup, record qualification, MAC-address clear, resolving-list reload, flag clearing, and diagnostics preserved |
| `0x0047CA98` | `0x0047CA9C` | 4 B | Retained record-clear dependency pointer | Official compatibility data remains separately mapped |
| `0x0047CA9C` | `0x0047CABE` | 34 B | Source-replaced Cordio all-record diagnostic iterator | Single table-holder read, ten slots, 200-byte stride, and source-owned record dumps preserved |
| `0x0047CABE` | `0x0047CBC4` | 262 B | Retained record-iterator compatibility pool | Official alignment, table data, pointers, and record-table holder literal remain separately mapped |
| `0x0047CBC4` | `0x0047CBE8` | 36 B | Source-replaced EFS non-reflected CRC-32C updater | Castagnoli polynomial, caller state, incremental update, and zero-length behavior preserved without the opaque table |
| `0x0047CBE8` | `0x0047CC14` | 44 B | Source-replaced protected-MRAM byte-program wrapper | Word rounding, interrupt masking/restoration, program key, arguments, and ignored result preserved |
| `0x0047CC14` | `0x0047CC1C` | 8 B | Retained CRC/MRAM literals | Official CRC-table pointer and protected-program key remain separately mapped compatibility data |
| `0x0047CC1C` | `0x0047CC5E` | 66 B | Source-replaced ARM EABI signed 64-bit division/modulo front end | Signed magnitude conversion, quotient/remainder signs, divide-by-zero policy, and four-register ABI preserved |
| `0x0047CC5E` | `0x0047CC60` | 2 B | Retained ARM EABI alignment | Official alignment bytes remain separately mapped compatibility data |
| `0x0047CC60` | `0x0047CE90` | 560 B | Source-replaced ARM EABI unsigned 64-bit division/modulo core | Full-width quotient/remainder, divide-by-zero policy, and `r0:r1`/`r2:r3` result ABI preserved |
| `0x0047CE90` | `0x0047CED6` | 70 B | Source-replaced template-3 lens/status packet reporter | Source template, two side samples, state bit 2, eight-byte size, and command `0x103` preserved |
| `0x0047CED6` | `0x0047CF28` | 82 B | Source-replaced template-6 lens/status packet reporter | Source template, opposite-side mapping, state bit 4 to status `2/3`, and send ABI preserved |
| `0x0047CF28` | `0x0047CF60` | 56 B | Source-replaced template-5 lens/status packet reporter | Source template, side fields, zero status byte, and send ABI preserved |
| `0x0047CF60` | `0x0047D818` | 2,232 B | Retained command-`0x103` lens-status dispatcher | Registered function pointer at `0x006A4744`; retained as one function-specific compatibility blob |
| `0x0047D818` | `0x0047D870` | 88 B | Source-replaced lens-status publisher | Availability/selector policy, diagnostics, and template-5/template-6 dispatch preserved |
| `0x0047D870` | `0x0047D8B8` | 72 B | Source-replaced template-4 lens/status packet reporter | Source template, two side samples, boolean status byte, eight-byte size, and command `0x103` preserved |
| `0x0047D8B8` | `0x0047D8FC` | 68 B | Five source-replaced lens-status state accessors | State bits 0, 1, 4, and 5 plus the paired bits-2-and-3 predicate preserved |
| `0x0047D8FC` | `0x0047D9C4` | 200 B | Retained lens-status literal pool | Official diagnostic, dependency, template, and state pointers remain separately mapped data |
| `0x0047D9C4` | `0x0047D9CC` | 8 B | Source-replaced lens-status availability wrapper | Retained query result is propagated unchanged |
| `0x0047D9CC` | `0x0047D9FA` | 46 B | Source-replaced selected-side status query | Selector chooses source-owned state bit 4 or 5 and normalizes the result |
| `0x0047D9FA` | `0x0047D9FC` | 2 B | Retained query alignment | Official two-byte alignment pad remains separately mapped compatibility data |
| `0x0047D9FC` | `0x0047DA16` | 26 B | Source-replaced SARC state-header checksum wrapper | Payload-length bound, 20-byte header, zero seed, and retained checksum ABI preserved |
| `0x0047DA16` | `0x0047DA58` | 66 B | Source-replaced SARC state validator | `SARC` magic, valid marker, payload-length bounds, and header-checksum comparison preserved |
| `0x0047DA58` | `0x0047DA78` | 32 B | Source-replaced SARC state initializer | Existing magic preservation and exact 4,524-byte zero initialization preserved |
| `0x0047DA78` | `0x0047DAC0` | 72 B | Source-replaced SARC report appender | Variadic formatting, 4,499-byte saturation, stock equality-only full gate, and termination policy preserved |
| `0x0047DAC0` | `0x0047DB02` | 66 B | Source-replaced SARC report finalizer | Magic, validity, sequence, payload copy/termination, flags, and header checksum preserved |
| `0x0047DB02` | `0x0047DC22` | 288 B | Source-replaced SARC report persistence | Record validation, 100 KiB rollover, exact header/payload/footer writes, diagnostics, and sequence-preserving clear preserved |
| `0x0047DC22` | `0x0047DC74` | 82 B | Retained SARC compatibility pool | Alignment, retired local mode/status strings, and old literals retained as separately mapped inactive compatibility data |
| `0x0047DC74` | `0x0047DCB4` | 64 B | Source-replaced wrap-extending monotonic-seconds helper | Exact interrupt-state restoration, 32-bit tick-wrap accumulation, and 64-bit milliseconds-to-seconds division preserved |
| `0x0047DCB4` | `0x0047DCE4` | 48 B | Source-replaced bounded wall-clock seconds helper | Conditional wall-clock query, raw return value, output validity flag, and 2024-through-2099 unsigned validity window preserved |
| `0x0047DCE4` | `0x0047DCEC` | 8 B | Source-replaced interrupt-disable primitive | Existing source-owned `PRIMASK` capture and IRQ-disable implementation reused |
| `0x0047DCEC` | `0x0047DD08` | 28 B | Source-replaced boot reset-status word helper | Exact 16-byte zeroed staging buffer, retained reset-status provider, ignored provider result, and signed halfword return preserved |
| `0x0047DD08` | `0x0047DD62` | 90 B | Source-replaced firmware-version encoder | Source-owned `2.2.6.10` string, first-three-decimal-component parsing, and `major << 16 \| minor << 8 \| patch` packing preserved |
| `0x0047DD62` | `0x0047DD8A` | 40 B | Source-replaced tracepoint deferral dispatcher | Query-controlled 2,000-tick timer rearm or EasyLogger event-bit fallback preserved |
| `0x0047DD8A` | `0x0047DD92` | 8 B | Source-replaced tracepoint timer callback | Callback argument ignored; deferral dispatcher invoked directly |
| `0x0047DD92` | `0x0047DDAC` | 26 B | Source-replaced tracepoint deferral begin helper | Null-handle guard and retry-counter clear before dispatch preserved |
| `0x0047DDAC` | `0x0047DDFE` | 82 B | Source-replaced tracepoint capture retry | Deferred 2,000-tick path, capture-before-limit ordering, signed ten-retry ceiling, and 5,000-tick successful retry preserved |
| `0x0047DDFE` | `0x0047DE0A` | 12 B | Source-replaced tracepoint state CRC-32 | Standard reflected CRC-32 over the first 12 state-record bytes preserved |
| `0x0047DE0A` | `0x0047DE18` | 14 B | Source-replaced tracepoint path formatter | Exact `/log/tp/tp_%u.bin` path and bounded formatter ABI preserved |
| `0x0047DE18` | `0x0047DE7A` | 98 B | Source-replaced tracepoint filename parser | `tp_` prefix, `.bin` suffix, decimal index, and exact suffix-boundary validation preserved |
| `0x0047DE7A` | `0x0047DEB4` | 58 B | Source-replaced tracepoint file-size query | Read-open, seek-end, positive-tell normalization, and unconditional close preserved |
| `0x0047DEB4` | `0x0047DF28` | 116 B | Source-replaced tracepoint directory scan | File-type filter and unsigned count/minimum/maximum index discovery preserved |
| `0x0047DF28` | `0x0047DF8A` | 98 B | Source-replaced tracepoint state writer | Exact 16-byte `TPS1`, sequence, next-index, CRC record and `wb` write policy preserved |
| `0x0047DF8A` | `0x0047DFEC` | 98 B | Source-replaced tracepoint state loader | Exact read, magic/CRC validation, sequence restore, and next-index minimum-one normalization preserved |
| `0x0047DFEC` | `0x0047E06A` | 126 B | Source-replaced tracepoint storage initializer | Idempotence, directory creation, state load, sequence advance, directory recovery, active-file window, state persistence, and ready flag preserved |
| `0x0047E06A` | `0x0047E080` | 22 B | Source-replaced tracepoint active-file closer | Conditional close and handle clearing preserved |
| `0x0047E080` | `0x0047E088` | 8 B | Retained tracepoint prefix data | Alignment and `tp_` compatibility literal retained |
| `0x0047E088` | `0x0047E090` | 8 B | Source-replaced tracepoint close callback | Active-file closer invoked directly |
| `0x0047E090` | `0x0047E0C8` | 56 B | Source-replaced tracepoint file pruner | Repeated scan and minimum-index removal until fewer than four files preserved |
| `0x0047E0C8` | `0x0047E13E` | 118 B | Source-replaced tracepoint file creator | Index advance/persist, `wb` create, exact 32-byte header write, and active-state publication preserved |
| `0x0047E13E` | `0x0047E144` | 6 B | Retained tracepoint mode data | Alignment and `rb` compatibility literal retained |
| `0x0047E144` | `0x0047E172` | 46 B | Source-replaced tracepoint append opener | Active-index path formatting and `ab` open preserved |
| `0x0047E172` | `0x0047E178` | 6 B | Retained tracepoint mode data | Alignment and `wb` compatibility literal retained |
| `0x0047E178` | `0x0047E1EC` | 116 B | Source-replaced tracepoint writer | Readiness gate, 32 KiB rollover, reopen/create policy, exact write, and size accounting preserved |
| `0x0047E1EC` | `0x0047E220` | 52 B | Source-replaced tracepoint commit helper | Payload-presence threshold, close, and active-state clearing preserved |
| `0x0047E220` | `0x0047E232` | 18 B | Source-replaced tracepoint flush helper | Null-handle no-op and file-flush result propagation preserved |
| `0x0047E232` | `0x0047E272` | 64 B | Source-replaced tracepoint timer bootstrap | Idempotent one-shot creation, 2,000-tick period, handle publication, fail-stop, retained setup, and initial deferral dispatch preserved |
| `0x0047E272` | `0x0047E2D0` | 94 B | Retained tracepoint literal/data pool | Reviewed globals, timer storage, former callback entry, timer name, and neighboring literals retained as compatibility data |
| `0x0047E2D0` | `0x0047E320` | 80 B | Source-replaced protobuf onboarding control update | Pending-state clear, eight-bit command dispatch, mutex-protected configuration update, and command acknowledgement policy preserved |
| `0x0047E320` | `0x0047E3E6` | 198 B | Source-replaced protobuf onboarding wear-status notifier | OTA/transport/mode gates, 12-byte event template, byte-truncated status, notification ABI, and success/failure diagnostics preserved |
| `0x0047E3E6` | `0x0047E470` | 138 B | Source-replaced deferred onboarding-flag persistence | Exact pending-value gate, pre-save diagnostics, success-only clear, and failure retention preserved |
| `0x0047E470` | `0x0047E4A6` | 54 B | Source-replaced onboarding-flag updater | Low-byte change detection, retained storage update, deferred-persistence scheduling, and event-bit signaling preserved |
| `0x0047E4A6` | `0x0047E51C` | 118 B | Source-replaced peer onboarding-flag notification | Exact `{0x0D, flag}` RPC payload, retained transport ABI, and structured/trace diagnostics preserved |
| `0x0047E51C` | `0x0047E58E` | 114 B | Source-replaced peer onboarding-flag reply | Exact `{0x0E, flag}` RPC payload, retained transport ABI, and structured/trace diagnostics preserved |
| `0x0047E58E` | `0x0047E60A` | 124 B | Source-replaced peer onboarding-process synchronization | Exact `{0x09, process_id, substep}` RPC payload, volatile state refresh, retained transport ABI, and diagnostics preserved |
| `0x0047E60A` | `0x0047E674` | 106 B | Retained onboarding process data | Reviewed state pointer and shared neighboring diagnostic literal table retained |
| `0x0047E674` | `0x0047E6DC` | 104 B | Source-replaced onboarding runtime initializer | Core initialization, prerequisite gate, exact timer-service thread attributes/publication, success ABI, and fail-stop path preserved |
| `0x0047E6DC` | `0x0047E712` | 54 B | Source-replaced dynamic RTOS timer-object creator | Exact 44-byte allocation, ownership-byte clear, six-argument shared initializer ABI, null handling, and return identity preserved |
| `0x0047E712` | `0x0047E75A` | 72 B | Source-replaced static-control-block RTOS timer-object creator | Exact 44-byte contract check, required caller-owned block, static ownership byte, six-argument shared initializer ABI, return identity, and fail-stop policy preserved |
| `0x0047E75A` | `0x0047E7B0` | 86 B | Source-replaced shared RTOS timer initializer | Zero-period fail-stop, runtime initialization, exact object-field writes, periodic flag merge, and 32-bit pointer ABI preserved |
| `0x0047E7B0` | `0x0047E812` | 98 B | Source-replaced RTOS timer command submission | Null guards, exact three-word message, signed task/ISR split, scheduler-dependent wait, wake-pointer forwarding, and exact send result preserved |
| `0x0047E812` | `0x0047E83A` | 40 B | Source-replaced RTOS auto-reload catch-up loop | Unsigned deadline arithmetic, active-list insertion, fresh period reads, callback ordering, and repeated expiry processing preserved |
| `0x0047E83A` | `0x0047E878` | 62 B | Source-replaced RTOS expired-timer processor | Active-list-head resolution, intrusive-list removal, periodic/one-shot handling, direct source reload, and final callback preserved |
| `0x0047E878` | `0x0047E88C` | 20 B | Source-replaced RTOS timer-service task loop | Active-list query, wait/expiry processing, command draining, and non-returning iteration order preserved |
| `0x0047E88C` | `0x0047E8F2` | 102 B | Source-replaced RTOS timer wait-or-expire processor | Scheduler suspension/resume, list-switch handling, unsigned deadline comparison, overflow-list policy, queue wait, and conditional yield preserved |
| `0x0047E8F2` | `0x0047E916` | 36 B | Source-replaced RTOS active-timer-list query | Normalized empty output and nonempty head-expiry lookup through current-list word `0x20074AA8` preserved |
| `0x0047E916` | `0x0047E93C` | 38 B | Source-replaced RTOS tick/list-switch sampler | Single tick sample, unsigned wrap detection against `0x20074AB8`, active/overflow-list switch, normalized output, and last-tick publication preserved |
| `0x0047E93C` | `0x0047E97A` | 62 B | Source-replaced RTOS timer-list insertion helper | Timer item fields, unsigned wrap/elapsed classification, active/overflow-list selection, and normalized expiry result preserved |
| `0x0047E97A` | `0x0047EA90` | 278 B | Source-replaced RTOS timer-command drain | Exact 16-byte queue message ABI, pended calls, list removal, commands 1–9, activation, period changes, deletion, callbacks, and fresh volatile reads preserved |
| `0x0047EA90` | `0x0047EAB8` | 40 B | Source-replaced RTOS timer-list overflow switch | Current-list timers drain at tick `0xFFFFFFFF` before exact current/overflow pointer swap |
| `0x0047EAB8` | `0x0047EAF6` | 62 B | Source-replaced RTOS timer list/queue runtime initializer | Critical-section-protected one-time list initialization, pointer publication, and 50-by-16-byte static queue creation preserved |
| `0x0047EAF6` | `0x0047EB26` | 48 B | Source-replaced RTOS timer active-state query | Null fail-stop, critical-section-protected status-byte read, active-bit extraction, and normalized result preserved |
| `0x0047EB26` | `0x0047EB4A` | 36 B | Source-replaced RTOS timer callback-context getter | Null fail-stop, critical-section-protected object-offset-`0x1C` read, and unchanged pointer return preserved |
| `0x0047EB4A` | `0x0047EB6C` | 34 B | Source-replaced RTOS timer pended-callback ISR submission | Exact four-word daemon message, queue handle, wake pointer, ISR send ABI, copy position, and return preserved |
| `0x0047EB6C` | `0x0047EB94` | 40 B | RTOS timer runtime literal pool | Reviewed queue/task handles, timer name, list pointers/objects, last tick, and static queue control/storage retained |
| `0x0047EB94` | `0x0047EBD8` | 68 B | Source-replaced static RTOS event-group constructor | Exact 32-byte ABI check, event bits, wait-list initialization, static ownership byte, fail-stop policy, and buffer return preserved |
| `0x0047EBD8` | `0x0047EBF8` | 32 B | Source-replaced dynamic RTOS event-group constructor | Exact allocation size, null policy, event bits, wait-list initialization, dynamic ownership byte, and allocation return preserved |
| `0x0047EBF8` | `0x0047ED10` | 280 B | Source-replaced RTOS event-group wait operation | Validation, scheduler suspension/resume, immediate and timeout paths, any/all matching, clear-on-exit, control bits, yield, and return masking preserved |
| `0x0047ED10` | `0x0047ED52` | 66 B | Source-replaced RTOS event-group clear-bits operation | Group/control-mask validation, zero-mask behavior, critical section, distinct return/update reads, masked update, and original snapshot return preserved |
| `0x0047ED52` | `0x0047ED64` | 18 B | Source-replaced RTOS event-group clear-from-ISR submission wrapper | Source clear callback, full group/mask forwarding, null wake pointer, direct source callback/pended-submission dependencies, and unchanged result preserved |
| `0x0047ED64` | `0x0047ED76` | 18 B | Source-replaced RTOS event-group ISR-safe bit-snapshot getter | BASEPRI save/raise, one volatile bit read, exact mask restore, and unchanged full-width snapshot preserved |
| `0x0047ED76` | `0x0047EE1E` | 168 B | Source-replaced RTOS event-group set-bits operation | Scheduler suspension, any/all waiter matching, clear-on-exit accumulation, cached-next removal traversal, unblock snapshots, resume, and returned bits preserved |
| `0x0047EE1E` | `0x0047EE26` | 8 B | Source-replaced RTOS event-group set-bits timer callback | Exact group/mask forwarding, ignored result, and direct source set-bits dependency preserved |
| `0x0047EE26` | `0x0047EE28` | 2 B | Retained callback alignment | Reviewed zero alignment before the clear-bits timer callback |
| `0x0047EE28` | `0x0047EE30` | 8 B | Source-replaced RTOS event-group clear-bits timer callback | Exact group/mask forwarding, ignored result, and direct source clear-bits dependency preserved |
| `0x0047EE30` | `0x0047EE4A` | 26 B | Source-replaced RTOS event-group wait-condition predicate | Exact any/all selection, full-width intersection/equality, nonzero selector policy, and normalized result preserved |
| `0x0047EE4A` | `0x0047EE5A` | 16 B | Source-replaced RTOS event-group set-from-ISR submission wrapper | Source set callback, full group/mask/wake-pointer forwarding, direct source pended-submission dependency, absent validation, and unchanged result preserved |
| `0x0047EE5A` | `0x0047EE5C` | 2 B | Retained wrapper alignment | Reviewed zero alignment after the set-from-ISR wrapper |
| `0x0047EE5C` | `0x0047EE60` | 4 B | Retained set-callback Thumb literal | Reviewed `0x0047EE1F` compatibility pointer; the source wrapper materializes its source callback directly |
| `0x0047EE60` | `0x0047EE78` | 24 B | Source-replaced priority-1 RTC initializer | XTAL selection through both reviewed Ambiq clock paths, RTC oscillator enable, unrelated-bit preservation, zero return, and initializer-table registration preserved |
| `0x0047EE78` | `0x0047EEFA` | 130 B | Source-replaced RTC calendar/time setter | 2000-based input mapping, SDK weekday/validation behavior, BCD register packing, write-enable sequencing, result normalization, and failure diagnostics preserved |
| `0x0047EEFA` | `0x0047EF10` | 22 B | Retained RTC setter data island | Two alignment bytes and five reviewed diagnostic pointers remain compatibility data |
| `0x0047EF10` | `0x0047EF18` | 8 B | Source-replaced RTC calendar/time getter wrapper | IRQ-protected RTC-edge polling workaround, timer-14 setup, ordered counter reads, read-error handling, BCD field decoding, and void caller ABI preserved |
| `0x0047EF18` | `0x0047EF38` | 32 B | Source-replaced Apollo510 peripheral-power descriptor lookup | Ambiq invalid-argument result, 34-entry bounds, exact four-word copy, and private caller ABI preserved |
| `0x0047EF38` | `0x0047EF74` | 60 B | Source-replaced Apollo510 trim-version getter | One-time INFO1 word `0x244` read, `0x200001E8` cache, zero/error normalization, null-output status six, and sole caller ABI preserved |
| `0x0047EF74` | `0x0047F0A0` | 300 B | Source-replaced Apollo510 MCU HP/LP switching sequence | SPOT preflight/rollback, HFRC2 forcing, readiness and ACK polling, mode cache, status propagation, and exact interrupt restoration preserved |
| `0x0047F0A0` | `0x0047F108` | 104 B | Source-replaced Apollo510 public MCU-mode selector | Low-byte validation, SIMOBUCK gating, already-selected short circuit, switching status propagation, and hardware-state verification preserved |
| `0x0047F108` | `0x0047F11C` | 20 B | Source-replaced Apollo510 public GPU-mode status getter | Null-output status six, cached byte at `0x20074F60`, one-byte copy, and sole caller ABI preserved |
| `0x0047F11C` | `0x0047F204` | 232 B | Source-replaced Apollo510 public GPU-mode selector | Validation, SIMOBUCK and graphics-use gates, cached modes, voltage/performance sequencing, SPOT TON updates, settle delays, and exact interrupt restoration preserved |
| `0x0047F204` | `0x0047F3C6` | 450 B | Source-replaced Apollo510 public MCU memory-power configuration | Short-enum ABI, ROM/TCM/NVM transitions, SPOT coordination, bounded waits, AXI-clock forcing, verification, and retention policy preserved |
| `0x0047F3C6` | `0x0047F418` | 82 B | Source-replaced Apollo510 public ROM power-domain enable | AUTO gate, SPOT desired status, enable-bit update, bounded readiness polling, ignored SPOT status, and timeout preserved |
| `0x0047F418` | `0x0047F46A` | 82 B | Source-replaced Apollo510 public ROM power-domain disable | AUTO gate, enable-bit clear, bounded status polling, post-clear SPOT notification, ignored SPOT status, and timeout-without-SPOT behavior preserved |
| `0x0047F46A` | `0x0047F56E` | 260 B | Source-replaced Apollo510 public shared-SRAM power configuration | Five-byte short-enum ABI, SPOT ordering, enable/status verification, active-client and retain fields, and override clearing preserved |
| `0x0047F56E` | `0x0047F5B8` | 74 B | Source-replaced Apollo510 private crypto power-down quiesce helper | MRAM crypto-ready check, crypto-idle fallback, power-down-bit update, final ready check, and exact status propagation preserved |
| `0x0047F5B8` | `0x0047F6F2` | 314 B | Source-replaced Apollo510 public peripheral-power enable routine | Descriptor lookup, low-byte ABI, GPU/device/audio SPOT policy, critical enable write, readiness checks, and crypto/OTP special handling preserved |
| `0x0047F6F2` | `0x0047F7AE` | 188 B | Source-replaced Apollo510 private peripheral-disable domain-mask checker | Low-byte descriptor lookup and five shared-domain last-enabled-member masks preserved |
| `0x0047F7AE` | `0x0047F90C` | 350 B | Source-replaced Apollo510 public peripheral-power disable routine | OTP/crypto and debug gates, critical enable clear, shared-domain status wait, GPU/clock and SPOT policy, and TempCo sequencing preserved |
| `0x0047F90C` | `0x0047F942` | 54 B | Source-replaced Apollo510 public peripheral enabled-state query | Null validation, output clearing, low-byte descriptor lookup, status-register predicate, and error propagation preserved |
| `0x0047F942` | `0x0047F954` | 18 B | Retained data/alignment island | Official bytes between the peripheral enabled-state query and INFO1 cache-population routine |
| `0x0047F954` | `0x0047FAB4` | 352 B | Source-replaced Apollo510 private INFO1 cache-population routine | Hardware-validity gates, nine ordered INFO1 reads, partial commits, and final validity marker preserved |
| `0x0047FAB4` | `0x0047FAE8` | 52 B | Retained data island | Official constants between INFO1 cache population and low-power initialization |
| `0x0047FAE8` | `0x0047FE12` | 810 B | Source-replaced Apollo510 public low-power initializer | Reset erratum, power/clock/OTP/INFO1 policy, factory trims, retention, SPOT/SIMOBUCK sequencing, interrupt restoration, and revision gates preserved |
| `0x0047FE12` | `0x0047FE68` | 86 B | Source-replaced Apollo510 private buck/LDO override initializer | Ten ordered volatile `MCUCTRL->VRCTRL` read/modify/write operations for SIMOBUCK, CoreLDO, and MemLDO preserved |
| `0x0047FE68` | `0x0047FE6C` | 4 B | Retained literal | Official `0x40021028` word after the buck/LDO override initializer |
| `0x0047FE6C` | `0x0047FE94` | 40 B | Source-replaced Apollo510 private dynamic buck/LDO override updater | Input low bit copied into SIMOBUCK, CoreLDO, and MemLDO override fields through three fresh volatile read/modify/write operations |
| `0x0047FE94` | `0x0047FEA0` | 12 B | Retained literal island | Official `0x4002101C`, `0x40021024`, and `0x4002102C` words after the dynamic override updater |
| `0x0047FEA0` | `0x0047FFBA` | 282 B | Source-replaced Apollo510 public miscellaneous power-control dispatcher | Low-byte command dispatch, SIMOBUCK initialization, crypto power-down, deep-sleep crystal shutdown, and ordered all-peripheral disable policy preserved |
| `0x0047FFBA` | `0x0047FFC4` | 10 B | Retained data island | Official compatibility bytes immediately after the miscellaneous power-control dispatcher |
| `0x0047FFC4` | `0x00480002` | 62 B | Source-replaced Apollo510 public CPDLPSTATE configurator | Packed short-enum ABI, cache-use safety gate, field packing, and status policy preserved |
| `0x00480002` | `0x00480004` | 2 B | Retained alignment pad | Official zero bytes between the CPDLPSTATE configurator and following function |
| `0x00480004` | `0x00480008` | 4 B | Retained compatibility pointer | Official `0x20074F61` word immediately before the CPDLPSTATE getter |
| `0x00480008` | `0x00480028` | 32 B | Source-replaced Apollo510 public CPDLPSTATE getter | Single state-register read and three-byte RLP/ELP/CLP short-enum output preserved |
| `0x00480028` | `0x00480058` | 48 B | Source-replaced Apollo510 public temperature-update routine | Hard-float input ABI, SPOT-manager call, threshold copy, and normalized failure outputs preserved |
| `0x00480058` | `0x0048009E` | 70 B | Source-replaced Apollo510 public system-PLL enable routine | B1 isolation release, ordered PLL rail-power updates, critical section, and settle delays preserved |
| `0x0048009E` | `0x004800DE` | 64 B | Source-replaced Apollo510 public system-PLL disable routine | Ordered PLL rail power-down, B1 isolation assertion, critical section, and one-microsecond delay preserved |
| `0x004800DE` | `0x004800E0` | 2 B | Retained alignment pad | Official zero bytes between the system-PLL disable routine and following literal |
| `0x004800E0` | `0x004800E4` | 4 B | Retained `PWRCTRLMODESTATUS` literal | Official `0x40021040` word still loaded by the earlier power-control routine at `0x0047F556` |
| `0x004800E4` | `0x004800F4` | 16 B | Source-replaced Apollo510 public system-PLL enabled-state query | Single `PLLCTL0` read, one-byte boolean output, and success status preserved |
| `0x004800F4` | `0x004801FC` | 264 B | Retained power-control literal pool | 66 reviewed register, state, constant, and compatibility-pointer words |
| `0x004801FC` | `0x00480240` | 68 B | Source-replaced Apollo510 public SPOT-manager timer initializer | Ordered timer disable/configuration, mode/compare writes, interrupt clear, and compare-0 interrupt enable preserved |
| `0x00480240` | `0x0048028A` | 74 B | Source-replaced Apollo510 public SPOT-manager timer-start routine | HFRC clock request, delay-to-tick scaling, global enable, clear-bit toggle, NVIC enable, and timer enable preserved |
| `0x0048028A` | `0x004802CE` | 68 B | Source-replaced Apollo510 public SPOT-manager timer-restart routine | Ordered disable and clear pulse, delay-to-tick scaling, compare interrupt acknowledgement, pending-IRQ clear, and final timer enable preserved |
| `0x004802CE` | `0x00480312` | 68 B | Source-replaced Apollo510 public SPOT-manager timer-stop routine | Timer/global disable, HFRC release, IRQ disable and acknowledgement, APB write flush, and pending-IRQ clear preserved |
| `0x00480312` | `0x0048032C` | 26 B | Source-replaced SPOT-manager power-state update dispatcher | Slots `+0x04`, byte-truncated stimulus/enable, third argument, null success, and fresh call-time handler read preserved |
| `0x0048032C` | `0x00480342` | 22 B | Source-replaced SPOT-manager TempCo-postpone dispatcher | Slot `+0x0C`, null success, and fresh call-time handler read preserved |
| `0x00480342` | `0x00480358` | 22 B | Source-replaced SPOT-manager pending-TempCo dispatcher | Slot `+0x10`, null success, and fresh call-time handler read preserved |
| `0x00480358` | `0x0048036E` | 22 B | Source-replaced SPOT-manager pre-override SIMOBUCK dispatcher | Slot `+0x14`, null success, and fresh call-time handler read preserved |
| `0x0048036E` | `0x00480384` | 22 B | Source-replaced SPOT-manager pre-enable SIMOBUCK dispatcher | Slot `+0x18`, null success, and fresh call-time handler read preserved |
| `0x00480384` | `0x0048039A` | 22 B | Source-replaced SPOT-manager post-enable SIMOBUCK dispatcher | Slot `+0x1C`, null success, and fresh call-time handler read preserved |
| `0x0048039A` | `0x004803AC` | 18 B | Source-replaced SPOT-manager timer-interrupt dispatcher | Void callback at slot `+0x2C`; null no-op and fresh call-time handler read preserved |
| `0x004803AC` | `0x004803C2` | 22 B | Source-replaced SPOT-manager TON-configuration initializer dispatcher | Slot `+0x20`, null success, and fresh call-time handler read preserved |
| `0x004803C2` | `0x004803DC` | 26 B | Source-replaced SPOT-manager TON-configuration update dispatcher | Slot `+0x24`, both byte-truncated arguments, null success, and fresh call-time handler read preserved |
| `0x004803DC` | `0x004803F2` | 22 B | Source-replaced SPOT-manager post-LP-to-HP dispatcher | Slot `+0x28`, null success, and fresh call-time handler read preserved |
| `0x004803F2` | `0x00480408` | 22 B | Source-replaced SPOT-manager SIMOBUCK low-power autoswitch initializer | Slot `+0x30`, null success, and fresh call-time handler read preserved |
| `0x00480408` | `0x0048041E` | 22 B | Source-replaced SPOT-manager SIMOBUCK low-power autoswitch-enable dispatcher | Slot `+0x34`, null success, and fresh call-time handler read preserved |
| `0x0048041E` | `0x00480434` | 22 B | Source-replaced SPOT-manager SIMOBUCK low-power autoswitch-disable dispatcher | Slot `+0x38`, null success, and fresh call-time handler read preserved |
| `0x00480434` | `0x004806D0` | 668 B | Source-replaced Apollo510 public SPOT-manager initializer | Complete revision/trim matrix, six cached flags, ordered analog-rail repair, 15-slot callback table, return policy, and sole caller preserved |
| `0x004806D0` | `0x004807A0` | 208 B | Retained shared SPOT-manager and initializer literal pool | Timer register literals plus reviewed state/global/handler pointers remain stock compatibility data |
| `0x004807A0` | `0x004807FC` | 92 B | Source-replaced Apollo510 microsecond delay | Exact source-assembled in place; all 116 stock callers preserved |
| `0x004807FC` | `0x00480826` | 42 B | Source-replaced Apollo510 masked status-change wait helper | Initial read, exact timeout budget, one-microsecond polling delay, success/timeout statuses, and 14 reviewed executable callers preserved |
| `0x00480826` | `0x0048086A` | 68 B | Source-replaced Apollo510 equal/not-equal masked status wait helper | Byte-truncated mode, single read per poll, exact timeout budget, and 24 reviewed callers preserved |
| `0x0048086A` | `0x00480872` | 8 B | Source-replaced Apollo510 public word-copy wrapper | Forward volatile word-copy order and nonzero-count precondition preserved; former call to private ITCM `0x00000048` removed |
| `0x00480872` | `0x00480874` | 2 B | Retained alignment | Stock zero padding between reviewed function boundaries |
| `0x00480874` | `0x004809C4` | 336 B | Source-replaced private Apollo510 MCUCTRL device-information collector | 64-byte ABI, fresh SKU reads, RAM/MRAM sizing, JEDEC PID/CID decoding, and ten reviewed delays preserved |
| `0x004809C4` | `0x00480C56` | 658 B | Source-replaced public Apollo510 MCUCTRL control dispatcher | Seven low-byte commands, oscillator RMW sequences, argument rules, clock request/release ordering, and backend status propagation preserved |
| `0x00480C56` | `0x00480C7C` | 38 B | Source-replaced public Apollo510 external-32-MHz-clock status getter | External-clock precedence, fresh powered-state read, byte-sized enum store, and sole caller preserved |
| `0x00480C7C` | `0x00480D72` | 246 B | Source-replaced private Apollo510 MCUCTRL trim-version decoder | INFO1 word `0x244`, chip-revision qualification, PCM/non-PCM packing, reader-status propagation, and sole caller preserved |
| `0x00480D72` | `0x00480E6C` | 250 B | Source-replaced public Apollo510 MCUCTRL information getter | Low-byte selector ABI, feature mapping from nine fresh SKU reads, null/invalid status, and source-owned trim/device dispatch preserved |
| `0x00480E6C` | `0x00480ED8` | 108 B | Retained MCUCTRL information-getter literal/alignment pool | Stock compatibility data before the already source-owned GPIO interrupt helper |
| `0x00480ED8` | `0x00480EEE` | 22 B | Source-replaced GPIO interrupt-index helper | Complete stock function replaced |
| `0x00480EEE` | `0x00480F0C` | 30 B | Source-replaced Apollo510 GPIO pin-configuration reader | Complete stock function replaced |
| `0x00480F0C` | `0x00480F8A` | 126 B | Source-replaced Apollo510 GPIO pin configuration | Complete stock function replaced |
| `0x00480F8A` | `0x00480FD6` | 76 B | Source-replaced Apollo510 GPIO state reader | Complete stock function replaced |
| `0x00480FD6` | `0x004810B0` | 218 B | Source-replaced Apollo510 GPIO state writer | Complete stock function replaced |
| `0x004810B0` | `0x004812F6` | 582 B | Source-replaced Apollo510 GPIO interrupt control | Complete stock function replaced |
| `0x004812F6` | `0x00481468` | 370 B | Source-replaced Apollo510 GPIO interrupt status | Complete stock function replaced |
| `0x00481468` | `0x00481574` | 268 B | Source-replaced Apollo510 GPIO interrupt clear | Complete stock function replaced |
| `0x00481574` | `0x004815F2` | 126 B | Source-replaced IRQ-specific GPIO status helper | Complete stock function replaced |
| `0x004815F2` | `0x0048162C` | 58 B | Source-replaced IRQ-specific GPIO clear helper | Complete stock function replaced |
| `0x0048162C` | `0x004816C6` | 154 B | Source-replaced GPIO interrupt-handler registration | Complete stock function replaced |
| `0x004816C6` | `0x0048173A` | 116 B | Source-replaced GPIO interrupt-handler service | Complete stock function replaced |
| `0x0048173A` | `0x00481818` | 222 B | Retained GPIO literal/data pool and alignment | Official compatibility bytes preserved |
| `0x00481818` | `0x0048182E` | 22 B | Source-replaced shared character-search primitive | Byte-truncated search value, first-match/terminator return, and absent-character null result preserved |
| `0x0048182E` | `0x00481830` | 2 B | Retained alignment | Stock zero padding between reviewed function boundaries |
| `0x00481830` | `0x00481836` | 6 B | Source-replaced shared ASCII case-folding primitive | Exact unsigned 32-bit `value \| 0x20` behavior and sole executable caller preserved |
| `0x00481836` | `0x00482518` | 3,298 B | Retained formatting core, literal pool, and alignment | Official compatibility bytes preserved before the integer-formatting helper |
| `0x00482518` | `0x0048262C` | 276 B | Source-replaced shared integer-formatting helper | Recovered 64-bit decimal/octal/hex conversion, precision, alternate-form, field-width, and pointer-bound behavior preserved |
| `0x0048262C` | `0x00482672` | 70 B | Source-replaced shared decimal power-scaling helper | Recovered non-negative exponentiation-by-squaring order and fixed double-multiply ABI preserved |
| `0x00482672` | `0x00482684` | 18 B | Retained alignment and literal pool | Official compatibility constants preserved after the decimal-scaling helper |
| `0x00482684` | `0x004826B2` | 46 B | Source-replaced runtime byte-span emitter | Callback state threading, failure, count, and byte-extension behavior preserved |
| `0x004826B2` | `0x004826FC` | 74 B | Retained runtime alignment and data | Official scalar and literal words preserved before the zero-fill adapter |
| `0x004826FC` | `0x00482708` | 12 B | Source-replaced runtime zero-fill adapter | Source-owned forward clearing and destination return now replace the retained byte-fill call |
| `0x00482708` | `0x00482716` | 14 B | Source-replaced runtime lookup-layout predicate | Exact byte-eight `0xFF` sentinel comparison preserved |
| `0x00482716` | `0x0048277E` | 104 B | Source-replaced dual-layout byte-map lookup | Static `{key,value}` records and mutable split value/key arrays preserved |
| `0x0048277E` | `0x0048278C` | 14 B | Source-replaced property-group index helper | Exact low-byte shift and index-31 saturation preserved |
| `0x0048278C` | `0x00482796` | 10 B | Source-replaced style initializer | Complete 12-byte descriptor zeroing preserved through the source zero adapter |
| `0x00482796` | `0x004827B0` | 26 B | Source-replaced style reset | Mutable table release, static-table preservation, and final descriptor zeroing preserved |
| `0x004827B0` | `0x00482868` | 184 B | Source-replaced style-property removal | Static rejection, packed stable copy, transactional allocation failure, and duplicate-key behavior preserved |
| `0x00482868` | `0x00482946` | 222 B | Source-replaced style-property mutation | Reverse duplicate lookup, packed reallocation, diagnostics, fatal path, and cached group bitmap preserved |
| `0x00482946` | `0x00482950` | 10 B | Source-replaced public byte-map lookup adapter | Low-byte property normalization and direct source-owned lookup preserved |
| `0x00482950` | `0x0048297C` | 44 B | Source-replaced transition-descriptor initializer | Six-word ABI, 20-byte layout, default path, timing, delay, and user context preserved |
| `0x0048297C` | `0x00482A5A` | 222 B | Source-replaced style default-value dispatcher | All property classes, volatile defaults, and three-byte `r1` padding behavior preserved |
| `0x00482A5A` | `0x00482A6A` | 16 B | Source-replaced style-empty predicate | Exact byte-eight zero test preserved |
| `0x00482A6A` | `0x00482AB2` | 72 B | Source-replaced style-property flag lookup | Special properties, source-owned built-in table, and custom-table bounds preserved |
| `0x00482AB2` | `0x00482B00` | 78 B | Retained style alignment and literal pool | Shared neighboring-function literals remain official compatibility data |
| `0x00482B00` | `0x00482B12` | 18 B | Source-replaced linked-list initializer | Head/tail clearing and 32-bit four-byte node-size rounding preserved |
| `0x00482B12` | `0x00482B56` | 68 B | Source-replaced linked-list head insertion | Allocation, link writes, and descriptor publication order preserved |
| `0x00482B56` | `0x00482BCA` | 116 B | Source-replaced linked-list insert-before routine | Null guards, head delegation, and malformed-previous behavior preserved |
| `0x00482BCA` | `0x00482C0E` | 68 B | Source-replaced linked-list tail insertion | Allocation, link writes, and descriptor publication order preserved |
| `0x00482C0E` | `0x00482C9A` | 140 B | Source-replaced linked-list unlink routine | Head, tail, middle, and nonmember mutation behavior preserved without freeing |
| `0x00482C9A` | `0x00482CD8` | 62 B | Source-replaced linked-list callback-clear routine | Next-first traversal and callback-or-remove/free ownership preserved |
| `0x00482CD8` | `0x00482D22` | 74 B | Source-replaced linked-list accessors | Null-safe head/tail, node-link offsets, and source traversal length preserved |
| `0x00482D22` | `0x00482D88` | 102 B | Source-replaced linked-list move-before routine | Exact remove/relink order, head/tail timing, and null-before semantics preserved |
| `0x00482D88` | `0x00482DAE` | 38 B | Source-replaced linked-list empty/clear helpers | Null/endpoint emptiness and null-cleanup forwarding preserved |
| `0x00482DAE` | `0x00482DC2` | 20 B | Source-replaced linked-list previous-pointer setter | Null-node short circuit and `node + node_size` write preserved |
| `0x00482DC2` | `0x00482DD8` | 22 B | Source-replaced linked-list next-pointer setter | Null-node short circuit and `node + node_size + 4` write preserved |
| `0x00482DD8` | `0x00482E4C` | 116 B | Source-replaced LVGL RGB888 color mixer | Three-byte B/G/R aggregate ABI, low-byte opacity, and exact divide-by-255 channel mixing preserved |
| `0x00482E4C` | `0x00482ED4` | 136 B | Source-replaced LVGL packed-alpha color mixer | BGRA lanes, alpha thresholds, destination alpha, and divide-by-256 behavior preserved |
| `0x00482ED4` | `0x00482EF6` | 34 B | Source-replaced LVGL packed-color brightness helper | Exact `(4B + G + 3R) / 8` integer weighting preserved |
| `0x00482EF6` | `0x00482F72` | 124 B | Source-replaced LVGL packed-alpha composition helper | Threshold precedence, composite alpha, source ratio, and source-owned mix dependency preserved |
| `0x00482F72` | `0x00482F74` | 2 B | Retained color-cluster alignment | Official zero padding preserved |
| `0x00482F74` | `0x00482F8A` | 22 B | Source-replaced LVGL theme resolver | Object-display/default-display selection and active-theme lookup preserved |
| `0x00482F8A` | `0x00482FAA` | 32 B | Source-replaced LVGL theme application entry | Null-theme gate, style removal, and recursive application preserved |
| `0x00482FAA` | `0x00482FCE` | 36 B | Source-replaced LVGL primary-color getter | Three-byte B/G/R field and palette-17 fallback preserved |
| `0x00482FCE` | `0x00482FF2` | 36 B | Source-replaced LVGL parent-theme traversal | Parent-first callback ordering preserved |
| `0x00482FF2` | `0x00483028` | 54 B | Source-replaced LVGL inheritable-class traversal | Base-first recursion and object-class restoration preserved |
| `0x00483028` | `0x00483030` | 8 B | Source-replaced bounded output callback | Unsigned output-capacity check and low-byte store preserved |
| `0x00483030` | `0x00483032` | 2 B | Source-replaced no-op output callback | Exact in-place `bx lr` implementation preserved |
| `0x00483032` | `0x00483044` | 18 B | Source-replaced ASCII digit predicate | Low-byte `0x30...0x39` test preserved |
| `0x00483044` | `0x0048306C` | 40 B | Source-replaced unsigned decimal parser | Cursor advance and modulo-2^32 accumulation preserved |
| `0x0048306C` | `0x004830DA` | 110 B | Source-replaced mpaland reverse-output helper | Leading/reverse/trailing output order, width flags, callback ABI, and 32-bit index wrap preserved |
| `0x004830DA` | `0x0048320A` | 304 B | Source-replaced mpaland integer formatter | Precision/zero padding, alternate prefixes, sign policy, and reverse-output dependency preserved |
| `0x0048320A` | `0x0048329C` | 146 B | Source-replaced mpaland 32-bit integer converter | Bases, case, precision-zero suppression, 32-byte digit bound, and source formatter call preserved |
| `0x0048329C` | `0x0048334E` | 178 B | Source-replaced mpaland 64-bit integer converter | Source-owned quotient/remainder core and formatter call preserved |
| `0x0048334E` | `0x00483350` | 2 B | Retained integer-format alignment | Official zero halfword preserved |
| `0x00483350` | `0x00483612` | 706 B | mpaland fixed-point floating converter | Source entry replacement |
| `0x00483612` | `0x0048364C` | 58 B | Fixed-point converter literal tail | Official compatibility bytes preserved |
| `0x0048364C` | `0x00483908` | 700 B | mpaland exponential floating converter | Source entry replacement |
| `0x00483908` | `0x00483960` | 88 B | Exponential converter literal pool | Official compatibility bytes preserved |
| `0x00483960` | `0x00483FCC` | 1,644 B | Source-replaced mpaland-derived formatter core | Complete variadic dispatcher, G2 pointer policy, and recursive `%PV`/`%pV` behavior preserved |
| `0x00483FCC` | `0x00483FD0` | 4 B | Inactive stock fixed-format negative-infinity token tail | Reversed `fni-\0` token formerly read by stock `ftoa`; source `ftoa` no longer references it |
| `0x00483FD0` | `0x00483FEA` | 26 B | Source-replaced public `snprintf` wrapper | Variadic cursor and bounded-output callback ABI preserved |
| `0x00483FEA` | `0x00483FFC` | 18 B | Source-replaced public `vsnprintf` wrapper | Existing `va_list` forwarding preserved |
| `0x00483FFC` | `0x00484014` | 24 B | Retained formatter/async literal gap | Official compatibility bytes preserved |
| `0x00484014` | `0x00484052` | 62 B | Source-replaced LVGL asynchronous-call creator | Allocation, one-shot timer creation, cleanup, and return ABI preserved |
| `0x00484052` | `0x004840AA` | 88 B | Source-replaced LVGL asynchronous-call cancellation | Exact callback/user-data match, remove-all traversal, and delete-before-free ordering preserved |
| `0x004840AA` | `0x004840AC` | 2 B | Retained async alignment halfword | Official compatibility bytes preserved |
| `0x004840AC` | `0x004840C6` | 26 B | Source-replaced LVGL asynchronous timer callback | Saved callback data, timer deletion, free, and invocation ordering preserved |
| `0x004840C6` | `0x0048413C` | 118 B | Retained application bytes | Official compatibility bytes preserved before the generic heap coordinator |
| `0x0048413C` | `0x00484180` | 68 B | Source-replaced generic heap initializer | TLSF/mutex creation, descriptor setup, diagnostics, and fatal behavior preserved |
| `0x00484180` | `0x004841D8` | 88 B | Source-replaced generic heap allocator | Locking, usable-size accounting, peak tracking, and failure behavior preserved |
| `0x004841D8` | `0x00484234` | 92 B | Source-replaced generic aligned allocator | Generic argument order and TLSF alignment/size forwarding preserved |
| `0x00484234` | `0x0048429E` | 106 B | Source-replaced generic heap reallocator | Old/new usable-size accounting and stock size-zero defect preserved |
| `0x0048429E` | `0x004842E6` | 72 B | Source-replaced generic heap free | Size-before-free ordering and saturating accounting preserved |
| `0x004842E6` | `0x0048431E` | 56 B | Retained heap-family initializer | Three reviewed descriptors remain bound to their stock arena bases and sizes |
| `0x0048431E` | `0x0048432A` | 12 B | Source-replaced primary-heap allocation adapter | Descriptor binding and unfiltered forwarding preserved |
| `0x0048432A` | `0x00484338` | 14 B | Source-replaced primary-heap reallocation adapter | Pointer/size forwarding and return behavior preserved |
| `0x00484338` | `0x00484344` | 12 B | Source-replaced primary-heap free adapter | Descriptor binding and unfiltered forwarding preserved |
| `0x00484344` | `0x0048D4E8` | 37,284 B | Retained application bytes | Official compatibility bytes after heap adapters and before bounded string length |
| `0x0048D4E8` | `0x0048D53E` | 86 B | Source-replaced bounded string-length leaf | Complete stock function replaced with overread-free return-equivalent source |
| `0x0048D53E` | `0x00490616` | 12,504 B | Retained application bytes | Official compatibility bytes preserved before the shared formatting append primitive |
| `0x00490616` | `0x00490678` | 98 B | Source-replaced shared formatting append primitive | Complete stock function replaced; seven direct callers preserved |
| `0x00490678` | `0x00490690` | 24 B | Source-replaced shared formatting boolean reader | Complete stock function replaced; three direct callers preserved |
| `0x00490690` | `0x0049087A` | 490 B | Source-replaced repeated-field encoder | Complete stock function replaced; sole regular-field caller preserved |
| `0x0049087A` | `0x00490A46` | 460 B | Source-replaced protobuf-style default-value checker | Complete stock function replaced; recursive and regular-field calls preserved |
| `0x00490A46` | `0x00490AEA` | 164 B | Source-replaced field-value dispatcher | Complete stock function replaced; all downstream adapters linked to source |
| `0x00490AEA` | `0x00490B1E` | 52 B | Source-replaced indirect-field callback helper | Complete stock function replaced; sole regular-field caller preserved |
| `0x00490B1E` | `0x00490BC8` | 170 B | Source-replaced regular field encoder | Complete stock function replaced; both direct callers preserved |
| `0x00490BC8` | `0x00490BF8` | 48 B | Source-replaced default extension-field wrapper | Complete stock function replaced; sole linked-dispatch caller preserved |
| `0x00490BF8` | `0x00490C32` | 58 B | Source-replaced linked extension-field dispatcher | Complete stock function replaced; sole generic-message caller preserved |
| `0x00490C32` | `0x00490C84` | 82 B | Source-replaced generic message encoder | Complete stock function replaced; 125 direct branch sites preserved |
| `0x00490C84` | `0x00490CE0` | 92 B | Source-replaced unsigned LEB128 encoder | Complete stock function replaced; sole direct caller moved to source |
| `0x00490CE0` | `0x00490D08` | 40 B | Source-replaced unsigned 64-bit prefix writer | Complete stock function replaced; nine direct callers preserved |
| `0x00490D08` | `0x00490D36` | 46 B | Source-replaced signed 64-bit zigzag writer | Complete stock function replaced; sole direct caller preserved |
| `0x00490D36` | `0x00490D40` | 10 B | Source-replaced fixed four-byte append wrapper | Complete stock function replaced; sole direct caller preserved |
| `0x00490D40` | `0x00490D4A` | 10 B | Source-replaced fixed eight-byte append wrapper | Complete stock function replaced; sole direct caller preserved |
| `0x00490D4A` | `0x00490D66` | 28 B | Source-replaced formatting field-key encoder | Complete stock function replaced; two callers preserved |
| `0x00490D66` | `0x00490DB6` | 80 B | Source-replaced descriptor-to-field-key adapter | Complete stock function replaced; two callers preserved |
| `0x00490DB6` | `0x00490DDC` | 38 B | Source-replaced length-prefixed formatting buffer writer | Complete stock function replaced; four callers preserved |
| `0x00490DDC` | `0x00490E90` | 180 B | Source-replaced two-pass formatting submessage writer | Complete stock function replaced; sole field-adapter caller preserved |
| `0x00490E90` | `0x00490EAE` | 30 B | Source-replaced boolean descriptor adapter | Complete stock function replaced; sole direct caller preserved |
| `0x00490EAE` | `0x00490F72` | 196 B | Source-replaced integer descriptor adapter | Complete stock function replaced; three callers preserved |
| `0x00490F72` | `0x00490FA2` | 48 B | Source-replaced fixed-width descriptor adapter | Complete stock function replaced; two callers preserved |
| `0x00490FA2` | `0x00490FE4` | 66 B | Source-replaced bytes descriptor adapter | Complete stock function replaced; sole dispatcher caller preserved |
| `0x00490FE4` | `0x0049104C` | 104 B | Source-replaced string descriptor adapter | Complete stock function replaced; sole dispatcher caller preserved |
| `0x0049104C` | `0x004910A4` | 88 B | Source-replaced submessage-field descriptor adapter | Complete stock function replaced; sole dispatcher caller preserved |
| `0x004910E8` | `0x004910F4` | 12 B | Source-replaced formatting span adapter | Exact source assembly; one dispatcher caller preserved |
| `0x004910F4` | `0x00491102` | 14 B | Source-replaced millisecond delay wrapper | Exact source assembly; 53 direct callers preserved |
| `0x00491102` | `0x0049110A` | 8 B | Source-replaced microsecond delay passthrough | Exact source assembly; 66 direct callers preserved |
| `0x0049110A` | `0x004C23DE` | 201,428 B | Retained application before the MSPI interrupt-clear leaf | Official compatibility bytes preserved |
| `0x004C23DE` | `0x004C240E` | 48 B | Source-replaced AmbiqSuite 5.1.0 `am_hal_mspi_interrupt_clear` | Generated redirect over the authenticated complete stock body |
| `0x004C240E` | `0x004CA6F8` | 33,514 B | Retained application before the littlefs utility quartet | Official compatibility bytes preserved |
| `0x004CA6F8` | `0x004CA700` | 8 B | Source-replaced littlefs v2.10.1 `lfs_max` | Complete upstream scalar leaf |
| `0x004CA700` | `0x004CA708` | 8 B | Source-replaced littlefs v2.10.1 `lfs_min` | Complete upstream scalar leaf |
| `0x004CA708` | `0x004CA714` | 12 B | Source-replaced littlefs v2.10.1 `lfs_aligndown` | Complete upstream unsigned alignment leaf |
| `0x004CA714` | `0x004CA720` | 12 B | Source-replaced littlefs v2.10.1 `lfs_alignup` | Complete upstream leaf; source-linked to `lfs_aligndown` |
| `0x004CA720` | `0x004CA77A` | 90 B | Source-replaced littlefs v2.10.1 `lfs_npw2` | Exact `LFS_NO_INTRINSICS` fallback body |
| `0x004CA77A` | `0x004CA78A` | 16 B | Source-replaced littlefs v2.10.1 `lfs_ctz` | Exact fallback body; source-linked to `lfs_npw2` |
| `0x004CA78A` | `0x004CA7B2` | 40 B | Source-replaced littlefs v2.10.1 `lfs_popc` | Exact `LFS_NO_INTRINSICS` fallback body |
| `0x004CA7B2` | `0x004CA7B6` | 4 B | Source-replaced littlefs v2.10.1 `lfs_scmp` | Exact upstream unsigned-wrap comparator; Apollo-main entry only |
| `0x004CA7B6` | `0x004CA7D8` | 34 B | Source-replaced littlefs v2.10.1 `lfs_fromle32` | Complete upstream endian leaf |
| `0x004CA7D8` | `0x004CA7E0` | 8 B | Source-replaced littlefs v2.10.1 `lfs_tole32` | Complete upstream endian leaf |
| `0x004CA7E0` | `0x004CA802` | 34 B | Source-replaced littlefs v2.10.1 `lfs_frombe32` | Complete upstream endian leaf |
| `0x004CA802` | `0x004CA80A` | 8 B | Source-replaced littlefs v2.10.1 `lfs_tobe32` | Complete upstream endian leaf |
| `0x004CA80A` | `0x004CB082` | 2,168 B | Retained littlefs core between endian and metadata-list helpers | Official compatibility bytes preserved |
| `0x004CB082` | `0x004CB0A0` | 30 B | Source-replaced littlefs v2.10.1 `lfs_mlist_isopen` | Exact upstream metadata-list membership predicate |
| `0x004CB0A0` | `0x004CB0BC` | 28 B | Source-replaced littlefs v2.10.1 `lfs_mlist_remove` | Exact upstream metadata-list removal helper |
| `0x004CB0BC` | `0x004CB0C4` | 8 B | Source-replaced littlefs v2.10.1 `lfs_mlist_append` | Exact upstream metadata-list append helper |
| `0x004CB0C4` | `0x004CB0CA` | 6 B | Source-replaced littlefs v2.10.1 `lfs_fs_disk_version` | Exact upstream disk-version getter |
| `0x004CB0CA` | `0x004CB0D6` | 12 B | Source-replaced littlefs v2.10.1 `lfs_fs_disk_version_major` | Exact complete stock span redirected to source |
| `0x004CB0D6` | `0x004CB0E0` | 10 B | Source-replaced littlefs v2.10.1 `lfs_fs_disk_version_minor` | Exact complete stock span redirected to source |
| `0x004CB0E0` | `0x004CB0E6` | 6 B | Source-replaced littlefs v2.10.1 `lfs_alloc_ckpoint` | Exact upstream allocator-state assignment with authenticated `lfs_t` offsets |
| `0x004CB0E6` | `0x004CB0F6` | 16 B | Source-replaced littlefs v2.10.1 `lfs_alloc_drop` | Exact upstream allocator-state restore with authenticated `lfs_t` offsets |
| `0x004CB0F6` | `0x004CB12E` | 56 B | Source-replaced littlefs v2.10.1 `lfs_alloc_lookahead` | Exact complete callback span redirected to source |
| `0x004CB12E` | `0x004CE45C` | 13,102 B | Retained littlefs core between allocator lookahead and private file-position getter | Official compatibility bytes preserved |
| `0x004CE45C` | `0x004CE460` | 4 B | Source-replaced littlefs v2.10.1 `lfs_file_tell_` | Exact upstream private file-position getter |
| `0x004CE460` | `0x004CE472` | 18 B | Source-replaced littlefs v2.10.1 `lfs_file_rewind_` | Generated full-span redirect to bounded upstream-compatible source |
| `0x004CE472` | `0x004CE48A` | 24 B | Source-replaced littlefs v2.10.1 `lfs_file_size_` | Generated full-span redirect to bounded upstream-compatible source |
| `0x004CE48A` | `0x004CFD18` | 6,286 B | Retained littlefs core before TLSF | Official compatibility bytes preserved |
| `0x004CFD18` | `0x004D0580` | 2,152 B | Retained TLSF implementation prefix and internal helpers | Official allocator bytes preserved before the first source-replaced public entry |
| `0x004D0580` | `0x004D05E4` | 100 B | Source-replaced TLSF pool walker | Complete stock function replaced; callback and pool-walk ABI preserved |
| `0x004D05E4` | `0x004D05FA` | 22 B | Source-replaced TLSF block-size query | Complete stock function replaced; null and usable-size behavior preserved |
| `0x004D05FA` | `0x004D0604` | 10 B | Source-replaced TLSF pool-overhead query | Complete stock function replaced; recovered 8-byte pool overhead preserved |
| `0x004D0604` | `0x004D0608` | 4 B | TLSF literal island | Official compatibility word retained |
| `0x004D0608` | `0x004D06AC` | 164 B | Retained TLSF pool-add implementation | Official internal/public implementation retained |
| `0x004D06AC` | `0x004D06B4` | 8 B | TLSF literal island | Official compatibility words retained |
| `0x004D06B4` | `0x004D06D6` | 34 B | Retained TLSF control-creation implementation | Official implementation retained |
| `0x004D06D6` | `0x004D06EC` | 22 B | TLSF literal island | Official compatibility data retained before create-with-pool |
| `0x004D06EC` | `0x004D0716` | 42 B | Source-replaced TLSF create-with-pool entry | Complete stock function replaced; 32-bit control and pool layout preserved |
| `0x004D0716` | `0x004D0722` | 12 B | Source-replaced TLSF pool accessor | Complete stock function replaced; `control + 0xC74` ABI preserved |
| `0x004D0722` | `0x004D0744` | 34 B | Source-replaced TLSF allocator | Complete stock function replaced; request adjustment and exhaustion behavior preserved |
| `0x004D0744` | `0x004D0802` | 190 B | Source-replaced TLSF aligned allocator | Complete stock function replaced; alignment-gap and split behavior preserved |
| `0x004D0802` | `0x004D0808` | 6 B | TLSF literal island | Official compatibility data retained before free |
| `0x004D0808` | `0x004D0852` | 74 B | Source-replaced TLSF free | Complete stock function replaced; null handling and bidirectional coalescing preserved |
| `0x004D0852` | `0x004D0868` | 22 B | TLSF literal island | Official compatibility data retained before realloc |
| `0x004D0868` | `0x004D094A` | 226 B | Source-replaced TLSF reallocator | Complete stock function replaced; null, zero, grow, shrink, copy, and preservation behavior retained |
| `0x004D094A` | `0x004D09B4` | 106 B | TLSF terminal literal island | Official diagnostics, source pointers, and constants retained |
| `0x004D09B4` | `0x004E0C0C` | 66,136 B | Retained application after TLSF | Official compatibility bytes preserved before EvenHub decompression |
| `0x004E0C0C` | `0x004E0CA0` | 148 B | Source-replaced EvenHub decompression adapters and byte-run decoder | Three complete stock functions replaced |
| `0x004E0CA0` | `0x004E0CCE` | 46 B | Source-replaced EvenHub lifecycle state accessors | Five complete stock functions replaced |
| `0x004E0CCE` | `0x004E0D3A` | 108 B | Source-replaced EvenHub container lookup | Complete stock function replaced |
| `0x004E0D3A` | `0x004E1192` | 1,112 B | Source-replaced EvenHub page-event callback | Complete stock callback replaced |
| `0x004E1192` | `0x004E1406` | 628 B | Source-replaced EvenHub common-data callback | Complete stock callback replaced; registered pointer preserved |
| `0x004E1406` | `0x004E1442` | 60 B | Source-replaced EvenHub IMU enable policy | Complete stock function replaced |
| `0x004E1490` | `0x004E1956` | 1,222 B | Source-replaced EvenHub registry UI-event handler | Complete stock handler replaced; registered pointer preserved |
| `0x00530084` | `0x005300E2` | 94 B | Source-replaced generic ring-write primitive | Complete stock function replaced; copy and null-source publish ABIs retained |
| `0x005300E2` | `0x0053013C` | 90 B | Source-replaced generic ring-read primitive | Complete stock function replaced; copy and null-destination discard ABIs retained |
| `0x005415C2` | `0x005415D8` | 22 B | Source-replaced installed dynamic display handler | Complete stock function replaced; length and sink linked directly |
| `0x0054F338` | `0x0054F356` | 30 B | Source-replaced LZ4 safe block-decoder wrapper | Complete stock function replaced |
| `0x0055E7FA` | `0x0055E898` | 158 B | Source-replaced asynchronous four-channel display sink | Complete stock function replaced; channel-table ABI retained |
| `0x0058DD30` | `0x0058DD5C` | 44 B | Source-replaced IRQ special-transfer finish helper | Complete stock function replaced; instance MMIO teardown retained |
| `0x0058DD5C` | `0x0058DD8A` | 46 B | Source-replaced IRQ bit-12 cleanup helper | Complete stock function replaced; FIFO-position reset retained |
| `0x0058DD8A` | `0x0058DDD6` | 76 B | Source-replaced IRQ completion-result helper | Complete stock function replaced; prioritized error mapping retained |
| `0x0058DEF2` | `0x0058DF5C` | 106 B | Source-replaced lower-level display-operation begin helper | Complete stock function replaced; exact prior PRIMASK restored |
| `0x0058DF5C` | `0x0058DFB2` | 86 B | Source-replaced event-side display-operation begin helper | Complete stock function replaced; exact prior PRIMASK restored |
| `0x0058DFB2` | `0x0058DFEE` | 60 B | Source-replaced event-side display-operation abort/reset helper | Complete stock function replaced; exact prior PRIMASK restored |
| `0x0058DFEE` | `0x0058E09E` | 176 B | Source-replaced IRQ bit-6 cleanup/restore helper | Complete stock function replaced; source bit-12/discard calls linked |
| `0x0058E2D8` | `0x0058E31E` | 70 B | Source-replaced direct display FIFO reader | Complete stock function replaced; empty/data-error MMIO ABI retained |
| `0x0058E31E` | `0x0058E352` | 52 B | Source-replaced direct display FIFO writer | Complete stock function replaced; instance MMIO ABI retained |
| `0x0058E352` | `0x0058E360` | 14 B | Source-replaced display FIFO discard wrapper | Complete stock function replaced; direct reader linked to source |
| `0x0058E360` | `0x0058E3A0` | 64 B | Source-replaced display FIFO-to-ring fill helper | Complete stock function replaced; reader and ring writer linked to source |
| `0x0058E3A0` | `0x0058E3F0` | 80 B | Source-replaced display ring-drain helper | Complete stock function replaced; ring and MMIO ABIs retained |
| `0x0058E3F8` | `0x0058E440` | 72 B | Source-replaced display-operation submit dispatcher | Complete stock function replaced; all four backends linked to source |
| `0x0058E454` | `0x0058E49E` | 74 B | Source-replaced display submit operation-zero backend | Complete stock function replaced; start/service linked to source |
| `0x0058E49E` | `0x0058E4E8` | 74 B | Source-replaced display submit operation-one backend | Complete stock function replaced; operation three linked to source |
| `0x0058E4E8` | `0x0058E50A` | 34 B | Source-replaced shared operation-start/operation-two helper | Complete stock function replaced; begin/service linked to source |
| `0x0058E50A` | `0x0058E534` | 42 B | Source-replaced display submit operation-three backend | Complete stock function replaced; event begin/service linked to source |
| `0x0058E534` | `0x0058E618` | 228 B | Source-replaced display-operation service | Complete stock function replaced; three caller ABIs retained |
| `0x0058E618` | `0x0058E6DE` | 198 B | Source-replaced event-side display-operation service | Complete stock function replaced; three caller ABIs retained |
| `0x0058E860` | `0x0058E910` | 176 B | Source-replaced IRQ-side display transport owner | Complete stock function replaced; event/operation services linked to source |
| `0x0058E910` | `0x005FA058` | 440,136 B | Retained application before the FreeRTOS NTZ port tranche | Official compatibility bytes preserved |
| `0x005FA058` | `0x005FA07E` | 38 B | FreeRTOS V10.5.1 `vRestoreContextOfFirstTask` | Exact source-assembled in-place copy |
| `0x005FA07E` | `0x005FA08C` | 14 B | FreeRTOS V10.5.1 `vRaisePrivilege` | Exact source-assembled in-place copy |
| `0x005FA08C` | `0x005FA0A4` | 24 B | FreeRTOS V10.5.1 `vStartFirstTask` | Exact source-assembled in-place copy; VTOR literal and SVC 2 preserved |
| `0x005FA0A4` | `0x005FA0BA` | 22 B | FreeRTOS V10.5.1 `ulSetInterruptMask` | Exact source-assembled in-place copy; public address and DSB/ISB sequence preserved |
| `0x005FA0BA` | `0x005FA0C8` | 14 B | FreeRTOS V10.5.1 `vClearInterruptMask` | Exact source-assembled in-place copy; public address and DSB/ISB sequence preserved |
| `0x005FA0C8` | `0x005FA120` | 88 B | FreeRTOS V10.5.1 `PendSV_Handler` | Exact source-assembled in-place copy; vector `0x005FA0C9` preserved |
| `0x005FA120` | `0x005FA132` | 18 B | FreeRTOS V10.5.1 `SVC_Handler` | Exact source-assembled in-place copy; vector `0x005FA121` preserved |
| `0x005FA132` | `0x006BECB0` | 805,758 B | Retained application after the FreeRTOS NTZ port tranche | Official compatibility bytes preserved; includes authenticated literal pool `[0x005FA132,0x005FA13C)` |
| `0x006BECB0` | `0x006BEED0` | 544 B | Retired stock peripheral-power descriptor table | All 34 records are reviewed and separately mapped; the live source replacement uses a byte-identical source-owned table in the overlay |
| `0x00794310` | `0x00794316` | 6 B | Source-replaced ITCM delay-cycle load literal | Exact source assembly; scatter-loaded to runtime `0x00000040` |
| `0x00794324` | `0x007AEF74` | 109,648 B | Multi-module Apollo source overlay before fallback bitops | Compiled source |
| `0x007AEF74` | `0x007AEFBC` | 72 B | Apollo-main littlefs v2.10.1 `lfs_npw2` | Mini-linked `LFS_NO_INTRINSICS` fallback body |
| `0x007AEFBC` | `0x007AEFCC` | 16 B | Apollo-main littlefs v2.10.1 `lfs_ctz` | Mini-linked fallback body; internal call to `lfs_npw2` resolved |
| `0x007AEFCC` | `0x007AEFF6` | 42 B | Apollo-main littlefs v2.10.1 `lfs_popc` | Mini-linked fallback body |
| `0x007AEFF6` | `0x007B0128` | 4,402 B | Remaining primary Apollo source text/data | Compiled source |
| `0x007B0128` | `0x007B0158` | 48 B | AmbiqSuite 5.1.0 `am_hal_mspi_interrupt_clear` | Relocation-free isolated source leaf |
| `0x007B0158` | `0x007B016E` | 22 B | FreeRTOS V10.5.1 `ulSetInterruptMask` | Relocation-free isolated source leaf |
| `0x007B016E` | `0x007B017C` | 14 B | FreeRTOS V10.5.1 `vClearInterruptMask` | Relocation-free isolated source leaf |
| `0x007B017C` | `0x007B01A8` | 44 B | Apollo-main littlefs v2.10.1 `lfs_mlist_isopen` | Relocation-free isolated source leaf |
| `0x007B01A8` | `0x007B01AA` | 2 B | Apollo-main littlefs v2.10.1 `lfs_fromle32` | Relocation-free identity source leaf |
| `0x007B01AA` | `0x007B01AC` | 2 B | Isolated-leaf alignment | Generated zero bytes |
| `0x007B01AC` | `0x007B01AE` | 2 B | Apollo-main littlefs v2.10.1 `lfs_tole32` | Relocation-free identity source leaf |
| `0x007B01AE` | `0x007B01B0` | 2 B | Isolated-leaf alignment | Generated zero bytes |
| `0x007B01B0` | `0x007B01B4` | 4 B | Apollo-main littlefs v2.10.1 `lfs_frombe32` | Relocation-free byte-swap source leaf |
| `0x007B01B4` | `0x007B01B8` | 4 B | Apollo-main littlefs v2.10.1 `lfs_tobe32` | Relocation-free byte-swap source leaf |
| `0x007B01B8` | `0x007B01C2` | 10 B | Apollo-main littlefs v2.10.1 `lfs_fs_disk_version_major` | Relocated source leaf; direct call to source disk-version provider |
| `0x007B01C2` | `0x007B01C4` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B01C4` | `0x007B01CE` | 10 B | Apollo-main littlefs v2.10.1 `lfs_fs_disk_version_minor` | Relocated source leaf; direct call to source disk-version provider |
| `0x007B01CE` | `0x007B01D0` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B01D0` | `0x007B0202` | 50 B | Apollo-main littlefs v2.10.1 `lfs_alloc_lookahead` | Relocation-free source leaf with recovered `lfs_t` offsets |
| `0x007B0202` | `0x007B0204` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B0204` | `0x007B0280` | 124 B | CMSIS-FreeRTOS v10.5.1 `osMessageQueueNew` | Relocated source leaf closed over three source-owned FreeRTOS dependencies |
| `0x007B0280` | `0x007B02A6` | 38 B | FreeRTOS V10.5.1 `pcTaskGetName` | Relocated source leaf closed over source-owned interrupt-mask assertion dependency |
| `0x007B02A6` | `0x007B02A8` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B02A8` | `0x007B031C` | 116 B | CMSIS-FreeRTOS v10.5.1 `osMutexNew` | Relocated source leaf closed over source-owned scheduler-state and static/dynamic mutex creators |
| `0x007B031C` | `0x007B035E` | 66 B | FreeRTOS V10.5.1 `prvHeapInit` | Relocated source leaf using the recovered G2 heap layout |
| `0x007B035E` | `0x007B0360` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B0360` | `0x007B03D6` | 118 B | FreeRTOS V10.5.1 `prvInsertBlockIntoFreeList` | Relocated source leaf preserving ordered insertion and coalescing |
| `0x007B03D6` | `0x007B03D8` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B03D8` | `0x007B050C` | 308 B | FreeRTOS V10.5.1 `pvPortMalloc` | Relocated source leaf closed over source heap and interrupt masking |
| `0x007B050C` | `0x007B057E` | 114 B | FreeRTOS V10.5.1 `vPortFree` | Relocated source leaf closed over source insertion and interrupt masking |
| `0x007B057E` | `0x007B0580` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B0580` | `0x007B05A6` | 38 B | FreeRTOS V10.5.1 `vQueueDelete` | Relocated source leaf closed over source heap free and interrupt masking |
| `0x007B05A6` | `0x007B05A8` | 2 B | Relocated-leaf alignment | Generated zero bytes |
| `0x007B05A8` | `0x007B065A` | 178 B | CMSIS-FreeRTOS v10.5.1 `osSemaphoreNew` | Relocated source leaf closed over source scheduler, queue, semaphore, and delete functions |
| `0x007B065A` | `0x007B065C` | 2 B | EasyLogger logger-provider alignment | Generated zero bytes |
| `0x007B065C` | `0x007B0666` | 10 B | Apollo-main EasyLogger logger-object provider | Source compiled |
| `0x007B0666` | `0x007B0668` | 2 B | EasyLogger assertion-provider alignment | Generated zero bytes |
| `0x007B0668` | `0x007B0710` | 168 B | Apollo-main EasyLogger assertion-policy provider | Source compiled; official strings/output/wait retained |
| `0x007B0710` | `0x007B0736` | 38 B | EasyLogger `get_fmt_enabled` | Relocated source leaf |
| `0x007B0736` | `0x007B0738` | 2 B | EasyLogger unsigned-predicate alignment | Generated zero bytes |
| `0x007B0738` | `0x007B074E` | 22 B | EasyLogger unsigned-argument predicate | Relocated source leaf |
| `0x007B074E` | `0x007B0750` | 2 B | EasyLogger pointer-predicate alignment | Generated zero bytes |
| `0x007B0750` | `0x007B0766` | 22 B | EasyLogger pointer-argument predicate | Relocated source leaf |
| `0x007B0766` | `0x007B0768` | 2 B | EasyLogger bounded-copy alignment | Generated zero bytes |
| `0x007B0768` | `0x007B07EA` | 130 B | EasyLogger `elog_strcpy` | Relocated source leaf |
| `0x007B07EA` | `0x007B07EC` | 2 B | FreeRTOS tick-provider alignment | Generated zero bytes |
| `0x007B07EC` | `0x007B07F8` | 12 B | FreeRTOS V10.5.1 `xTickCount` provider | Relocation-free source leaf binding RAM `0x20074A34` |
| `0x007B07F8` | `0x007B07FC` | 4 B | FreeRTOS V10.5.1 `xTaskGetTickCount` | Source leaf; one jump relocation to the source provider |
| `0x007B07FC` | `0x007B0800` | 4 B | FreeRTOS V10.5.1 `xTaskGetTickCountFromISR` | Source leaf; one jump relocation to the source provider |
| `0x007B0800` | `0x007B080E` | 14 B | FreeRTOS V10.5.1 `vTaskMissedYield` | Relocation-free source leaf binding `xYieldPending` at `0x20074A44` |
| `0x007B080E` | `0x007B0810` | 2 B | Event-item reset alignment | Generated zero bytes |
| `0x007B0810` | `0x007B082A` | 26 B | FreeRTOS V10.5.1 `uxTaskResetEventItemValue` | Relocation-free source leaf binding `pxCurrentTCB` at `0x20074A20` |
| `0x007B082A` | `0x007B082C` | 2 B | Mutex-held increment alignment | Generated zero bytes |
| `0x007B082C` | `0x007B0844` | 24 B | FreeRTOS V10.5.1 `pvTaskIncrementMutexHeldCount` | Relocation-free source leaf binding `pxCurrentTCB` at `0x20074A20` |
| `0x007B0844` | `0x007B0854` | 16 B | FreeRTOS V10.5.1 `vTaskSuspendAll` | Relocation-free source leaf binding `uxSchedulerSuspended` at `0x20074A58` |
| `0x007B0854` | `0x007B0866` | 18 B | FreeRTOS V10.5.1 `vTaskInternalSetTimeOutState` | Relocation-free source leaf binding overflow/tick words at `0x20074A48` and `0x20074A34` |
| `0x007FE000` | `0x007FE010` | 16 B | Persistent update-flag record | Confirmed; bootloader-owned and protected |
| `0x00800000` | — | — | End of 4 MiB internal MRAM | Device-family boundary |

The official main payload has a 32-byte staging preamble. Only bytes from
payload offset `0x20` are installed at `0x00438000`. The source profile
regenerates that preamble, partitions the official application into
non-overlapping opaque and source-replacement ranges, then appends the overlay.
At that milestone, the 3,639,398 installed bytes ended at `0x007B0866`, leaving
259,994 bytes before the conservative source-build ceiling at `0x007F0000` and 317,338 bytes
before the protected update flag at `0x007FE000`.

The five prior NTZ source-owned spans total 182 bytes and are installed
through the fixed-address `in_place_leaves` contract, not appended to the
overlay ABI. Their 5,487-byte source adapter has SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
Four explicit PC-relative relocations preserve the literal words
at `0x005FA134` (`pxCurrentTCB=0x20074A20`) and `0x005FA138`
(`SCB_VTOR=0xE000ED08`); the only branch relocations preserve
`vTaskSwitchContext` at `0x004551B4` and `vPortSVCHandler_C` at
`0x00442134`. That historical tranche left its overlay, provider, and package
bytes unchanged. The subsequent disk-version-parts tranche appends the two
source leaves and redirects their exact stock spans in both images. The
allocator-lookahead tranche appends one additional source leaf and redirects
its exact 56-byte stock span in each image. The earlier CMSIS tranche appends
the Apollo-main `osMessageQueueNew` leaf and redirects its exact 140-byte
stock span. The task-name tranche then appends `pcTaskGetName`; the mutex
tranche appends `osMutexNew`. The prior atomic heap/semaphore tranche
appends four `heap_4` leaves, `vQueueDelete`, and `osSemaphoreNew`, with eight
alignment bytes, while redirecting 766 complete stock bytes. The subsequent
tick manifest had 828 placed, two unresolved, and five container-only regions;
its 596,957-byte flash plan had SHA-256
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`.
The preceding missed-yield manifest had 831 placed, two unresolved, and five
container-only regions. The event-item/mutex-held manifest had 838 placed,
two unresolved, and five container-only regions. The current suspend/timeout
manifest has 844 placed, two unresolved, and five container-only regions; its
608,608-byte flash plan has SHA-256
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`.

The broad CMSIS-FreeRTOS constructor compile-closure proof remains
candidate-only for unrelated services.
Candidate shims at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
provide `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}` and
let the authenticated, unmodified CMSIS-FreeRTOS v10.5.1 `cmsis_os2.c`
compile for Cortex-M55 with `-Oz -Werror`. Garbage collection retains 370
text bytes (`IRQ_Context` 46, `osMessageQueueNew` 88, `osMutexNew` 98,
`osSemaphoreNew` 138), zero read-only or writable data, and four 8-byte EHABI
`.ARM.exidx` sections; 6/6 isolated tests pass in 0.231 seconds. The bounded
production `osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew` adapters above are instead
admitted from their authenticated stock ranges, ABI/configuration, IRQ
policies, and direct source-owned dependencies. The semaphore cleanup path
closes through source-owned `vQueueDelete` and the selected bounded `heap_4`
adapter. These bounded leaves do not resolve the broader RTE/device-header,
`SystemCoreClock`, MVE, `INCLUDE_*`, assert/NVIC/libc, or candidate
`StaticTask_t` questions.

The UI-module registry source preserves the 43-row flash table at
`0x006A44B0...0x006A475F`, its runtime copy at `0x20066230`, and its count at
`0x200744D4`. The GPIO handler source preserves two existing Apollo SRAM ABI ranges:
`0x20068228...0x20068927` contains 14 × 32 handler pointers and
`0x20068928...0x20069027` contains the corresponding callback arguments. The
EvenHub lifecycle source preserves the reviewed words at `0x200745AC`,
`0x200745B4`, `0x200745B8`, `0x200745C4`, and `0x200745C8`, plus the byte at
`0x20074FC4`. These are fixed firmware-owned state, not writable sections
appended to the overlay. The source page-event callback additionally preserves
the word at `0x200745C0`, the byte at `0x20074FC3`, and manager byte `+0x34`.
The common-data callback remains registered through the stock Thumb pointer at
`0x006A4524`; the source registry UI-event handler remains registered through
`0x006A4528` and publishes its root at `0x20000B3C`. Their downstream UI,
allocation, event-validation, queue, peer-state, status, display-stop,
IMU-report, and diagnostic entries remain explicit version-pinned source/blob
ABI boundaries. The source display initializer now calls its two source setup
helpers and registers the source thread entry directly through the retained
RTOS ABI at `0x004490E3`; display setup binds the source callback wrapper,
which reads the current downstream handler from `0x200742F0`. The stock Thumb
words `0x004437E1` at `0x004448F0` and `0x00444685` at `0x004448BC` remain
preserved but inactive. The source-owned setter installs a handler whose
recovered contract is `sink(1, buffer, length(buffer))`. The shared length
primitive at `0x0044A43C` is now source-owned and linked directly by the
handler; sink entry `0x0055E7FA` is source-owned as well. The sink preserves
the four 28-byte channel records at `0x20000D2C` and calls the source submit
dispatcher at `0x0058E3F8` directly. That dispatcher preserves its masked
handle signature and routes all four operation backends directly to source.
Operation zero at `0x0058E454` and operation one at `0x0058E49E` implement
their bounded polling policies. The shared start helper at `0x0058E4E8` also
implements dispatcher operation two. Operation three at `0x0058E50A` clears
the optional completion word, invokes source event-side begin `0x0058DF5C`,
and services a successful begin through source event service `0x0058E618`;
operation one calls source operation three and the same source event service
directly. IRQ-side transport owner `0x0058E860` also calls the source event
and operation services directly. Its normal path services status masks
`0x50/0x20/0x01`; its special path publishes FIFO progress, handles status
bits 6, 11, and 12 through four source helpers, dispatches the optional
completion callback, and clears handle byte `+0x11B`. Those helpers own the
instance MMIO teardown at `0x0058DD30`, bit-12 cleanup at `0x0058DD5C`,
prioritized error result at `0x0058DD8A`, and bit-6 cleanup/restore path at
`0x0058DFEE`. That path calls source event abort `0x0058DFB2`, which clears
the receive state only when busy byte `+0x11A` equals one. The
lower-level operation-zero/two begin helper at `0x0058DEF2` is source-owned and receives
both the handle and descriptor. Under one PRIMASK critical section it rejects
an already-busy handle, otherwise publishes the busy byte at `+0x119`, copies
descriptor words `+0x00...+0x18` into handle state `+0xA0...+0xB8`, copies
descriptor byte `+0x34` to handle byte `+0xD4`, and clears handle word `+0xD8`
and byte `+0xDE`. Service `0x0058E534` is source-owned as well. It advances
direct or ring-buffer transport, publishes the transferred byte count through
descriptor pointer `+8`, clears busy state on completion or ring-write
failure, and invokes the descriptor callback from handle state `+0xB0/+0xB4`.
Event-side begin `0x0058DF5C` uses busy byte `+0x11A`, copies descriptor words
`+0x00...+0x18` into handle state `+0x64...+0x7C`, publishes operation byte
`+0x34` at handle `+0x98`, and clears progress word `+0x9C` under one PRIMASK
critical section. Event service `0x0058E618` fills the receive ring when
enabled, then drains the ring or reads the FIFO directly into the published
destination. It updates the optional progress pointer at handle `+0x6C` and
invokes result-one failure or result-zero completion callbacks from
`+0x74/+0x78`.
Direct FIFO transport is source-owned in both directions. Reader
`0x0058E2D8` selects the FIFO instance from handle word `+0x28`, reads while
MMIO status bit 4 says data is available, reports the number accepted, and
preserves the stock `0x00000F00` data-error policy. Writer `0x0058E31E`
selects the same instance, writes while status bit 5 is clear, and reports the
number accepted. The discard wrapper at `0x0058E352` invokes the source reader
as `(handle, NULL, 32, NULL)`. FIFO-to-ring fill `0x0058E360` calls the source
reader and source ring writer under one PRIMASK critical section. Ring drain
`0x0058E3A0` is source-owned too and calls the source ring reader and direct
writer under one PRIMASK critical section. Ring read `0x005300E2` and ring
write `0x00530084` are source-owned. Duration delay `0x004807A0` is
source-assembled exactly in place, preserving all 116 stock callers and the
call to the source-generated Ambiq three-cycle loop at ITCM `0x00000040`.
Reset enters startup at `0x005E4294`; its scatter loader at `0x005E42B4`
walks the table beginning at `0x0075D3C8`. The second record at `0x0075D3E0`
resolves handler `0x0043A11E`, the 22-byte compressed stream at `0x0079430E`,
and destination `0x00000040`. That stream's first token emits a 14-byte
literal, so load-image bytes `0x00794310...0x00794315` map exactly to runtime
`0x00000040...0x00000045`. The builder validates that relationship before
copying the six source-assembled bytes. The scatter loader/table, two-byte
stream header, and 14-byte tail encoding neighboring ITCM functions remain
stock-owned compatibility ABIs. The adjacent wrapper at `0x004910F4`
multiplies milliseconds by 1,000 before calling the exact in-place delay; the
wrapper at `0x00491102` passes microseconds unchanged. Both wrappers are exact
source copies. The sink's argument of 10 therefore means 10 microseconds, not
10 milliseconds. Immediately before them, format type-11 adapter
`0x004910E8` is an exact source copy that reads descriptor length `+0x12` and
data pointer `+0x1C`, then forwards them to source-owned shared writer
`0x00490DB6`. That writer emits an unsigned length prefix through retained
entry `0x00490CE0`; only a successful prefix is followed by the original span
through retained append entry `0x00490616`. The initializer, callback,
setup helpers,
handler, and thread
preserve the reviewed display SRAM ABI at `0x20000654`, `0x20073B48`,
`0x20073B60`, `0x20073FCC`, `0x200742F0`,
`0x200744CC...0x200744E8`, `0x20074F2C`, `0x200E99B4`, and
`0x2034DC30`.

The source setter at `0x00472C7C` is the only recovered writer to
`0x200742F0`. Its sole stock caller at `0x00541726` installs Thumb handler
`0x005415C3`. The source-replaced generic formatting dispatcher at
`0x004733EE` gates on that word, passes its AAPCS variadic cursor to retained
formatter core `0x00473036`, reloads the word, and invokes the selected
handler with context `0x2006B930`. All 731 stock direct callers remain valid.
The adjacent unsigned 64-bit divide-by-ten runtime at `0x00472C84`, the core's
decimal/hex sizing and emission, signed width/precision parsing, nullable
string length, padding dependencies, and bounded float conversion through
`0x00473035` are source-replaced too. The 952-byte conversion parser/core at
`0x00473036` is source-replaced and links its non-floating work directly to
the source helper implementations; its hard-float call reaches the source
converter through the preserved stock entry ABI.

After the dispatcher's 90-byte literal/data pool, the LVGL millisecond tick
increment, dynamic getter, and wrap-safe elapsed helper at
`0x00473474...0x004734BB` are source-replaced. They preserve the shared
`0x2006F600` state layout, the optional callback at offset eight, and unsigned
wraparound subtraction. The adjacent four-byte SRAM literal remains official
data. The following 12-byte LVGL zero-fill wrapper at `0x004734C0` is
source-replaced too and performs its bounded byte clear without an opaque
memory-runtime call. The adjacent 124-byte global-state initializer at
`0x004734CC` is source-owned as well: it clears the 492-byte state, initializes
the two embedded lists, writes the recovered defaults, and preserves the
reviewed LVGL list/finalize and fatal-diagnostic ABIs.
The complete 222-byte `lv_init` sequence at `0x00473548` is source-owned too.
It preserves the initialized flag at `0x2006F548`, calls the source global
initializer directly, makes all 17 still-opaque subsystem calls explicit,
retains the reviewed UTF-8 and byte-order guards, and sets the flag only after
successful completion.
After its inactive 70-byte literal pool, the 136-byte full-screen buffer
synchronizer at `0x0047366C` is source-owned. It constructs the
`(0,0)...(575,287)` area directly, retains the display word at `0x200746B8`,
and exposes the remaining readiness, transfer, selection, and completion
operations as four reviewed display-port ABIs.
The installed callback at `0x004736F4` is source-owned as well. The setup
routine still registers stock Thumb pointer `0x004736F5` from `0x00473908`,
which reaches the generated entry redirect. Source preserves the area copy
and wrapped coordinate translation, buffer selection, readiness gate,
display field `+0x30` clear, source buffer-sync call, and final `576x288`
clear sequence.
The following setup sequence at `0x00473782` is source-owned too. It allocates
and publishes the 28-byte display state, applies the recovered `576x288`
format-13 configuration, registers callback pointer `0x004736F5`, creates and
publishes the full-screen format-6 buffer, and preserves attach, mode, size,
position, and failure-diagnostic calls as reviewed fixed ABIs.
The adjacent lock, unlock, mutex initializer, and display-port initializer at
`0x0047381E...0x00473933` are source-owned. They preserve mutex word
`0x200746BC`, the 1,000-tick acquisition timeout, task-versus-IRQ release
selection, all recovered diagnostics, and link the port initializer directly
to the source mutex and display setup functions. The now-inactive 74-byte
shared literal pool remains official data.
The following PRIMASK-read enable/disable primitives and display-task
attribute accessor at `0x00473934...0x00473951` are source-owned too. The
interrupt primitives retain their architectural `MRS` then `CPSIE/CPSID`
ordering, while the accessor makes retained data pointer `0x00776A3C`
explicit.
The adjacent display-driver thread and message-queue initializers at
`0x00473952...0x00473AA3` are source-owned as well. They preserve handle
words `0x20000660` and `0x20000664`, retained RTOS constructors, thread entry
`0x00473C45`, the reviewed thread and queue attribute pointers, queue
dimensions `96 x 36`, and the original success/failure diagnostic gates.
The following display runtime cluster at `0x00473AA4...0x00473C43` is
source-owned too. It preserves thread terminate-before-clear behavior,
resource ID 12 acquire/release calls, timer creation and handle publication at
`0x200744F0`, the 2,000-tick start interval, and the zeroed 36-byte queue
messages for commands 6 and 8. The command-8 helper retains its externally
called entry at `0x00473BC4`, byte truncation, and zero/-one result ABI.
The adjacent manager thread at `0x00473C44...0x00473E2D` is source-owned as
well. Its infinite receive loop retains queue retry and zeroing, enter/leave
hooks, the active word at `0x200744EC`, the gate-or-message-word-eight policy,
commands 0 through 6 and 8, timer transitions, six-word forwarding, query
output order, byte truncation, and both recovered diagnostic paths.
The six public queue senders at `0x00473E2E...0x004740FF` are source-owned
too. They emit zeroed 36-byte messages for clear, initialize, power up/down,
brightness, and six-word reflash commands with the fixed queue, priority zero,
1,000-tick timeout, per-API diagnostics, and the reflash sender's zero/-one
return ABI.
The forced lifecycle functions at `0x00474100` and `0x0047432C` are
source-owned as well. After their retained literal/diagnostic pools, the
shared file wrappers at `0x00474550...0x00474CD1` are source-owned. They
retain the 0x60-byte stream object, driver pointer `0x20071AC8`, mutex handle
word `0x200748F4`, 1,000-tick acquire timeout, `r`/`w`/`a`/`+` mode-bit
composition, backend byte-count ABI, allocation/free ordering, and the
file-write diagnostic policy. Seek and tell also retain origin validation,
signed offsets, position results, and backend result normalization. Size
retains the manually recovered transfer caller, successful length return, and
`EBADF`/`EBUSY`/`EIO` failure mapping. The adjacent flush wrapper through
`0x0047498B` is source-owned too and retains its null/standard-stream no-op,
mutex/backend sequence, and `EBUSY`/`EIO` failure mapping. The following
path-removal wrapper retains the runtime-ready no-op, null validation,
serialized backend call, already-absent success, and error mapping. The
following path-rename wrapper retains the same ready-state gate, validation of
both paths, serialized backend call, and error mapping. The intervening
directory-create wrapper retains its ignored mode argument and separate
`EEXIST`, `ENOENT`, and general `EIO` mappings. Directory open retains its
0x240-byte object, bounded path mirror, serialized backend call, cleanup
ordering, and `ENOENT`/`ENOMEM`/`EBUSY`/`EIO` mappings. Directory read retains
the shared dirent object at `0x200701E8`, end-of-directory behavior, bounded
name copy, and backend-to-dirent type translation. Directory close retains
the recovered runtime-not-ready success case, serialized backend close,
unconditional post-backend free, and `EBADF`/`EBUSY`/`EIO` failures. The
intervening mode-literal pool remains opaque compatibility data. The following
allocation, free, and reallocation wrappers at
`0x00474CD2...0x00474D9B` are source-owned too. They retain the separate mutex
word `0x200748F8`, heap-handle word `0x20074ABC`, 1,000-tick serialization,
backend allocation/free/reallocation ABIs, and all three timeout diagnostics.
The adjacent 160-byte file-runtime initializer is source-owned too. It creates
and publishes the primary and heap mutexes, preserves the zero/minus-one
result ABI, and retains the recovered success/failure diagnostics. Its
following 120-byte literal pool remains a distinct official-data region.

The next five Apollo510 cache-controller HAL functions through
`0x00475193` are source-owned. They preserve the cache-power state gate at
`0xE001E300`, SCB instruction/data cache control, the prefetch configuration
at `0x200001C8`, exact DSB/ISB ordering, whole-cache set/way operations, and
unaligned range-maintenance behavior. Their following 52-byte register literal
pool remains official compatibility data.
The adjacent application-wide memory comparator at
`0x004751C8...0x0047522F` is source-owned too. It preserves the optimized
stock ABI's exact byte-difference results and normalized minus-one/plus-one
aligned-word mismatch results for all 64 raw callers.
The following Apollo510 secure-OTA descriptor-addition routine at
`0x00475230...0x00475285` is source-owned as well. It preserves the SDK
`am_hal_ota_add` ABI, including the inclusive MRAM upper bound, exact
eight-image guard, counter update before programming, pending-bit encoding,
backend status propagation, and successful OTA-pointer valid-bit update. Its
ten-byte literal pool at `0x00475286...0x0047528F` remains official
compatibility data.
The adjacent BLE message-transmit thread entry at
`0x00475290...0x00475307` is source-owned too. Its retained lifecycle calls
and thread-flags wait/dispatch loop preserve initialization order, valid
positive flags, zero and CMSIS error returns, conditional diagnostics, and
indefinite retry. The stored Thumb pointer at `0x00475E68` continues to target
the original redirected entry.
The following lifecycle hooks through `0x00475333` are source-owned as well:
two exact in-place no-ops surround the BLE TX queue initializer. The
initializer writes the CMSIS 150-element, four-byte queue handle to
`0x2000402C` and retains the stock fatal path when allocation fails.
The adjacent setup-stage adapters and thread creator/destructor through
`0x0047538B` are source-owned too. They preserve stage index 8, entry pointer
`0x00475291`, attributes pointer `0x0075B85C`, state handle at `0x20004028`,
fatal creation failure, conditional termination, and handle clearing.
The following queue drain, thread-flag router, and wait handler through
`0x00475523` are source-owned too. They preserve nonblocking queue polling,
commands 1/2/4/8, source message freeing, bits `0x00400000` and `0x00800000`,
diagnostic gates, and the indefinite retained-backend wait.
The adjacent queue-clear routine through `0x0047564D` is source-owned too. It
preserves the null-handle result, initial/final depth queries, zero-timeout
drain/free loop, returned freed count, and diagnostics.
The following enqueue core through `0x00475A37` is source-owned too. It
preserves all four message layouts, 16-bit length arithmetic, stream reset,
half-capacity backpressure, queue submission, failure cleanup, and bit-22
thread wakeup across all eight stock callers. The adjacent direct
protobuf-over-BLE wrapper through `0x00475AA5` is source-owned as well. Its
three callers preserve byte/length truncation, source enqueue forwarding,
OTA-active suppression, gated structured and trace diagnostics, and
constant-zero OTA return. The following protobuf-notification counterpart
through `0x00475B13` is source-owned too. Its two callers preserve subtype
one and its distinct function, line, structured-message, and trace-message
constants. The following guarded protobuf sender through `0x00475C19` is source-owned as
well. Its 76 callers retain the four-register ABI; OTA activity returns zero,
the left-lens predicate returns status eight, both reject paths suppress
enqueue and preserve their exact diagnostics, and accepted sends truncate and
forward to the source enqueue core. The following guarded protobuf-notification
sender through `0x00475D5D` is source-owned too. Its 39 callers preserve OTA
precedence, left-lens and command-role status-eight rejection, subtype-one
enqueue forwarding, truncation, diagnostics, and result propagation. The
shared literal pool at `0x00475D5E...0x00475D77` remains official data; the
following streaming-notification wrapper at `0x00475D78...0x00475DD7`,
ungated transport-three sender at `0x00475DE0...0x00475DF9`, and EFS send and
notify wrappers at `0x00475DFA...0x00475ED3` are source-owned as well. Their
8-byte and 10-byte intervening pools and the 236-byte shared pointer table at
`0x00475ED4...0x00475FBF` remain official data. The scanner wrapper at
`0x00475FC0...0x00475FE1` is source-owned too and now supplies its
string-reader callback from the overlay instead of computing the old
`0x00439BC7` callback pointer. Its 6-byte alignment/displacement pool remains
official data. The following littlefs directory/recovery/initialization functions and
read/program/erase/sync callbacks through `0x004764DF` are source-owned as
well. Their config-table entry words remain at `0x006E83A8...0x006E83B4`;
the 138-byte dependency pool at `0x00476452...0x004764DB` remains official
data. The following event-loop initializer, queue worker/push path, timer
callback, delayed insertion, and delayed removal through `0x00476BEF` are
source-owned too. Their two-byte worker alignment and 204-byte dependency
pool through `0x00476CBB` remain official data. The following BLE
connection-parameter update scheduler through `0x00476DB7` is source-owned
too, preserving immediate updates and mode-derived delayed retries. The two
following connection-mode selectors through `0x0047720B` are source-owned
too, preserving their 25- and 72-unit thresholds and complete diagnostics.
The adjacent connection-mode coordinator through `0x0047761B` and delayed
callback through `0x0047773D` are source-owned as well, preserving selector
state, pending retry behavior, controller/context/role gates, and both
12-byte command layouts. Their 54-byte literal pool remains official data.
The following remote connection-parameter handler through `0x00477A69` is
source-owned too, preserving its received state, diagnostics, secondary-mode
selection, and role-gated 60-second retry. Its 114-byte literal pool remains
official data. The following connection-update event state machine through
`0x004780D7` is source-owned too, preserving status-specific retry behavior,
25/72-unit mode reconciliation, state publication, and all delayed callback
paths. Its four-byte pointer literal remains official data. The following
BLE connection-global initializer through `0x004780F7` is
source-owned too, preserving the endpoint byte, both caller-supplied pointers,
and fixed defaults-table pointer. The five following BLE connection-mode
control helpers through `0x0047826B` are source-owned too, preserving stream
readiness, short/long scheduling, retry holdoff, diagnostics, and remote-mode
reset. Their interleaved literal pools remain official data. The following
connection-event dispatcher through `0x004786B3` is source-owned too,
preserving its identifier/state mapping, seven recovered message classes,
profile-selected defaults, callback removal, source-owned remote/event and
scheduling paths, coordinator forwarding, and diagnostic records. Its
240-byte dependency pool remains official data. The following MRAM
zero-region programmer and protected update-flag setter through
`0x00478965` are source-owned too, preserving cache coherence, zero-fill and
word-count behavior, update-record idempotence/template construction, exact
PRIMASK restoration, and programmer diagnostics. Their 74-byte literal pool
remains official compatibility data. The following protected-MRAM record
diagnostic dump through `0x004793E9` is source-owned too, preserving
byte-index selection, all scalar and label fields, four hex-dump ranges, both
sparse halfword tables, and exact log/trace gates. Its 46-byte front-literal
pool remains official compatibility data. The following MRAM record
synchronizer through `0x0047956B` is source-owned too, covering two-pass
record qualification, record-table pointer reload, bit-two mutation,
timestamped publication, final-record signaling, batch commit, diagnostic
gates, and preservation of incoming `r0` through `r3`. Its 112-byte dependency
pool is shared with the record diagnostic dump and remains official
compatibility data. The following protected-MRAM record-list loader through
`0x00479981` is source-owned too, preserving ten-slot traversal, source and
destination strides, cache invalidation, zero/erased sentinel termination,
exact active-state validation, four-key mask rebuilding and persistence,
invalid destination clearing, valid record copying, IRK dumps, loaded counts,
and all recovered diagnostics. Its local 200-byte copy and clear paths are
source loops. The following 38-byte diagnostic continuation pool remains
official compatibility data. The following single-record programmer at
`0x004799A8...0x00479AB3` invalidates the data cache, writes the selected
0x100-byte protected slot as two ordered 0x80-byte transactions, performs the
stock yield only in thread mode, and preserves both transaction statuses and
their diagnostics. Its following 192-byte literal/dependency pool remains
official compatibility data. The following protected-MRAM application
record-database updater through `0x0047A461` is source-owned too, preserving
the existing-record and empty-slot fast paths, direct reusable-slot priority,
strict oldest-inactive and active-record replacement ordering, type
preference, diagnostic dumps, source-owned programming and comparison,
post-write cache invalidation, identifier verification, all diagnostics, and
the stock return value after verification failure. Its following 26-byte
literal pool remains official compatibility data. The following 32-byte
record-deactivation adapter through `0x0047A49B` is source-owned too,
preserving both flag clears, source database persistence, retained NVM
verification, exact pointer/call order, and the verifier return value. The
following 282-byte record-activation adapter through `0x0047A5B5` is
source-owned too, preserving the low-byte diagnostic argument and record
mask, ordered activity-flag mutation, incremented `0x20074344` counter and
record timestamp, source database update, unconditional retained NVM
verification, success diagnostics only for updater result one, and the
original full-width mask return. Its following 10-byte padding/literal pool
remains official compatibility data. The following 16-byte conditional
deactivation adapter through `0x0047A5CF` is source-owned too, preserving the
zero-only confirmation-byte gate and same-pointer call to source
deactivation. Its callers discard the stock routine's incidental return. The
following five record-query helpers through `0x0047A6FF` are source-owned
too, preserving exact membership flags and identity, untyped-record presence,
null and arbitrary-pointer active traversal, low-byte type counting, and
strict-minimum oldest-record selection. Their three intervening literal pools
remain official compatibility data. The following protected-record allocator
through `0x0047A855` is source-owned too, preserving type-threshold eviction,
release/deactivation ordering, first-free selection, initialization, and
timestamping. Its six-byte following gap remains official compatibility
data. The following record initialization wrapper through `0x0047A891` is
source-owned too, preserving cache invalidation, record-list loading,
synchronization, and all ten diagnostic dumps. Its following 50-byte literal
pool remains official compatibility data. The following Cordio address
resolver through `0x0047AB4D` is source-owned too, preserving the exact
resolvable-private-address classification, first-valid-IRK submission,
mapped-owner record matching, and diagnostics. Its following 30-byte
diagnostic-pointer pool remains official compatibility data. The following
resolved-address callback through `0x0047ACE9` is source-owned too, preserving
low-16-bit index handling, record validity checks before address use, resolved
address diagnostics, and the LTK-valid return. Its following 14-byte
diagnostic-pointer pool remains official compatibility data. The following
Cordio database delete-all adapter through `0x0047AD69` is source-owned too,
preserving the exact per-record flag and address clearing order, structured
and trace diagnostics, and database persistence. Its following 10-byte
record-table and diagnostic-pointer pool remains official compatibility data.
The following Cordio application-database address lookup through
`0x0047ADC5` is source-owned too, preserving owner normalization, active
record filtering, exact six-byte address comparison, first-match selection,
and timestamp refresh. Its following 14-byte pointer pool remains official
compatibility data. The following Cordio security-database LTK-request lookup
through `0x0047AE25` is source-owned too, preserving low-16-bit diversifier
matching, exact eight-byte random-number comparison, first-match selection,
and timestamp refresh. Its following 82-byte shared pointer pool remains
official compatibility data. The following Cordio key accessor through
`0x0047AEBF` is source-owned too, preserving valid-mask gating, all four key
classes, the two LTK security-level outputs, byte truncation, and unsupported
types. The adjacent peer-address and peer-address-type accessors through
`0x0047AED3` are source-owned too, preserving their exact null behavior. The
following Cordio key writer through `0x0047B3AD` is source-owned too,
preserving all four key layouts, mask updates, diagnostics, sign-counter
reset, and exact-one persistence. The following Cordio application-database
record-metadata accessors through `0x0047B4D3` are source-owned too,
preserving peer/device database hashes, cache/discovery state, CCC values,
client supported features and change awareness, handle-list persistence,
peer sign counters, and peer address-resolution state. Three intervening
literal/alignment pools remain official compatibility data. The following
Cordio resolving-list reload wrapper through `0x0047B567` is source-owned
too, preserving its before/after diagnostics, retained reload request, and
direct source-owned MRAM synchronization. Its following 52-byte literal pool
remains official compatibility data. The following Cordio complete-record
clear wrapper through `0x0047B6DB` is source-owned too, preserving owner-byte
truncation, null/miss/success diagnostics, source-owned lookup and
deactivation, and retained release. Its following 84-byte pointer pool
remains official compatibility data. The following protected-MRAM write
verifier through `0x0047BBF7` is source-owned too, preserving whole-cache
invalidation, first persisted-record matching, field and selected-key
comparisons, diagnostics, and hex dumps. Its following 56-byte pointer pool
remains official compatibility data. The following protected-MRAM
record-status reporter through `0x0047C069` is source-owned too, preserving
both inactive classifications, active record metadata, reversed identifier
display, strict timestamp selection, cache invalidation, and diagnostics. Its
following 26-byte pointer pool remains official compatibility data. The
following Cordio record timestamp-update wrapper through `0x0047C149` is
source-owned too, preserving its null guard, overflow renumbering call,
monotonic counter/write, diagnostics, source-owned persistence, and
source-owned verification. Its following 26-byte pointer pool remains
official compatibility data. The following Cordio timestamp-renumbering
routine through `0x0047C275` is source-owned too, preserving start,
per-selected-record, and end diagnostics, the ten-slot allocation/activity
gates, counter reset, slot-ordered timestamp assignment, and source-owned
persistence. Its following 70-byte pointer pool remains official
compatibility data. The following Cordio persistent-record status reporter
through `0x0047C503` is source-owned too, preserving the initial whole-cache
clean/invalidation, ten-slot protected-MRAM scan, valid/in-use/nonempty
selection, reversed address bytes, key masks, record counts, base address,
geometry, and diagnostics without mutating records. Its following 100-byte
pointer pool remains official compatibility data. The following Cordio
pairing-failure handler through `0x0047C8A1` is source-owned too, preserving
connection/status truncation, NVM status reporting before connection lookup,
validity and LTK-mask qualification, all four named SMP failure reasons,
unknown reasons, retained record clearing, direct invalid-record flag
clearing, and diagnostics. After 42 bytes of retained alignment and diagnostic
pointer data, the following connection-indexed pairing-record clearer through
`0x0047CA97` is source-owned too, preserving handle truncation, lookup,
record qualification, direct invalid-record flag clearing, source-owned
MAC-address clearing and resolving-list reload, and outcome diagnostics. Its
following four-byte dependency pointer remains official compatibility data,
and the following ten-slot record diagnostic iterator through `0x0047CABD`
is source-owned too. It preserves the single record-table-holder read, exact
200-byte stride, ordered source-owned diagnostic dumps, and no record
mutation. Its following 262-byte alignment/table/pointer pool remains
official compatibility data. The following EFS non-reflected CRC-32C updater
and protected-MRAM byte-program wrapper through `0x0047CC13` are source-owned
too. They preserve the Castagnoli algorithm without its sole table
dependency, unsigned byte-to-word rounding, source-owned interrupt disable,
exact PRIMASK restoration, program key and arguments, and ignored program
result. Their following eight-byte literal pair remains official
compatibility data. The following ARM EABI signed and unsigned 64-bit
division/modulo helpers through `0x0047CE8F` are source-owned too, preserving
the stock register ABI and divide-by-zero policy. Their two-byte alignment
pad remains official compatibility data. The three adjacent eight-byte
lens/status packet reporters through `0x0047CF5F` are source-owned too,
including their source-defined templates and fixed command/send ABI. The
following command-`0x103` dispatcher through `0x0047D817` is isolated as one
function-specific compatibility blob. Its neighboring publisher, template-4
reporter, and five state accessors through `0x0047D8FB` are source-owned,
while the following 200-byte literal pool remains separately mapped
compatibility data. The availability wrapper and selector-dependent status
query through `0x0047D9F9` are source-owned too; their two-byte alignment pad
remains compatibility data. The following SARC state-header checksum,
validator, initializer, bounded variadic report appender, payload finalizer,
and crash-file persistence routine through `0x0047DC21` are source-owned too.
The following 82-byte retired compatibility pool remains separately mapped;
the following wrap-extending monotonic-seconds helper through `0x0047DCB3` is
source-owned too. The following bounded wall-clock seconds helper and shared
interrupt-disable primitive through `0x0047DCEB` are source-owned too. The
following boot reset-status and firmware-version encoding helpers through
`0x0047DD61` are source-owned too. The following four-function EasyLogger
tracepoint deferral and bounded capture-retry cluster through `0x0047DDFD` is
source-owned too. The following tracepoint CRC/path/directory/state/storage
cluster through `0x0047E069` is source-owned too. The following tracepoint
active-file close/callback, pruning, creation, append-open, write/rotation,
commit, and flush cluster through `0x0047E231` is source-owned too, with three
intervening data islands retained explicitly. The following tracepoint timer
bootstrap through `0x0047E271` is source-owned too. Its 94-byte literal/data
pool remains compatibility data. The following protobuf onboarding control
update through `0x0047E31F` is source-owned too. The following gated protobuf
wear-status notifier through `0x0047E3E5` is source-owned too. The following
deferred onboarding-flag persistence worker through `0x0047E46F` is
source-owned too. The following onboarding-flag updater through `0x0047E4A5`
is source-owned too. The following peer onboarding-flag notification through
`0x0047E51B` is source-owned too. The following peer onboarding-flag reply
through `0x0047E58D` is source-owned too. The following peer onboarding
process synchronization through `0x0047E609` is source-owned too; its
106-byte literal/data table remains compatibility data, and the next opaque
executable boundary is `0x0047E674`.

The bootloader installs the application in place; no second application slot
or autonomous rollback has been observed.

The same Apollo payload is used for both left and right temples. Per-device
information space, pairing data, keys, calibration, and external flash are not
represented by this bundle.

## Charging-case STM32G0 flash

| Logical start | End exclusive | Function | Status |
|---:|---:|---|---|
| `0x08000000` | `0x08040000` | Active logical 256 KiB bank | Confirmed |
| `0x08040000` | `0x08080000` | Inactive logical 256 KiB bank | Confirmed |
| `0x08000000` | `0x0800D9C8` | Case application image | Confirmed |
| `0x08040000` | `0x0804D9C8` | Same image while programmed into inactive bank | Confirmed alias/install target |

The case updater erases 128 2-KiB pages in the inactive bank, programs
eight-byte doublewords, verifies a 32-bit additive sum, then toggles the
STM32G0 `nSWAP_BANK` option. After the swap, the newly selected physical bank
appears at logical `0x08000000`.

The updater explicitly preserves these device-specific windows:

- bank 1: `0x0803F000...0x0803F00F` and
  `0x0803F800...0x0803F807`;
- bank 2: `0x0807F000...0x0807F00F` and
  `0x0807F800...0x0807F807`.

The raw split artifact is an application image, not a safe 512-KiB whole-flash
replacement.

## EM9305 Bluetooth controller

The record table directly encodes four destinations:

| Address | Size | Function |
|---:|---:|---|
| `0x00300000` | 224 B | Record 0 |
| `0x00300400` | 656 B | Record 1 |
| `0x00302000` | 56 B | FHDR descriptor; entry point `0x00302028` |
| `0x00302400` | 210,888 B | Application record |

These are confirmed controller addresses. Gaps between records are preserved;
the builder does not synthesize a flat gap-filled EM9305 image.

The application is ARC EM7D/ARCv2 EM. Authenticated SDK archive `.comment`
sections identify the object compiler as Synopsys MetaWare ARC Compiler
T-2022.09 build 004 / LLVM 14.0.6, EM-Micro target, with `-Os`. Its current
semantic subdivision is:

| Address range | Size | Segment status |
|---|---:|---|
| `0x00302400...0x00302517` | 280 B | Stock-retained application prefix; reachable vector/ROM seams partly analyzed |
| `0x00302518...0x00302663` | 332 B | Fully archive-identified QK ARC port: `qkPortDummy`, `IRQHandler_SWI0`, `QK_noPreemption`, `QK_restoreContext`, `IRQHandler_SWI1`, and two alignment spans; exact after relocation normalization |
| `0x00302664...0x00302E7F` | 2,076 B | Stock-retained application; partly analyzed |
| `0x00302E80...0x00302E8D` | 14 B | Exact SDK-archive `BSP_Init` body |
| `0x00302E8E...0x00310BDF` | 56,658 B | Stock-retained application/vendor code and data interleaved with exact Packetcraft controller/baseband/LL/PAL and EM HAL/system/radio functions from the expanded SDK census |
| `0x00310BE0...0x00310C07` | 40 B | Fully named and behaviorally bounded vendor-modified `ProtTimer_SetHwTriggerEnable`; same SDK role/size, with stock critical-section protection |
| `0x00310C08...0x00310CE9` | 226 B | Exact relocation-normalized SDK `ProtTimer_StoreConfig` |
| `0x00310CEA...0x00310CEB` | 2 B | Compiler alignment |
| `0x00310CEC...0x00310D17` | 44 B | Exact relocation-normalized SDK `ProtTimer_UpdateRestartTime` |
| `0x00310D18...0x003117EB` | 2,772 B | Fully source/archive-identified QP/C 6.5.1 cluster; 22 portable functions / 2,450 bytes hash-bounded, all QF/QK hook owners and all shared-assertion calls assigned, no anonymous executable bytes, and approximately 80–90% semantically reversed |
| `0x003117EC...0x003126DF` | 3,828 B | Stock-retained mixed QP/vendor BLE/application code and data; `Q_onAssertExt` is fully bounded through `0x003117F7`, with exact SDK controller/support functions interleaved through the remainder |
| `0x003126E0...0x003128E3` | 516 B | Stock-retained vendor-configured `SLEEP_MANAGER_GoToSleep`; boundary, sole caller, `ILINK` race guard, and two hardware `SLEEP` sites recovered; partially reverse engineered |
| `0x003128E4...0x00312917` | 52 B | Exact relocation-normalized SDK `SLEEP_MANAGER_RCCAL_Callback` |
| `0x00312918...0x00334513` | 138,236 B | Stock-retained mixed BLE/application code and data; extensively classified by exact WSF/HCI/LL/baseband/controller SDK functions, with modified functions and data still interleaved |
| `0x00334514...0x0033454F` | 60 B | Fully classified retained module-name table (`MyApp`, six QP modules, `WsfOs`) |
| `0x00334550...0x00335B93` | 5,700 B | Stock-retained tail data/code; opaque except separately inventoried strings |
| `0x00335B94...0x00335BB7` | 36 B | Fully classified retained nine-entry QF/QK hook function-pointer table |
| `0x00335BB8...0x00335BC7` | 16 B | Stock-retained terminal data; opaque |

Within the QP cluster, `[0x00311554,0x003115E4)` is a pinned 144-byte QK
activation/scheduling candidate and `0x003117D8` is the shared assertion
handler reached by 31 direct calls across the application. All calls are
module-assigned: 29 portable QP calls plus `MyApp` ID 181 and `WsfOs` ID 653.
The 188-byte `QActive_post_` candidate at `[0x00310E28,0x00310EE4)` pins the
v6.3.6 portable ancestry floor, three-argument non-Q-SPY ABI, and ARC
`CLRI; SYNC` / `SETI` critical-section convention.
The exact release is QP/C v6.5.1 at official commit
`416dcec8820b9cdb5827497e645d0d9375db53c6`, independently identified by the
authenticated EM9305 SDK v4.2 source oracle. Seven callback globals occupy
`0x0080FE04...0x0080FE1F`; their names and stock accesses are pinned by the
analyzer. This does not prove the vendor's exact private checkout.
Six authenticated SDK archives now prove 98 exact functions / 7,172 bytes
(92 globally unique fingerprints / 7,146 bytes) across QP/C, PML, sleep
manager, sleep timer, protocol timer, and unitimer. The assertion-bearing
upstream `qf_time` closure is absent from the module table/reference topology;
`QF_init` proves `QF_MAX_TICK_RATE=0`, while the separate vendor protocol and
sleep-timer libraries are now directly located. The unused QP time-event
counter layout remains non-observable.
An expanded 16-archive discovery lane adds 1,146 distinct exact functions /
132,610 bytes. With the first six archives, its first combined pass contains
1,244 non-overlapping functions in 781 merged intervals / 139,782 bytes. A
second 32-archive lane then adds 67 globally new functions / 13,078 bytes: 62
Packetcraft ISO/BIG bodies, four EM NVM erase/write bodies, and `AOAD_Init`.
The 16-byte-floor 1,311-function map covers 152,860 bytes in 812 merged
intervals. A boundary/xref-qualified 8-byte replay promotes 124 additional
short or relocation-heavy functions / 2,106 bytes while withholding five
uncorroborated candidates. Strict exact-neighbor link-order tiling resolves 16
exact bodies / 784 bytes. Its NOP-aware extension adds 34 exact bodies / 774
bytes and 123 non-exact function identities / 9,080 bytes. The current exact
map is 1,494 functions / 157,122 bytes in 875 merged intervals (74.504950%).
Function-provenance coverage is 167,684 bytes in 879 intervals (79.513296%).
Four vector-resolved handler segments are now explicit:

| Range | Bytes | State |
|---|---:|---|
| `0x00305B1C...0x00305BDD` | 194 | Exact SDK `IRQHandler_ArcTimer0`; vector IRQ 0 resolves duplicate body |
| `0x00305BE0...0x00305CA1` | 194 | Exact SDK `IRQHandler_ArcTimer1`; vector IRQ 1 resolves duplicate body |
| `0x00306384...0x0030643D` | 186 | Exact SDK `IRQHandler_RadioRx`; vector IRQ 21 resolves duplicate body |
| `0x00306440...0x003064F9` | 186 | Vector-identified `IRQHandler_RadioTx`; vendor-modified from 380-byte SDK TX body, still stock-retained |

The dynamic per-function address/name/object/archive/raw-hash map is enforced
by `tools/analyze_em9305_sdk_discovery.py`; representative anchors include
`BOOT_BootUp @ 0x00302AE8`, `BbBleInit @ 0x003032CC`, Bluetooth-5.4
`LlExtCreateConnV2 @ 0x0030B974`, `WsfOsStartOnly @ 0x003140D0`, and
`wsfDispatcherThread @ 0x00333C44`. The 53,766-byte exact-function complement
is not treated as wholly proprietary. Of the 43,204 bytes not yet
function-provenance identified, 264 are the vector table, 1,812 are boundary
`nop_s` alignment, and 7,470 are post-text tables/data. The remaining 33,658
bytes are conservatively marked unresolved code or mixed content.
The exact per-segment portable/remainder partition, including alignment,
partially reversed vendor callbacks, opaque boundaries, and the fully reversed
`Q_onAssert` adapter, is maintained in the
[QP/C ARCompact audit](research/em9305-qpc-arcompact-audit.md) and enforced by
`tools/analyze_em9305_qpc.py`.
Archive-object extraction, relocation masking, exact addresses, and evidence
hashes are maintained in the
[SDK archive match audit](research/em9305-sdk-archive-match-audit.md) and
enforced by `tools/compare_em9305_sdk_archive.py`.
The wider per-function census, archive identities, Packetcraft version limits,
and reproduction hashes are in the
[expanded SDK archive census](research/em9305-expanded-sdk-archive-census.md).
The [link-order recovery ledger](research/em9305-sdk-link-order-recovery.md)
records the 202 link-order and four vector-resolved exact, short,
relocation-only, and vendor-modified placements.
The [residual segment census](research/em9305-residual-segment-census.md)
records all 1,083 complement segments and structural boundaries.
No EM9305 byte is source-replaced yet.
See the [QP/C ARCompact audit](research/em9305-qpc-arcompact-audit.md).

## Touch controller

The 32-byte FWPK wrapper declares a 34,432-byte raw Cortex-M image. Its initial
stack pointer is `0x20002000`, and its reset vector is `0x00004675`, which
places the vector table at `0x00000000`. This base is strong vector-table
evidence but remains classified as inferred until the updater's write command
or controller part is independently recovered.

## Codec / DSP

The codec FWPK has two CRC-32-protected segments:

| Payload offset | Size | Function | Target address |
|---:|---:|---|---|
| `0x00000030` | 38,236 B | Codec segment 1 | Unresolved |
| `0x0000958C` | 287,808 B | Codec segment 2 | Unresolved |

The segment table provides IDs, offsets, sizes, and CRCs but no target
addresses. Their output filenames therefore say `address-unresolved`; no
flash plan should infer placement from their file offsets.

## Prior Apollo-main FreeRTOS task-name increment

| Range | Size | Ownership | Function |
|---|---:|---|---|
| `[0x00454F16,0x00454F38)` | 34 B | Generated redirect/NOP fill | Complete official `pcTaskGetName` entry |
| `[0x007B0280,0x007B02A6)` | 38 B | Source compiled | Relocated FreeRTOS V10.5.1 getter |

The leaf reads `pxCurrentTCB` at `0x20074A20`, returns TCB offset `0x34`,
and binds its sole call relocation to source-owned `ulSetInterruptMask` at
`0x007B0158`. The installed Apollo-main image now ends at `0x007B02A6`.

## Prior Apollo-main CMSIS mutex increment

| Range | Size | Ownership | Function |
|---|---:|---|---|
| `[0x0044971C,0x004497B6)` | 154 B | Generated redirect/NOP fill | Complete official `osMutexNew` entry |
| `[0x007B02A6,0x007B02A8)` | 2 B | Generated alignment | Four-byte alignment before relocated leaf |
| `[0x007B02A8,0x007B031C)` | 116 B | Source compiled | Relocated CMSIS-FreeRTOS v10.5.1 `osMutexNew` |

The leaf has five reviewed relocations: scheduler state at `+0x0E`, static
mutex creation at `+0x32/+0x5C`, and dynamic mutex creation at
`+0x56/+0x64`. They resolve only to source-owned targets at
`0x007AECFC`, `0x007AEEBC`, and `0x007AE100`. That release's installed
Apollo-main image ended at `0x007B031C`.

The overlay/component/package pins are respectively 114,680 bytes/
`7603cf2a0de6e8b05d66dc356bf3e0701f6157536d29bdac8ad692dc56e0362c`,
3,638,076 bytes/
`f696c6dfbd8ab1f7b5cc44fdc06fcdc5baf44f368ad55130e7571d82ee31ec82`,
and 4,416,258 bytes/
`11d40cd1b3648f96b5ec98c9fa2dff6de121e878978206a0a9694ede38d3a0ff`.
The focused production gate passes 10/10 tests offline; no hardware was
accessed.

## Prior Apollo-main FreeRTOS heap and CMSIS semaphore increment

| Range | Size | Ownership | Function |
|---|---:|---|---|
| `[0x00456110,0x00456338)` | 552 B | Generated redirect/NOP fill | Four complete official FreeRTOS `heap_4` functions |
| `[0x00441EA2,0x00441EC4)` | 34 B | Generated redirect/NOP fill | Complete official FreeRTOS `vQueueDelete` |
| `[0x0044989A,0x0044994E)` | 180 B | Generated redirect/NOP fill | Complete official CMSIS-FreeRTOS `osSemaphoreNew` |
| `[0x007B031C,0x007B057E)` | 610 B | Source plus 4 B alignment | Relocated `heap_4` source closure |
| `[0x007B057E,0x007B05A6)` | 40 B | Source plus 2 B alignment | Relocated `vQueueDelete` source leaf |
| `[0x007B05A6,0x007B065A)` | 180 B | Source plus 2 B alignment | Relocated `osSemaphoreNew` source leaf |

Those historical overlay/component/package pins are 115,510 bytes/
`6359e4e8c824af3cea36280a1aabd6ad671027e38fb3263fe9ac0cbb292660b4`,
3,638,906 bytes/
`00d112e265f40dd8bf98fc9021bba54b3bcc94f159111b2f4815d5484e91c67c`,
and 4,417,088 bytes/
`064c9429352132cee2a5dfe45c2bf52349e10111b89db91f093b1ce16ed0c2b0`.
The installed image ends at `0x007B065A`; all sixteen new relocations bind
to source-owned dependencies.

## Prior dual-image EasyLogger helper increment

| Image | Stock replacements | Appended source/alignment | Current overlay |
|---|---:|---:|---|
| Apollo main | 320 B | 390 B source + 10 B alignment at `[0x007B065A,0x007B07EA)` | 115,910 B, SHA-256 `e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d` |
| Bootloader | 320 B | 270 B source + 2 B alignment at `[0x004345D6,0x004346E6)` | 622 B, SHA-256 `fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813` |

The source-owned functions are `get_fmt_enabled`, its unsigned-argument and
pointer-argument predicates, and `elog_strcpy`. Image-specific source
providers bind the shared algorithms to the recovered logger objects and
assertion policies. Official assertion strings, hook globals, `elog_output`,
and wait wrappers remain explicit binary seams.

The 3,639,306-byte main component and 149,222-byte boot provider hash to
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.
The 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`;
its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`.

## Preceding Apollo-main FreeRTOS tick-getter increment

The stock entry map is corrected to two adjacent complete functions:

| Span | Bytes | Current ownership | Meaning |
|---|---:|---|---|
| `[0x00454EFE,0x00454F06)` | 8 B | Generated redirect/NOP fill | `xTaskGetTickCount`; SHA-256 `6dbb234e35fb86f883529c083fed0e1cabdca99d6647a95568ed1a5522310ac0` before replacement |
| `[0x00454F06,0x00454F10)` | 10 B | Generated redirect/NOP fill | `xTaskGetTickCountFromISR`; SHA-256 `8fe0a4f494b20b340d1126b2da725919f86c53cc3c1cabf5031fffc03f6de63a` before replacement |
| `[0x007B07EA,0x007B07EC)` | 2 B | Generated alignment | Zero pad before provider |
| `[0x007B07EC,0x007B07F8)` | 12 B | Source compiled | Relocation-free `xTickCount` provider for RAM `0x20074A34` |
| `[0x007B07F8,0x007B07FC)` | 4 B | Source compiled | Normal getter, sole relocation to provider |
| `[0x007B07FC,0x007B0800)` | 4 B | Source compiled | ISR getter, sole relocation to provider |

`0x00454F08` is the ISR getter's second instruction, not an entry. Nine
normal `BL` callers retain `0x00454EFE`; the sole ISR caller retains
`0x00454F06`. The authenticated stock pair totals 18 bytes and hashes to
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
The 3,412-byte MIT source has SHA-256
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`;
its header hashes to
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.

The 115,932-byte overlay and 3,639,328-byte main component hash to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`
and
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`.
The installed component ends at `0x007B0800`. Its raw application partition
is 116,118 source, 81,622 generated, and 3,441,556 opaque bytes. Builder
accounting reports 116,114 source-owned bytes including 182 in place, 81,626
generated patch-site bytes, 81,808 replaced-stock bytes, 3,441,556 opaque
base bytes, and the 32-byte wrapper.

The 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`;
its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions. The plan includes 53 source-compiled regions, 574
generated source-entry replacement regions, and 18 generated alignment
regions. Package ownership is 116,738 source bytes (2.642457%), 83,415
generated bytes (1.888165%), and 4,217,629 opaque bytes (95.469378%);
200,153 bytes (4.530622%) are controlled. Boot remains unchanged at 620
source, 817 generated, and 147,785 opaque bytes.

## Preceding Apollo-main FreeRTOS missed-yield increment

| Span | Bytes | Current ownership | Meaning |
|---|---:|---|---|
| `[0x004555E6,0x004555F0)` | 10 B | Generated redirect/NOP fill | Complete FreeRTOS V10.5.1 `vTaskMissedYield`; stock SHA-256 `8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d` |
| `[0x007B0800,0x007B080E)` | 14 B | Source compiled | Relocation-free `pdTRUE` store to recovered `xYieldPending` at `0x20074A44` |

Only two direct stock callers exist, at `0x00441FA2` and `0x00441FD8`; no
interior branch or stored pointer enters the ten-byte body. The source leaf
therefore preserves the complete reviewed entry topology.

The preceding overlay ended at `0x007B080E`. Its 115,946 bytes hash to
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`;
the 3,639,342-byte component hashes to
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`.
It contains 592 functions and 559 patch sites. Builder accounting is 116,128
source-owned bytes including 182 in place, 81,636 generated patch bytes,
81,818 replaced-stock bytes, and 3,441,546 opaque base bytes.

The canonical 4,417,796-byte package hashes to
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`
and records 831 placed, two unresolved, and five container-only regions. The
Linux profile places the byte-identical leaf at
`[0x007B0F38,0x007B0F46)` after two alignment bytes; its aggregate pins are
documented in
[`research/freertos-missed-yield-source-boundary-audit.md`](research/freertos-missed-yield-source-boundary-audit.md).

## Prior Apollo-main FreeRTOS task-leaf increment

| Span | Bytes | Current ownership | Meaning |
|---|---:|---|---|
| `[0x00455ACA,0x00455AE0)` | 22 B | Generated redirect/NOP fill | Complete `uxTaskResetEventItemValue`; SHA-256 `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049`; sole caller `0x0047ECCE` |
| `[0x00455AE0,0x00455AF6)` | 22 B | Generated redirect/NOP fill | Complete `pvTaskIncrementMutexHeldCount`; SHA-256 `3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f`; sole caller `0x00441D46` |
| `[0x007B080E,0x007B0810)` | 2 B | Generated alignment | Padding before the reset leaf |
| `[0x007B0810,0x007B082A)` | 26 B | Source compiled | Reset leaf, SHA-256 `04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6` |
| `[0x007B082A,0x007B082C)` | 2 B | Generated alignment | Padding before the mutex-held leaf |
| `[0x007B082C,0x007B0844)` | 24 B | Source compiled | Mutex-held leaf, SHA-256 `494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf` |
| `[0x00454D7C,0x00454D88)` | 12 B | Generated redirect/NOP fill | Complete `vTaskSuspendAll`; SHA-256 `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2`; 13 direct callers |
| `[0x00455556,0x00455566)` | 16 B | Generated redirect/NOP fill | Complete `vTaskInternalSetTimeOutState`; SHA-256 `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862`; four direct callers |
| `[0x007B0844,0x007B0854)` | 16 B | Source compiled | Suspend leaf, SHA-256 `0928ce291a4a96b18baf7304bc7f87fb828ac06902619f1f42500e04c73883be` |
| `[0x007B0854,0x007B0866)` | 18 B | Source compiled | Timeout-state leaf, SHA-256 `8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a` |

Both source leaves preserve the released volatile evaluations of
`pxCurrentTCB` at `0x20074A20`. The reset seam is event-list value `+0x18`,
priority `+0x2C`, and 56 priorities; the mutex-held seam is the `+0x64`
field with `configUSE_MUTEXES=1`.

Suspend increments 32-bit nested depth `uxSchedulerSuspended` at
`0x20074A58`; retained `xTaskResumeAll` decrements the same word. Timeout
capture stores `xNumOfOverflows` at `0x20074A48` and `xTickCount` at
`0x20074A34` into `TimeOut_t` offsets `+0` and `+4`.

The current overlay ends at `0x007B0866`. Its 116,034 bytes hash to
`d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd`;
the 3,639,430-byte component hashes to
`8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc`.
It contains 596 functions and 563 patch sites. Builder accounting is
116,216 source-owned bytes including 182 in place, 81,708 generated patch
bytes, 81,890 replaced-stock bytes, and 3,441,474 opaque bytes.

The 4,417,884-byte package hashes to
`e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7`.
Its 608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.
Linux places reset at `[0x007B0F48,0x007B0F62)` and mutex-held at
`[0x007B0F64,0x007B0F7C)`, with two alignment bytes before each, then
suspend at `[0x007B0F7C,0x007B0F8C)` and timeout capture at
`[0x007B0F8C,0x007B0F9E)` without padding.

## Prior scheduler-cluster map

| Stock range | Source target (Apple) | Source target (Linux) | Function |
|---|---|---|---|
| `[0x004420BC,0x004420D0)` | `[0x007B0868,0x007B0880)` | `[0x007B0FA0,0x007B0FB8)` | `vPortYield` |
| `[0x004420D0,0x004420E8)` | `[0x007B0880,0x007B089E)` | `[0x007B0FB8,0x007B0FD6)` | `vPortEnterCritical` |
| `[0x004420E8,0x00442114)` | `[0x007B08A0,0x007B08D6)` | `[0x007B0FD8,0x007B100E)` | `vPortExitCritical` |
| `[0x00455876,0x0045589C)` | `[0x007B08D8,0x007B08F8)` | `[0x007B1010,0x007B1030)` | `prvResetNextTaskUnblockTime` |
| `[0x0045504C,0x0045519E)` | `[0x007B08F8,0x007B0A50)` | `[0x007B1030,0x007B1182)` | `xTaskIncrementTick` |
| `[0x00454DCC,0x00454EFE)` | `[0x007B0A50,0x007B0B74)` | `[0x007B1184,0x007B12A8)` | `xTaskResumeAll` |

All six stock spans are complete redirect/NOP regions. Apple alignment occurs
at `[0x007B0866,0x007B0868)`, `[0x007B089E,0x007B08A0)`, and
`[0x007B08D6,0x007B08D8)`; Linux also aligns resume at
`[0x007B1182,0x007B1184)`. The canonical overlay ends at `0x007B0B74` and
the Linux overlay at `0x007B12A8`, leaving both well below `0x007F0000`.

Canonical overlay/component/package hashes are respectively
`b9cb2b00d4859650d120ff713a8af9a1ca626876b46bac751098abdbca575153`,
`fcb218fd5d9a33b2398cd046550b26258ca9da90d423c50ae635203535614a58`,
and
`5a31772a8a4fb746fa9eff53d618541fd38cf44a93c9d602eb88e15d142cef01`.

## Prior authenticated upstream LZ4 map

The active LZ4 path now uses authenticated upstream v1.10.0 source selected by
openCFW; the selection does not identify the stripped stock decoder's exact
point release.

| Stock span | Bytes | Current ownership / role |
|---|---:|---|
| `[0x00439710,0x004397A6)` | 150 | Fully reverse-engineered/source-recreated `__aeabi_memmove`; generated production redirect |
| `[0x004397A8,0x004397C4)` | 28 | Fully reverse-engineered/source-recreated VFP `sqrtf`; qualified candidate, stock still retained pending production placement |
| `[0x00439BE4,0x00439C04)` | 32 | Fully reverse-engineered/source-recreated public `__aeabi_memcpy` prefix; generated production redirect |
| `[0x00439C04,0x00439C8A)` | 134 | Fully reverse-engineered/source-recreated aligned `__aeabi_memcpy` entry; generated production redirect |
| `[0x00439CA4,0x00439CB2)` | 14 | Fully reverse-engineered/source-recreated DLIB domain-error setter; qualified candidate, stock retained |
| `[0x00439CB2,0x00439CC4)` | 18 | Fully reverse-engineered/source-recreated DLIB range-error setter; qualified candidate, stock retained |
| `[0x00439CC4,0x00439CD0)` | 12 | Fully reverse-engineered/source-recreated errno-address accessor returning `0x20074F14`; qualified candidate, stock retained |
| `[0x00439CD0,0x00439CE0)` | 16 | Fully classified errno pointers and alignment; retained stock data |
| `[0x004E0C0C,0x004E0C34)` | 40 | Generated redirect/NOP fill to the active source mode-2 adapter |
| `[0x0054EE90,0x0054EF08)` | 120 | Opaque unreachable stock variable-length reader |
| `[0x0054EF08,0x0054F338)` | 1,072 | Opaque unreachable stock generic decoder |
| `[0x0054F338,0x0054F356)` | 30 | Generated redirect/NOP fill to the active source safe adapter |

The complete provider SHA-256 values are
`31caf15ad676c4a99eace5673e1fe46b818b64d901707c461074e8acc5474b28`
for `memmove` and
`8e696e1fb54917a436f850e562f74e8cc8734c259fdaac9f767a3c264ff427cd`
for `memcpy`. They are bound as void EABI functions with destination/source/
count in `r0`/`r1`/`r2`; the active decoder does not consume a C-style return
value.

| Appended region | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Upstream decoder text | `[0x007B0B74,0x007B11F0)`, 1,660 B | `[0x007B12A8,0x007B1942)`, 1,690 B |
| Table alignment | none | `[0x007B1942,0x007B1944)`, 2 B |
| `inc32table` + `dec64table` | `[0x007B11F0,0x007B1230)`, 64 B | `[0x007B1944,0x007B1984)`, 64 B |
| Safe ABI adapter | `[0x007B1230,0x007B1234)`, 4 B | `[0x007B1984,0x007B1988)`, 4 B |
| Mode-2 adapter | `[0x007B1234,0x007B1252)`, 30 B | `[0x007B1988,0x007B19A6)`, 30 B |

The source-owned table span is read-only. No writable LZ4 allocation is
present. The old primary mode-2 and hand-decoder sections remain unreachable
under `_legacy` names (Apple
`[0x007973E8,0x00797406)` and `[0x00797408,0x007976C0)`); retaining them
keeps every later primary-overlay address fixed. Linux likewise retains its
30-byte mode-2 and 650-byte hand-decoder legacy sections at their established
profile-specific positions.

The final Apple overlay is `[0x00794324,0x007B1252)`, 118,574 bytes, SHA-256
`1a0b92e12203b78f48191969744128bfbcc2559c811ae40a1f393370eceacea9`.
Its 3,641,970-byte component hashes to
`6621c7d0403e37d0598c5f2f521633afb13b98034542c8010cf9d210f576e91d`,
and its 4,420,424-byte package hashes to
`d576be2c4626006a830593a5ad1aae21da8ee3e16d67d80c62eb8f3994bfc294`.

The Linux overlay is `[0x00794324,0x007B19A6)`, 120,450 bytes, SHA-256
`2901320d6169c2b9ad49d501cb25e7f50ceaa90b94e7d0640f80d318932d8fc7`.
Its 3,643,846-byte component hashes to
`140cac71e8ec612f2129800ee9a205c30f743dfd51664207c1661fdb337d8f8d`,
and its 4,422,300-byte package hashes to
`cb1516c2c61402626a723f05f4fb315e8af91adae599818830b2f8e1ffee0bf8`.

Canonical component accounting is 118,756 source-owned, 82,478 generated
patch, 82,660 replaced-stock, 3,440,704 opaque-base, and 32 wrapper bytes.
Canonical package accounting is 119,370 source, 84,277 generated, and
4,216,777 opaque bytes. Whole-image branch and stored-pointer scans found no
alternate route to the stock decoder bodies. The map and artifacts were
validated offline; no hardware was flashed or executed.

## Prior FreeRTOS queue/task closure map

| Stock range | Bytes | Current ownership |
|---|---:|---|
| `[0x00441A42,0x00441B0A)` | 200 | Generated redirect/NOP fill for `xQueueGiveFromISR` |
| `[0x00455370,0x00455466)` | 246 | Generated redirect/NOP fill for `xTaskRemoveFromEventList` |
| `[0x00455820,0x00455836)` | 22 | Generated redirect/NOP fill for `prvTaskCheckFreeStackSpace` |

| Appended region | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Alignment | `[0x007B1252,0x007B1254)` | `[0x007B19A6,0x007B19A8)` |
| `xTaskRemoveFromEventList` | `[0x007B1254,0x007B132C)` | `[0x007B19A8,0x007B1A80)` |
| `xQueueGiveFromISR` | `[0x007B132C,0x007B1400)` | `[0x007B1A80,0x007B1B54)` |
| `prvTaskCheckFreeStackSpace` | `[0x007B1400,0x007B143E)` | `[0x007B1B54,0x007B1B92)` |

The Apple overlay now ends at `0x007B143E`; the Linux overlay ends at
`0x007B1B92`. They are respectively 119,066 and 120,942 bytes with SHA-256
values
`da056ac28814f1b07c90d3651b290cd459bfde5e3cbcf30fed9a75a72729a0ae`
and
`8d56bdf484f3b1d67378f53eef89d7aea88282c6d552b8b2b1ee2bb7e0cb6905`.
Both remain below the `0x007F0000` ceiling. The map was assembled and checked
offline; it has not been written to G2 hardware.

## Preceding FreeRTOS timeout-check map

The complete official FreeRTOS V10.5.1 `xTaskCheckForTimeOut` body is
`[0x00455566,0x004555E6)`, 128 bytes. It is now a generated source-entry
redirect and NOP fill targeting the profile-selected source leaf. Its SHA-256
before replacement is
`83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c`.

| Appended region | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Alignment | `[0x007B143E,0x007B1440)`, 2 B | `[0x007B1B92,0x007B1B94)`, 2 B |
| `xTaskCheckForTimeOut` | `[0x007B1440,0x007B14C8)`, 136 B | `[0x007B1B94,0x007B1C1C)`, 136 B |

The leaf has no relocation or retained data. Its profile SHA-256 values are
`33f0782fa8af468bccf78b558cc010a9f7a89f30c7c76abced9a799feb6a93f5`
and
`486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c`.
Its direct providers remain fixed at `0x005FA0A4` (assertion mask),
`0x004420D0`/`0x004420E8` (critical entry/exit), and `0x00455556`
(`vTaskInternalSetTimeOutState`); its tick and overflow globals remain at
`0x20074A34` and `0x20074A48`.

The current Apple overlay ends at `0x007B14C8`, is 119,204 bytes, and hashes
to
`4b3071e64d0e183efbb59788c94dca8ae01fba6d952aecbb9682893844171a79`.
The Linux overlay ends at `0x007B1C1C`, is 121,080 bytes, and hashes to
`75054c31d8ca3e50659443c470f11a604fb715db430e08b3ad4c468042282324`.
They remain 256,824 and 254,948 bytes, respectively, below the conservative
`0x007F0000` ceiling. The canonical package is 4,421,054 bytes with SHA-256
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`;
the qualified Linux package is 4,422,930 bytes with SHA-256
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
This map was assembled and checked offline; it has not been signed, flashed,
or executed on G2 hardware.

## Preceding EasyLogger output/async map

The production entry replacements own these exact stock spans:

| Function | Stock span | Bytes |
|---|---|---:|
| `elog_output` | `[0x0043D574,0x0043D976)` | 1,026 |
| stock-compatible record builder | `[0x00448D4E,0x00448DD2)` | 132 |
| G2 submit wrapper | `[0x0044AA80,0x0044AA98)` | 24 |

| Appended closure | Apple clang 21.0.0 | exact-root Linux clang 22.1.8 |
|---|---|---|
| builder text + read-only data | `[0x007B14C8,0x007B15E2)` | `[0x007B1C1C,0x007B1D30)` |
| submit text | `[0x007B15E4,0x007B1602)` | `[0x007B1D30,0x007B1D4E)` |
| output text + read-only data | `[0x007B1604,0x007B1CF6)` | `[0x007B1D50,0x007B2346)` |

Apple has two alignment bytes before submit and two before output; Linux has
two before output. The strict extractor authenticates each exact 8-byte
selected-function `.ARM.exidx` CANTUNWIND/`R_ARM_PREL31` companion and then
deliberately discards it as metadata, so no unwind record is appended into
the executable closure. Both profile maps reproduced byte-identically in two
builds. They were not signed, flashed, reset, or executed on G2 hardware.
## Preceding EasyLogger hexdump source ownership

Apollo main now redirects the complete authenticated spans
`[0x0043DACC,0x0043DC88)`, `[0x00448CCC,0x00448D4E)`, and
`[0x0044AA76,0x0044AA80)` to production source. The builder/raw ends are
exactly adjacent to the existing source redirects at `0x00448D4E` and
`0x0044AA80`; the hexdump literal pool begins at the preserved
`0x0043DC88` boundary.

| Appended closure | Apple clang 21.0.0 | exact-root Linux clang 22.1.8 |
|---|---:|---:|
| bounded put | `0x007B1E90` / 22 | `0x007B25CC` / 22 |
| arithmetic hex put | `0x007B1EA8` / 268 | `0x007B25E4` / 264 |
| fill | `0x007B1FB4` / 84 | `0x007B26EC` / 84 |
| header formatter | `0x007B2008` / 238 | `0x007B2740` / 238 |
| byte/character/blank formatters | `0x007B20F8` / 78 | `0x007B2830` / 78 |
| level-less builder + rodata | `0x007B2148` / 262 | `0x007B2880` / 256 |
| raw submit | `0x007B2250` / 6 | `0x007B2980` / 6 |
| `elog_hexdump` + rodata | `0x007B2258` / 521 | `0x007B2988` / 507 |

All ranges are end-exclusive in the overlay/manifest contracts. No stock
literal or retained adjacent function is included in a replacement span.

## Preceding FreeRTOS+CLI parameter-accessor-only ownership

This phase assigned two exact fixed flash spans and two appended source
leaves:

| Fixed flash span | Bytes | Manifest file offset | Ownership / action |
|---|---:|---:|---|
| `[0x00541708,0x0054170A)` | 2 | 1,087,272 | Generated exact source copy of `CMP R0,#127` (`7f28`), replacing authenticated `CMP R0,#128` (`8028`) |
| `[0x005848FC,0x00584960)` | 100 | 1,362,204 | Generated `B.W` to the profile-selected production accessor plus 48 Thumb NOPs |

The capacity halfword is interior control flow and therefore has no independent
stock function entry. Its separately compiled two-byte source fragment is
appended, authenticated, and copied to `0x00541708`; the appended copy has no
branch or stored-pointer ingress. The accessor stock span is a complete
function boundary. Its 115 official callers continue to reach that same entry,
which is now the sole external `B.W` ingress to the appended source leaf.

| Appended closure | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| accessor alignment | `[0x007B2461,0x007B2464)`, 3 B | none |
| `open_cfw_freertos_cli_get_parameter` | `[0x007B2464,0x007B2560)`, 252 B | `[0x007B2B84,0x007B2C80)`, 252 B |
| `open_cfw_freertos_cli_collector_capacity_patch` | `[0x007B2560,0x007B2562)`, 2 B | `[0x007B2C80,0x007B2C82)`, 2 B |

The Apple component stores those appended regions at file offsets 3,646,593
through 3,646,850: three generated alignment bytes, 252 source bytes, and two
source bytes. Both source leaves are relocation-free. The accessor bytes hash
to `7b77ccc3441cb8e725fa8a97a8197e0f993a00456925c6eb0126e77fb00f9914`;
the capacity bytes hash to
`dbf2d8a1ffb886d7964cf470133c8a289aff606c14e6d75fd258678de0f47495`.
Whole-component scans reject every additional branch, interior target, and
aligned even or Thumb-form stored pointer into either appended range.

The final Apple overlay is `[0x00794324,0x007B2562)`, 123,454 bytes. The
exact-root Linux overlay is `[0x00794324,0x007B2C82)`, 125,278 bytes. Both
remain below the conservative `0x007F0000` ceiling. This map was assembled and
checked offline; no firmware was signed, flashed, reset, booted, or executed on
G2 hardware.

## Prior phase-local nanopb `pb_decode_varint` production map

The exact stock range `[0x0048F5B8,0x0048F628)` is now a generated B.W plus
full Thumb NOP-fill replacement. Its original 112 bytes hash to
`f93d678981f92603982c9afc6c6f9976ca14d1a7a7e0bfc949d3ff73f2791ff2`.
The replacement preserves the three entry callers at `0x00490156`,
`0x004901EC`, and `0x004902A0`; no branch or stored pointer enters an old
interior address.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| alignment | `[0x007B2562,0x007B2564)`, 2 B | `[0x007B2C82,0x007B2C84)`, 2 B |
| `open_cfw_nanopb_decode_varint` text | `[0x007B2564,0x007B25E4)`, 128 B | `[0x007B2C84,0x007B2D00)`, 124 B |
| local `"varint overflow\0"` | `[0x007B25E4,0x007B25F4)`, 16 B | `[0x007B2D00,0x007B2D10)`, 16 B |

The only external leaf dependency is `pb_readbyte` at `0x0048F454`, bound by
one reviewed `R_ARM_THM_CALL`; the string is closed by a local PREL MOVW/MOVT
pair. The Apple overlay is `[0x00794324,0x007B25F4)`, 123,600 bytes. The
Linux overlay is `[0x00794324,0x007B2D10)`, 125,420 bytes. Both remain below
the conservative `0x007F0000` ceiling. The map was assembled and checked
offline; it was not flashed to G2 hardware.

## Preceding CmBacktrace current-thread-name production map

The stock helper `[0x00593AF6,0x00593AFE)` is one complete generated entry
replacement; its four stock BL callers remain unchanged. The new source layout
is profile-specific:

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| G2 current-task-name adapter | `[0x007B25F4,0x007B2602)`, 14 B | `[0x007B2D10,0x007B2D1E)`, 14 B |
| generated alignment | `[0x007B2602,0x007B2604)`, 2 B | `[0x007B2D1E,0x007B2D20)`, 2 B |
| CmBacktrace helper | `[0x007B2604,0x007B2608)`, 4 B | `[0x007B2D20,0x007B2D24)`, 4 B |

The Apple overlay is now `[0x00794324,0x007B2608)`, 123,620 bytes. Linux is
`[0x00794324,0x007B2D24)`, 125,440 bytes. Both remain below `0x007F0000`.
The adapter preserves current-TCB address `0x20074A20`, name offset `0x34`,
and null-to-`0x34` behavior. No hardware execution was performed.

## Prior phase-local complete FreeRTOS+CLI console-task production map

The complete stock task `[0x00541600,0x0054171C)` is a generated `B.W` plus
140-NOP replacement. The sole authenticated stored Thumb pointer at
`0x0054178C` remains `0x00541601` and therefore reaches the generated redirect
without rewriting initializer data. The earlier exact capacity patch at
`[0x00541708,0x0054170A)` is no longer a separate region, and its appended
two-byte source leaf is absent.

| Source closure | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| fill | `[0x007B2604,0x007B26D2)`, 206 B | `[0x007B2D20,0x007B2DEE)`, 206 B |
| generated alignment | `[0x007B26D2,0x007B26D4)`, 2 B | `[0x007B2DEE,0x007B2DF0)`, 2 B |
| state initialization | `[0x007B26D4,0x007B26F0)`, 28 B | `[0x007B2DF0,0x007B2E0C)`, 28 B |
| 22-group registration | `[0x007B26F0,0x007B274E)`, 94 B | `[0x007B2E0C,0x007B2E6A)`, 94 B |
| generated alignment | `[0x007B274E,0x007B2750)`, 2 B | `[0x007B2E6A,0x007B2E6C)`, 2 B |
| command-process text | `[0x007B2750,0x007B2790)`, 64 B | `[0x007B2E6C,0x007B2EAC)`, 64 B |
| local prompt `"\n#\0"` | `[0x007B2790,0x007B2793)`, 3 B | `[0x007B2EAC,0x007B2EAF)`, 3 B |
| generated alignment | `[0x007B2793,0x007B2794)`, 1 B | `[0x007B2EAF,0x007B2EB0)`, 1 B |
| byte consumption | `[0x007B2794,0x007B27F4)`, 96 B | `[0x007B2EB0,0x007B2F10)`, 96 B |
| receive/poll once | `[0x007B27F4,0x007B2830)`, 60 B | `[0x007B2F10,0x007B2F4C)`, 60 B |
| task entry | `[0x007B2830,0x007B2858)`, 40 B | `[0x007B2F4C,0x007B2F74)`, 40 B |

The production task keeps `FreeRTOS_CLIProcessCommand` at `0x005847FE`, the
display helpers at `0x005415C2` / `0x005415D8`, the ring read at
`0x0057E136`, receive-handle slot `0x200748BC`, output array `0x20071B48`,
and input array `0x20071BC8`. It calls the 22 retained registration groups in
their authenticated order, covering 76 proprietary descriptors. Its
source-owned policies reserve input byte 127 for NUL and accept only receive
count one.

Removing the old capacity leaf compactly moves nanopb text to `0x007B2560`
/ `0x007B2C80`, the CmBacktrace G2 adapter to `0x007B25F0` / `0x007B2D0C`,
and its MIT helper to `0x007B2600` / `0x007B2D1C`. Their closure sizes and
attribution boundaries are unchanged. The final Apple overlay ends at
`0x007B2858`, is 124,212 bytes, and hashes to
`913d0b39126eac6d13ac05baa44c745cd2a0c7317957293e34bbf418547d96bd`.
Exact-root Linux ends at `0x007B2F74`, is 126,032 bytes, and hashes to
`bdc8bf69d75b7ff8354e12aa392416956a2afa04442488e7653e79b89ce62f1f`.
Their complete package pins are 4,426,062 /
`0c257168dfc07a39e4603847329f6ac542d093719f0ea9c5a4cf904707b83670`
and 4,427,882 /
`3aa279193bf67b50a75ad5490a8cd2e22ffb32d36f6de1e5befe0a11368fe743`.
This map was assembled and inspected offline; it was not signed, flashed, or
executed on hardware.

## Prior phase-local FreeRTOS queue-message-count production map

The adjacent official accessors are now two complete generated entry
replacements:

| Official function | Stock range | Replacement |
|---|---|---|
| `uxQueueMessagesWaiting` | `[0x00441E66,0x00441E8A)`, 36 B | `B.W` plus 16 Thumb NOPs |
| `uxQueueMessagesWaitingFromISR` | `[0x00441E8A,0x00441EA2)`, 24 B | `B.W` plus 10 Thumb NOPs |

The appended source layout is:

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| task-context accessor | `[0x007B2858,0x007B288A)`, 50 B | `[0x007B2F74,0x007B2FA6)`, 50 B |
| generated alignment | `[0x007B288A,0x007B288C)`, 2 B | `[0x007B2FA6,0x007B2FA8)`, 2 B |
| ISR accessor | `[0x007B288C,0x007B28AE)`, 34 B | `[0x007B2FA8,0x007B2FCA)`, 34 B |

The task and ISR text hashes are
`fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04`
and
`38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c`.
Neither leaf has a text relocation. The six stock callers remain unchanged;
whole-component ingress contains only the two generated entry branches to
the new ranges and no branch or stored pointer to an interior address or the
alignment gap.

The Apple overlay is `[0x00794324,0x007B28AE)`, 124,298 bytes, SHA-256
`09c6c86c38a88905ea389eb9c2c860d6a2e559f435d225b02bb5bdc313e828d4`.
The Linux overlay is `[0x00794324,0x007B2FCA)`, 126,118 bytes, SHA-256
`db4f80dd7caa313de96580ce10050cba2ad07bc0b7495bbc3f122a29bf9dfefa`.
Their component/package size pairs are 3,647,694 / 4,426,148 and
3,649,514 / 4,427,968. The preceding console map is retained as a phase-local
pin. This map was assembled and checked offline; it was not signed, flashed,
or executed on hardware.

## Prior phase-local nanopb `pb_skip_varint` production map

The complete official function `[0x0048F628,0x0048F64C)` is now a generated
`B.W` plus sixteen-NOP source-entry replacement. The sole caller at
`0x0048F6B6` remains unchanged. The source leaf's one relocation binds stock
`pb_read` at `0x0048F3BE`; there is no local rodata or writable-data closure.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| generated alignment | `[0x007B28AE,0x007B28B0)`, 2 B | `[0x007B2FCA,0x007B2FCC)`, 2 B |
| `open_cfw_nanopb_skip_varint` | `[0x007B28B0,0x007B28D4)`, 36 B | `[0x007B2FCC,0x007B2FF0)`, 36 B |

The unrelocated text hashes to
`7e2f6a8b3dca56e4c2d0499a6d4f12ad97dc4bc7f127ff6f4c31b8d379f0ba3b`.
Apple relocated text hashes to
`d3a60ee83a801c7f7ae58b45d0a1e7b6d85fd920484f738ea5698b1196897df7`;
Linux relocated text hashes to
`09b1b218b4b222b284b44d433b5ae257e70c13b9cab13e7d53ca9168e7bcf27c`.
The profile-specific full-span patch hashes are
`ec17aa0a8e01050d8b30f737e7ca83d4b8842da1d7d33f6b3b74fa199a4f4519`
and
`f54c433a31f74f74b34709901da696d850b4dd2d0fb743b8166d49256c287303`.

The Apple overlay is `[0x00794324,0x007B28D4)`, 124,336 bytes, SHA-256
`97c57c110eb7b5fb7474bf945f35121432dfd713c02fcd47931da699c1da739a`.
The Linux overlay is `[0x00794324,0x007B2FF0)`, 126,156 bytes, SHA-256
`e7f3d94e8a7253f761c5d535dba918b765c9f3f2aba82a5cdc5372bd0ebf9d62`.
Their component/package size pairs are 3,647,732 / 4,426,186 and
3,649,552 / 4,428,006. Both remain below the conservative `0x007F0000`
ceiling. The preceding queue map is phase-local. This map was assembled and
checked offline; it was not signed, flashed, or executed on hardware.

## Preceding littlefs `lfs_file_size_` production map

The complete official private helper `[0x004CE472,0x004CE48A)` is now a
generated `B.W` plus ten-NOP source-entry replacement. Its two retained direct
callers remain at `0x004CE3E2` and `0x004CFC56`; no branch or stored pointer
enters an interior address. The bootloader has no matching helper and is not
patched.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| `open_cfw_littlefs_file_size_private` | `[0x007B28D4,0x007B28E8)`, 20 B | `[0x007B2FF0,0x007B3004)`, 20 B |

There is no intervening alignment region. The unrelocated text hashes to
`1edf2a8aae0009f5fca77cb8ba1430c2bfa7e52181c4620841450cbc2cbb3683`.
Apple and Linux relocated text hash respectively to
`d4cc044bcd8d14e246fe1626c70814ea2d37f47f32290852aa47efc460241a43`
and `74544bcbc851e0164d33575a42b8fe3d9270ff4fc25b056fd7dc743a7410fc72`.
The only relocation closes over the already source-owned
`open_cfw_littlefs_util_max`; no hardware or stock-binary dependency is added.

The Apple overlay is `[0x00794324,0x007B28E8)`, 124,356 bytes, SHA-256
`ab16010088fc71b58ed32c7bf28867900301bd92baa871a441f18fdf10ee0b1a`.
The Linux overlay is `[0x00794324,0x007B3004)`, 126,176 bytes, SHA-256
`45ddc376dc3943a1b2aaff981566cbd55a89197ddfe65ac368cedd6f607b4fd3`.
Their component/package size pairs are 3,647,752 / 4,426,206 and
3,649,572 / 4,428,026. Both remain below the conservative `0x007F0000`
ceiling. The preceding nanopb and queue maps are phase-local. This mapping was
assembled and checked offline and authorizes no G2 filesystem format or erase.

## Preceding FreeRTOS task-list initializer production map

The complete official Apollo-main `prvInitialiseTaskLists` span
`[0x0045568C,0x004556E0)` is now a generated `B.W` plus forty-NOP
source-entry replacement. Its sole caller is the unchanged `BL` at
`0x00454A20`. The source leaf initializes the recovered Apollo-main objects:

| Object | SRAM address |
|---|---:|
| `pxReadyTasksLists[56]` | `0x2006A49C` |
| delayed list 1 / delayed list 2 | `0x20073CFC` / `0x20073D10` |
| pending-ready / termination / suspended lists | `0x20073D24` / `0x20073D38` / `0x20073D4C` |
| delayed / overflow-delayed selector words | `0x20074A24` / `0x20074A28` |

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| `open_cfw_freertos_task_lists_initialize` | `[0x007B28E8,0x007B2940)`, 88 B | `[0x007B3004,0x007B305C)`, 88 B |

No alignment region precedes either leaf. The common unrelocated SHA-256 is
`6710533445c9aac3904152a43147d0e9ba9bec7eff8e7c5c6b72007c4c301fdb`;
Apple/Linux relocated hashes are
`22d2909d84e02d0216a71168fdac379a576317c22dd5de6f527fb595c4668b52`
and `dd4a36cadf6346d513ec039724a2a58309f443d31aad4e50858c5a64d95c04f6`.
All six call relocations bind to source-owned
`open_cfw_freertos_list_initialise`.

The Apple overlay is `[0x00794324,0x007B2940)`, 124,444 bytes, SHA-256
`34c6d23ea9e1c3f01440222e44fe2af38121a02309b61efb2b15a806e0e77158`.
The Linux overlay is `[0x00794324,0x007B305C)`, 126,264 bytes, SHA-256
`62d8e21bec02a7505a39296f2e474e703b6a3989c252c6cda3fda43e12e7d236`.
Their component/package size pairs are 3,647,840 / 4,426,294 and 3,649,660 /
4,428,114. Both remain below `0x007F0000`. The distinct bootloader homolog at
`[0x00418A44,0x00418A98)` and its separate SRAM map are unchanged.

## Preceding nanopb close-string-substream production map

The complete official nanopb-compatible body
`[0x0048F7CA,0x0048F7F4)` is 42 bytes with SHA-256
`439bbeecb6a0b8266dc3dcd913e98793352b6b346a7a58cdd44322c734621818`.
Its three retained direct callers are at `0x0048FA30`, `0x0048FBA2`, and
`0x00490524`. The body's only outgoing call is to stock `pb_read` at
`0x0048F3BE`; no alternate entry, interior transfer, or stored function
pointer enters the selected span. Production replaces all 42 bytes with one
profile-specific `B.W` and nineteen Thumb NOPs.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| `open_cfw_nanopb_close_string_substream` | offset 124,444, `[0x007B2940,0x007B2964)`, 36 B | offset 126,264, `[0x007B305C,0x007B3080)`, 36 B |
| complete overlay | `[0x00794324,0x007B2964)`, 124,480 B | `[0x00794324,0x007B3080)`, 126,300 B |

The shared unrelocated text hash is
`5e6ee5f441e5ba91e0e0147b8453a31186f3ce4bd0efc114edda60f00093a51e`.
Its sole `R_ARM_THM_CALL` at leaf offset 16 binds
`open_cfw_nanopb_read` to `0x0048F3BE`. After relocation, Apple hashes to
`c838be0dfb478fe7fa03d9d71069a200a6477eb5783b631d7d977cd501475438`
and Linux to
`a90a09f0f98c5b4cf7d885af34c914ae5d492ac7352b5e359ba68ad482cb3044`.
The Apple and Linux full-span patch hashes are
`1b395a30b511a1732cec3791c0c0e1306eac8b3a5c9fb2c1ce3f92e6eaca2255`
and
`bcffd3e5e32492e5c32143eac31bec47f2fabb91c8411a274eebd29e99f203f3`.

The Apple component/package sizes are 3,647,876 / 4,426,330 bytes; Linux's
are 3,649,696 / 4,428,150. Both appended overlays remain below the existing
`0x007F0000` ceiling. This map proves only the selected entry, ABI, callers,
and read seam; it does not classify the surrounding opaque application as
source-authenticated.

## Preceding littlefs private rewind production map

The official private rewind body occupies `[0x004CE460,0x004CE472)`, between
the source-owned private tell and size leaves. Its only outgoing call is from
offset six to retained private seek at `0x004CE3BC`; its only direct caller is
the public wrapper call at `0x004CFC28`. Production replaces all 18 stock
bytes with a profile-specific `B.W` and seven Thumb NOPs.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| `open_cfw_littlefs_file_rewind_private` | offset 124,480, `[0x007B2964,0x007B2974)`, 16 B | offset 126,300, `[0x007B3080,0x007B3090)`, 16 B |
| complete overlay | `[0x00794324,0x007B2974)`, 124,496 B | `[0x00794324,0x007B3090)`, 126,316 B |

The relocated leaf hashes are
`1c2e2b1fded0de515345b90fe34de51a9c0f08a02a5ad983c1120481c51c5783`
and `9731cbf3ff15be31186591ed148d009ae8985cb18bdfca3ba365aeb0897e3fd1`.
Apple component/package sizes are 3,647,892 / 4,426,346; Linux uses
3,649,712 / 4,428,166. Both overlays remain below `0x007F0000`.

## Preceding nanopb fixed32 production map

The official `pb_decode_fixed32` leaf is
`[0x00490190,0x004901AC)`, 28 bytes, SHA-256
`1ee27599a8ac5b8d2a0cbaac59986fb49be7b24c348a960a216b8cbbecce5bf3`.
Its sole direct caller at `0x0048F89C` remains unchanged. Production replaces
the complete stock span with one `B.W` and twelve Thumb NOPs; no interior stock
instruction remains executable.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| `open_cfw_nanopb_decode_fixed32` | offset 124,496, `[0x007B2974,0x007B29A6)`, 50 B | offset 126,316, `[0x007B3090,0x007B30C2)`, 50 B |
| complete overlay | `[0x00794324,0x007B29A6)`, 124,546 B | `[0x00794324,0x007B30C2)`, 126,366 B |

The unrelocated text hashes to
`798f8f7cbed57f6ba11dad46a6de9d25cb1f1710eb4fa904d79b6fe449952a04`.
Its single call relocation at leaf offset 10 resolves to stock `pb_read` at
`0x0048F3BE`; after relocation Apple hashes to
`c9fc88c025ec843fa3ad3f77b4e1bfb84126fd397a81d96c271646eb70632539`
and Linux to
`53a1961d2df94674da6890611087ab865498084ced6a6f0c6850dcee23c7bf60`.

The Apple and Linux full-span patch hashes are
`34c42ae60118f9f3546e0ef05a41f4ca68983fc81503e9915e7c4d9361f15616`
and
`d6c11f5f1a5b6f89f12e30c476f27daf0301a2d17d7ad9bafd5039d0aa970085`.
Their component/package sizes are 3,647,942 / 4,426,396 and
3,649,762 / 4,428,216. Both overlays remain below `0x007F0000`. This map
retains `pb_read` as opaque authenticated code and was not exercised on
hardware.

## Preceding littlefs tag-type production map

The official private `lfs_tag_type2` helper occupies
`[0x004CAE90,0x004CAE98)`, eight bytes, SHA-256
`a017094f8fc58d202d8c5a588f66dd319248578fa39e0f392ba3c7857d3500ef`.
Its two direct callers at `0x004CBB26` and `0x004CBC38` remain unchanged.
Production replaces the complete stock span with one profile-specific `B.W`
and two Thumb NOPs; no stock interior remains executable.

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| generated alignment | `[0x007B29A6,0x007B29A8)`, 2 B | `[0x007B30C2,0x007B30C4)`, 2 B |
| `open_cfw_littlefs_tag_type2` | offset 124,548, `[0x007B29A8,0x007B29B2)`, 10 B | offset 126,368, `[0x007B30C4,0x007B30CE)`, 10 B |
| complete overlay | `[0x00794324,0x007B29B2)`, 124,558 B | `[0x00794324,0x007B30CE)`, 126,378 B |

The common relocation-free text hashes to
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`.
The Apple and Linux full-span patch hashes are
`659991e787790e45f3c2b41575292709cf44eb4b6342c9f6ff4b735426d188df`
and
`84c933a2887b7027c2904be21d89be5ef671b3ec83f7f7160974aa8fe17dbd4d`.

The current artifact pins are:

| Profile | Overlay SHA-256 | Component SHA-256 | Package SHA-256 |
|---|---|---|---|
| Apple Clang 21.0.0 | `8dc6206e0a6ed458401de46e5fa60d0a7eebc152eab4032d087fc4e667f7f378` | `ec9f098bf69029862df63ff0929f6bbd9c345f540b3565b6cfc7cd71edbc36c4` | `f31bef6e0faf8e3655f5c92c385ebe6ee3e7f5ef5635401ceb05cf98089976fe` |
| exact-root Linux Clang 22.1.8 | `12ebf0aef9e1ce61c6f5f151515a8c4245b1b353ca921dcddfc6b521cf8f870a` | `eeaca07a2c4bec75f4652e9f2853a75ff45684584d5e6074d99d112a41e5ddfc` | `caa150eda201d91c8ec6046f5a9017ab87e7ee936fe0f542957bff4efdd4b37f` |

Apple component/package sizes are 3,647,954 / 4,426,408; Linux uses
3,649,774 / 4,428,228. Both overlays remain below `0x007F0000`. This
BSD-3-Clause scalar source replacement does not include a G2 block-device
port, reclassify the surrounding littlefs implementation, or authorize
filesystem format, erase, flashing, or hardware operation.

## Preceding dual-image littlefs tag-chunk map

The atomic `lfs_tag_chunk` promotion changes both Apollo images. The stock
leaves are byte-identical `000dc0b27047`, six bytes with SHA-256
`63fc572597119c756fa5d4ee0904c8c34dfa545495b77bba02e2ff3298ce23ae`:

| Image | Stock span | Generated patch semantics | Appended source span |
|---|---|---|---|
| Apollo main, Apple | `[0x004CAEA0,0x004CAEA6)` | `B.W 0x007B29B4` + one NOP (`e7f288bd00bf`) | `[0x007B29B4,0x007B29BA)`, after alignment `[0x007B29B2,0x007B29B4)` |
| Apollo main, exact-root Linux | `[0x004CAEA0,0x004CAEA6)` | profile-specific `B.W 0x007B30D0` + one NOP | `[0x007B30D0,0x007B30D6)`, after alignment `[0x007B30CE,0x007B30D0)` |
| Bootloader, Apple and Linux | `[0x00410BA8,0x00410BAE)` | profile-specific `B.W 0x004346E6` + one NOP | `[0x004346E6,0x004346EC)` |

The Apple main patch hashes to
`dc6ab8f21c612f18dc4453749e4243cb71f6eeb4ffa43203d4b649b6ec70b991`;
the Apple boot patch (`23f09dbd00bf`) hashes to
`9df9d5b78ff7bab718aa4c4a489da70591495fc77c6dc527eda633199fbd2b92`.
Every patch supersedes the complete stock body and preserves four direct
callers. The common six-byte source leaf hashes to
`db1dfda72afb267e96cd4e11eaf5d44659195b0afecbdcd8ed8572c34049df74`
and has no relocation or provider.

| Profile | Main overlay/component/package | Boot overlay/component |
|---|---|---|
| Apple Clang 21.0.0 | 124,566 / 3,647,962 / 4,426,422; hashes `0339a938dd13e8b89997cd6e75d7dc56e2300125039304f751b802af1dd73da8` / `ac8b3c62d32e849bfd1e71f4950f7ee58d02dc56dd8595c6706a453fe1cf402e` / `441bc7dd753518464afa0ac8ab84c26aedcd18228dbab3427d8c20ff66a8d914` | 628 / 149,228; hashes `10dce6ad20335a583b4ab2fad4b916ed335d65f126af06b77a935be9702149f6` / `ecfe0087fef4eab3a75f41a2db28d31b3e31c589fdaceec3c209e6e503eb295f` |
| exact-root Linux Clang 22.1.8 | 126,386 / 3,649,782 / 4,428,242; hashes `5ebdb04c602ff59241f9d376caa474180f1e9c90ba2ea05581e2b247528b814a` / `3ad0a8692694132ce30b266ae8ec4ffb66617de173cb1e3d96ee90335945c70d` / `8f62cf0ffb7d861ca1e6f9881e3221557f0da4640491489c7468129c5d57f1ba` | 628 / 149,228; hashes `e7619c604912ded4b5ac4513287bb68560bba2a09f84cda42dd9f1cf2d080a63` / `64d87f89085988da184b7cf3b9758e702093e35f0e4b2afb6da22971b8532f1b` |

The Apple overlay ends are `0x007B29BA` and `0x004346EC`; Linux main ends at
`0x007B30D6`. All remain within their reviewed flash bounds. The map records
offline source assembly only and does not authorize a G2 write, format,
erase, reset, boot, or hardware test.

## Preceding dual-image littlefs tag-validity/type1 map

The atomic promotion adds two complete entry replacements and two appended
source leaves to each Apollo image:

| Image/profile | Stock helper | Generated patch | Appended source span |
|---|---|---|---|
| Apollo main, Apple | `lfs_tag_isvalid` `[0x004CAE6A,0x004CAE74)` | `e7f2a7bd00bf00bf00bf` | `[0x007B29BC,0x007B29C2)`, after alignment `[0x007B29BA,0x007B29BC)` |
| Apollo main, Apple | `lfs_tag_type1` `[0x004CAE88,0x004CAE90)` | `e7f29cbd00bf00bf` | `[0x007B29C4,0x007B29CE)`, after alignment `[0x007B29C2,0x007B29C4)` |
| Apollo main, Linux | `lfs_tag_isvalid` `[0x004CAE6A,0x004CAE74)` | `e8f235b900bf00bf00bf` | `[0x007B30D8,0x007B30DE)`, after alignment `[0x007B30D6,0x007B30D8)` |
| Apollo main, Linux | `lfs_tag_type1` `[0x004CAE88,0x004CAE90)` | `e8f22abd00bf00bf` | `[0x007B30E0,0x007B30EA)`, after alignment `[0x007B30DE,0x007B30E0)` |
| Bootloader, both | `lfs_tag_isvalid` `[0x00410B72,0x00410B7C)` | `23f0bbbd00bf00bf00bf` | `[0x004346EC,0x004346F2)` |
| Bootloader, both | `lfs_tag_type1` `[0x00410B90,0x00410B98)` | `23f0afbd00bf00bf` | `[0x004346F2,0x004346FC)` |

The common validity/type1 source text hashes to
`65e477818b1c6002b2ceb88812da258524e438ded36dfa059e034c3bce19624e`
and `079f868da6ae04c0d4ace93e9e9d9132247224f81903b57fba51d407f49ddfcf`.
Both are provider- and relocation-free. Complete-image scans preserve the
three/eight direct caller sets per image and find no reviewed interior ingress.
The source authority is an authenticated littlefs v2.10.1 source-equivalent
baseline, not proof of the vendor's exact historical checkout.

## Preceding dual-image littlefs tag-type3 map

| Image/profile | Stock span | Complete generated patch | Appended source span |
|---|---|---|---|
| Apollo main, Apple | `[0x004CAE98,0x004CAEA0)` | `e7f29abd00bf00bf` | `[0x007B29D0,0x007B29D6)`, after alignment `[0x007B29CE,0x007B29D0)` |
| Apollo main, exact-root Linux | `[0x004CAE98,0x004CAEA0)` | `e8f228b900bf00bf` | `[0x007B30EC,0x007B30F2)`, after alignment `[0x007B30EA,0x007B30EC)` |
| Bootloader, both | `[0x00410BA0,0x00410BA8)` | `23f0acbd00bf00bf` | `[0x004346FC,0x00434702)` |

The common leaf is six bytes `c0f30a507047`, SHA-256
`a6781f0a92086cca25476ca00824d8f0fd736ac7d800aa9e3f6e4d6544490921`,
with no providers or relocations. The main/boot overlays end at
`0x007B29D6` / `0x00434702` for Apple and `0x007B30F2` / `0x00434702` for
Linux, within their reviewed bounds. Complete-image scans preserve 30/17
direct caller sets and find no reviewed interior ingress.

The map records deterministic offline source assembly only. It does not
authorize signing, flashing, filesystem mutation, reset, boot, or hardware
operation. At that preceding map milestone, `lfs_tag_size` and nanopb
`pb_decode_fixed64` was still awaiting a production address assignment at that
preceding milestone;
`lfs_tag_id` was promoted by the now-preceding map below. Tag-size is promoted
by the current map that follows it; nanopb fixed64 is promoted by the current
Apollo-main-only map at the end of this ledger.

| Profile | Main overlay/component/package | Boot overlay/component |
|---|---|---|
| Apple Clang 21.0.0 | 124,586 / 3,647,982 / 4,426,458; hashes `043dbfb45fcfb9707616c486ac2e736227f7186af8b25fc71a5e355a8e0ba79a` / `1227c4953bfcaeb62fb497b8a6911462a2d25fd3ed7b2bb88eea9dd3fdf13a18` / `f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23` | 644 / 149,244; hashes `959923a9b5253bd6409fedb82427b7ff666e2d52bc09ac5c391bc28bfbcc70c2` / `e8924fe19f6f768d01fa7c6ec111a4db5790eb28c423c5be84e09b0996423e20` |
| exact-root Linux Clang 22.1.8 | 126,406 / 3,649,802 / 4,428,278; hashes `7196c0d0d456b46e125b793d7ab4c6175768067589f4153d9b3ee997011c0314` / `a8684ae43a99cc692dd6cb95c8d4835cc138492d49bf9fd4a3689d32523913ef` / `07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc` | 644 / 149,244; hashes `078b88569f6adb147d3c12c727f29c5f3a6ddeb2f66de7d68122b4096f6ac794` / `6fff06068442ab3203d124c0adfd5052f216459642f67aa32cc39afffd2c0593` |

Apple main ends at `0x007B29CE`, Linux main at `0x007B30EA`, and boot at
`0x004346FC`, all within the reviewed flash bounds. This is an offline map and
assembly GO only; it does not authorize signing, flashing, reset, boot,
filesystem mutation, or hardware operation.

## Preceding dual-image littlefs tag-ID map

Both complete stock spans are now generated full-span entry replacements for
the same source-owned scalar leaf:

| Image/profile | Stock span | Complete generated patch | Appended source leaf |
|---|---|---|---|
| Apollo main, Apple | `[0x004CAEB0,0x004CAEB8)` | `e7f292bd00bf00bf` | offset `124,596`, `0x007B29D8` |
| Apollo main, exact-root Linux | `[0x004CAEB0,0x004CAEB8)` | `e8f220b900bf00bf` | offset `126,416`, `0x007B30F4` |
| Bootloader, Apple | `[0x00410BB8,0x00410BC0)` | `23f0a3bd00bf00bf` | offset `650`, `0x00434702` |
| Bootloader, exact-root Linux | `[0x00410BB8,0x00410BC0)` | `23f0a3bd00bf00bf` | offset `650`, `0x00434702` |

The official body is `800a8005800d7047`, SHA-256
`0843abb3e9ef39afac8e69ae1e181efa0b5b5c8ebf53e20844b53fdf245b1036`.
The common source text is `c0f389207047`, SHA-256
`6194594e24288e708887a0e938b2a54401c8c732210d91af7a5927d03bd3604c`,
with no providers or relocations. Complete-image scans preserve all 50/41
direct callers and find no reviewed interior ingress.

| Profile | Main overlay/component/package | Boot overlay/component |
|---|---|---|
| Apple Clang 21.0.0 | `124,602` / `3,647,998` / `4,426,486`; hashes `229ca8faff25bd61cd21152d828275f6e1dad9883eab359056482956ea166e98` / `8dddb1f59da1319dc15815ded6258f966a6fd08d6ed7edc134122de5bca2fff6` / `bfa8629a4c182e7448b4b6d89f875cd99f7e105876f12e4d2904d755cafc69f1` | `656` / `149,256`; hashes `432f0c91a6db142a951db076fc89a4a80e740675d63f62263f45c21e37777ad3` / `6d96308ea4e5851ab137831d6da991184b6611551a01fa18e4cef3f1877f4694` |
| exact-root Linux Clang 22.1.8 | `126,422` / `3,649,818` / `4,428,306`; hashes `fcf2783a5a73474fb87cdd22cc592a12056b6a4d4080e7f8ca6120b88d82ebaa` / `40d16ee5833eae6ae3229d82fcd583fd2c3ba9fe6234978d503a57c0d88ffeff` / `727354ce585843f11fabec93884640fdf58c71b251f5b7067ee4c0703cb53fcd` | `656` / `149,256`; hashes `4cadbf422b57b1905b38df77ab0d24932839aa28f883f57e56a09183d577edb8` / `a3ca91bb744c777d7d98d8b34a044e613ad251a972d6e6d54a8a48b959795ad2` |

The final Apple main/boot overlays end at `0x007B29DE` / `0x00434708`;
exact-root Linux ends at `0x007B30FA` / `0x00434708`. This pure scalar map
introduces no
block-device, mount, format, program, or erase path and authorizes no signing,
flashing, filesystem mutation, reset, boot, or hardware operation.

## Preceding dual-image littlefs tag-size map

The production full-span entry replacements are fixed at the official stock
boundaries, with final appended source placement:

| Image/profile | Stock span | Complete generated patch | Appended source leaf |
|---|---|---|---|
| Apollo main, Apple | `[0x004CAEB8,0x004CAEBE)` | `e7f292bd00bf` | offset `124604`, address `0x007B29E0` |
| Apollo main, exact-root Linux | `[0x004CAEB8,0x004CAEBE)` | `e8f220b900bf` | offset `126424`, address `0x007B30FC` |
| Bootloader, Apple | `[0x00410BC0,0x00410BC6)` | `23f0a2bd00bf` | offset `656`, address `0x00434708` |
| Bootloader, exact-root Linux | `[0x00410BC0,0x00410BC6)` | `23f0a2bd00bf` | offset `656`, address `0x00434708` |

Both stock bodies are `8005800d7047`, SHA-256
`8596106584e598a657aea7fdd2e1156a748158d2d63d9c121c92587fabbdf8ca`.
The authenticated littlefs v2.10.1 source at `lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`, implements only
`tag & 0x000003ff`; Apple production text is `6ff39f207047`, SHA-256
`35890ebcdee5cb7f51b3e8d874201b7e0214f6111eebe56c772133f259cf9b54`,
with no providers or relocations. Complete-image scans close 15/14 callers.

Final main/boot overlay ends and component/package identities are closed in
the explicit root and evidence ledgers. The tag-ID map above is the settled
preceding production map. This scalar promotion adds no block-device, mount,
format, program, or erase path
and authorizes no signing, flashing, filesystem mutation, reset, boot, or
hardware operation.

## Preceding Apollo-main nanopb fixed64 map

| Profile | Official replacement | Appended source leaf | Retained provider |
|---|---|---|---|
| Apple Clang 21.0.0 | `[0x004901AC,0x004901CC)`: `22f31cbc` + fourteen `00bf` | offset `124612`, `[0x007B29E8,0x007B2A04)` after `[0x007B29E6,0x007B29E8)` alignment | `pb_read` at `0x0048F3BE` |
| exact-root Linux Clang 22.1.8 | `[0x004901AC,0x004901CC)`: `22f3aabf` + fourteen `00bf` | offset `126432`, `[0x007B3104,0x007B3122)` after `[0x007B3102,0x007B3104)` alignment | `pb_read` at `0x0048F3BE` |

The stock span is exactly 32 bytes, hashes to
`96228dfbdfe30665d79281ba0fd5ba3b3af38701396671cd20b77623ffd82d54`,
has one external caller at `0x0048F8C6`, and has no reviewed interior ingress
or stored pointer. The source leaf's only relocation resolves to the retained
provider. The bootloader load range `[0x00410000,0x00434477)` has no
authenticated homolog, so its map and overlay remain unchanged. At that
milestone the main overlay ends were `0x007B2A04` and `0x007B3122`, inside the
conservative Apollo MRAM ceiling.

## Preceding Apollo-main nanopb `pb_read` map

| Profile | Official replacement | Appended source leaf | Retained binary seams |
|---|---|---|---|
| Apple Clang 21.0.0 | `[0x0048F3BE,0x0048F454)`: `23f321bb` + 73 `00bf`; SHA `c2c44419ee24c41c8d0e8bc7f04689bb7f1c18b1f7ec3d7304e04c37579938a1` | offset `124640`, `[0x007B2A04,0x007B2AA2)` | `buf_read` identity `0x0048F3A5`; strings `0x00787C70`, `0x0078B690` |
| exact-root Linux Clang 22.1.8 | `[0x0048F3BE,0x0048F454)`: `23f3b1be` + 73 `00bf`; SHA `4dc433588344c12d1a0abfab8c5f1673c24f6702d8f285f67fb0fd8b8e6e3eab` | offset `126464`, `[0x007B3124,0x007B31C2)`, after alignment `[0x007B3122,0x007B3124)` | same three fixed seams |

The official 150-byte body hashes to
`69aecb900c749fd98bd2d05e2229e9a3d6829bd36f3e393f624e3579a9b4af7f`.
Its 13 external direct callers remain at their stock ABI call sites, while two
recursive calls are internal to the replaced body. No external interior branch
or stored pointer was found. The 158-byte relocated leaf hashes to
`8b3de44a2cf7ca2e07715c913db0fa454ef65cbc453366190b12736e455aa7a8`.
At that milestone the main overlay ended at `0x007B2AA2` on Apple and
`0x007B31C2` on Linux, both below the conservative Apollo MRAM ceiling. The
bootloader contained no authenticated `pb_read`/`buf_read` homolog or matching
error-string closure. Those endpoints belong to the preceding `pb_read`
milestone. The following constructor map superseded them, and the subsequent
signed-varint map records the current Apple boundary. This map is an offline assembly
description and is not authorization to write either image to hardware.

## Preceding Apollo-main nanopb stream-constructor map

| Profile | Official replacement | Appended constructor leaf | Preceding overlay end |
|---|---|---|---|
| Apple Clang 21.0.0 | `[0x0048F49C,0x0048F4B8)`: `23f332bb` + twelve `00bf` | offset `124896`, `[0x007B2B04,0x007B2B18)` | `0x007B2B18` (`124916` bytes) |
| exact-root Linux Clang 22.1.8 | `[0x0048F49C,0x0048F4B8)`: `23f3c2be` + twelve `00bf` | offset `126720`, `[0x007B3224,0x007B323A)` | `0x007B323A` (`126742` bytes) |

At that preceding milestone, the Apple package was 4,426,806 bytes with exact
source/generated/opaque ownership `125709 / 88436 / 4212661`. The exact-root
Linux package was 4,428,632 bytes with ownership
`127623 / 88196 / 4212813`. Their package SHA-256 values are
`062eaf5a7f301022f97162f4517d15248276e80c11a27b7c9f9b0e4cda4fbef2`
and `c9f09923a8c97706f32aed0c0c7db455a9aed01eff06d968cf8be81ee552793f`.
All 30 callers retained the official constructor entry, and both leaves preserved
callback identity `0x0048F3A5`. Full qualification is in
`docs/research/nanopb-istream-from-buffer-source-audit.md`; this remains an
offline map and authorizes no hardware operation.

## Preceding Apollo-main nanopb signed-varint map

| Region | Apple Clang 21.0.0 | exact-root Linux Clang 22.1.8 |
|---|---|---|
| Official predecessor | `[0x0048F7F4,0x00490150)`, 2,396 B | same authenticated stock span |
| Generated `pb_decode_svarint` replacement | component offset 360,816, `[0x00490150,0x00490190)`, 64 B | same component offset and span |
| Official successor | begins `0x00490190` without a gap | same boundary |
| `open_cfw_nanopb_decode_svarint` | overlay offset 124,916 / component offset 3,648,312, `[0x007B2B18,0x007B2B4E)`, 54 B | overlay offset 126,744 / component offset 3,650,140, `[0x007B323C,0x007B326E)`, 50 B |

The leaf's only relocation is `+0x08 R_ARM_THM_CALL` to
`open_cfw_nanopb_decode_varint`, resolved source-to-source. The complete entry
replacement hashes to
`e8c5601b86e9a38362fb292b0a8ba70250d2ccc3094d0c8c117b1c33f5bf11cc`.
The Linux entry replacement hashes to
`e6bb4ee4baec73757a5f465cf99a32e787fb25bd651b2b16e2e76fda4c6d18fd`.
The canonical Apple manifest contains 951 Apollo-main regions; the alternate
Linux flash plan preserves the fixed-address partition and coarsens the
profile-owned appended tail, yielding 846 placed regions.

## Preceding Apollo-main nanopb varint32-pair map

| Region | Apple Clang 21.0.0 |
|---|---|
| Private stock patch | file offset 357,592, `[0x0048F4B8,0x0048F5AE)`, 246 B |
| Public stock patch | file offset 357,838, `[0x0048F5AE,0x0048F5B8)`, 10 B |
| Private alignment/text | component offsets 3,648,366/3,648,368; `[0x007B2B4E,0x007B2C2E)`, 2+222 B |
| Overflow rodata | component offset 3,648,590, `[0x007B2C2E,0x007B2C3E)`, 16 B |
| Public alignment/text | component offsets 3,648,606/3,648,608; `[0x007B2C3E,0x007B2C4A)`, 2+10 B |

The overlay closes at 125,222 bytes and the component at 3,648,618 bytes.
All source calls bind directly to other source-owned nanopb leaves. Exact-root
Linux maps private text at `0x007B3270`, its literal at `0x007B334E`, and the
public wrapper at `0x007B3360`; the overlay ends at `0x007B336A`. This offline
map authorizes no hardware operation.

## Preceding Apollo-main nanopb skip-string map

| Region | Apple Clang 21.0.0 | Linux Clang 22.1.8 |
|---|---|---|
| Stock replacement | `[0x0048F64C,0x0048F66C)`, 32 B | same fixed address |
| Alignment | `[0x007B2C4A,0x007B2C4C)`, 2 B | `[0x007B336A,0x007B336C)`, 2 B |
| Source leaf | `[0x007B2C4C,0x007B2C6E)`, 34 B | `[0x007B336C,0x007B338E)`, 34 B |

The leaf closes only over source-owned varint32/read providers. The 960-region
manifest and both profiles at that milestone are offline build evidence, not
hardware authorization.

## Current Apollo-main nanopb skip-field map

| Region | Apple Clang 21.0.0 | Reconstruction state |
|---|---|---|
| Stock replacement | `[0x0048F6A0,0x0048F6EA)`, 74 B | Generated full-span `B.W` plus Thumb NOP fill; fully recreated routing |
| `read_raw_value` stock entry | `[0x0048F6EA,0x0048F77E)`, 148 B | Generated full-span `B.W` plus Thumb NOP fill; fully recreated routing |
| `pb_make_string_substream` | `[0x0048F77E,0x0048F7CA)`, 76 B | Upstream-identified, fully boundary-audited, still opaque/cut-forward; retained memcpy seam |
| Alignment | `[0x007B2C6E,0x007B2C70)`, 2 B | Generated |
| Source text | `[0x007B2C70,0x007B2CB2)`, 66 B | Fully recreated from bounded Zlib-licensed source |
| Source rodata | `[0x007B2CB2,0x007B2CC4)`, 18 B | Fully recreated diagnostic closure |

Rizin and the fail-closed analyzer pin the two callers, complete wire-type
switch, and four calls to source-owned `pb_skip_varint`, `pb_read`, and
`pb_skip_string`. The reviewed Linux/Clang 22 placement remains opaque as a
build result—not as firmware bytes—until that exact compiler is available.
See `docs/research/nanopb-skip-field-source-candidate-audit.md`.

The following substream helper is pinned in
`docs/research/nanopb-raw-substream-boundary-audit.md`; identification does not
yet reclassify its bytes as source-recreated.

## Current Apollo-main nanopb raw-value map

| Region | Apple Clang 21.0.0 | Reconstruction state |
|---|---|---|
| Stock replacement | `[0x0048F6EA,0x0048F77E)`, 148 B | Generated full-span `B.W` plus Thumb NOP fill; fully recreated routing |
| `pb_make_string_substream` stock entry | `[0x0048F77E,0x0048F7CA)`, 76 B | Generated full-span redirect; fully recreated routing |
| Source text | `[0x007B2CC4,0x007B2D4A)`, 134 B | Fully recreated from bounded Zlib-licensed source |
| Source rodata | `[0x007B2D4A,0x007B2D6C)`, 34 B | Fully recreated diagnostic closure |

The source leaf has one direct call and one tail jump to source-owned
`open_cfw_nanopb_read`; its remaining four relocations address the local
diagnostic block. The reviewed Linux/Clang 22 placement remains pending until
that exact compiler is available and is not inferred from Apple output.

## Current Apollo-main nanopb make-string-substream map

| Region | Apple Clang 21.0.0 | Reconstruction state |
|---|---|---|
| Stock replacement | `[0x0048F77E,0x0048F7CA)`, 76 B | Generated full-span redirect and NOP fill |
| Source text | `[0x007B2D6C,0x007B2DB4)`, 72 B | Fully recreated; source-owned varint32 provider and explicit stream-field copy |
| Source rodata | `[0x007B2DB4,0x007B2DCC)`, 24 B | Fully recreated diagnostic closure |

No compiler-runtime copy provider remains in the source closure. Linux/Clang
22 placement remains pending and is not inferred from Apple output.

## Current Apollo-main nanopb Boolean decoder-pair map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Public stock entry | `[0x0049012C,0x00490150)` | 36 | Fully recreated routing: `B.W` plus complete NOP fill |
| Private adapter stock entry | `[0x004901CC,0x004901D6)` | 10 | Fully recreated routing: `B.W` plus complete NOP fill |
| Public source leaf | `[0x007B2DCC,0x007B2DE8)` | 28 | Fully recreated from bounded Zlib source; call to source-owned varint32 |
| Private adapter source leaf | `[0x007B2DE8,0x007B2DEE)` | 6 | Fully recreated from bounded Zlib source; tail-call to public Boolean leaf |
| Following `pb_dec_varint` stock entry | `[0x004901D6,0x00490352)` | 380 | Fully recreated routing: `B.W` plus complete NOP fill |

The overlay now ends at `0x007B2DEE`, remains inside the conservative Apollo
MRAM ceiling, and adds no data segment or alignment span. Exact-root Linux
placement remains pending and is not inferred from Apple output.

## Current Apollo-main nanopb private field-varint map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `pb_dec_varint` entry | `[0x004901D6,0x00490352)` | 380 | Fully recreated routing: `B.W` plus complete NOP fill |
| Preserved boundary literal island | `[0x00490352,0x00490358)` | 6 | Opaque/cut-forward; separately hash-pinned |
| Source alignment | `[0x007B2DEE,0x007B2DF0)` | 2 | Generated zero fill |
| Source text | `[0x007B2DF0,0x007B2F20)` | 304 | Fully recreated from bounded Zlib source; all provider calls source-owned |
| Source diagnostic data | `[0x007B2F20,0x007B2F44)` | 36 | Fully recreated local `invalid data_size` and `integer too large` strings |

The overlay now ends at `0x007B2F44`, below the conservative Apollo MRAM
ceiling. Exact-root Linux placement remains pending and is not inferred from
Apple output.

## Current Apollo-main nanopb private bytes-field map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `pb_dec_bytes` entry | `[0x00490358,0x004903EA)` | 146 | Fully recreated routing: `B.W` plus complete NOP fill |
| Following stock `pb_dec_string` | `[0x004903EA,0x00490488)` | 158 | Opaque/cut-forward; next contiguous nanopb frontier |
| Source text | `[0x007B2F44,0x007B2FA6)` | 98 | Fully recreated from bounded Zlib source; both provider calls source-owned |
| Source diagnostic data | `[0x007B2FA6,0x007B2FD6)` | 48 | Fully recreated local `bytes overflow`, `size too large`, and `no malloc support` strings |

The overlay now ends at `0x007B2FD6`, below the conservative Apollo MRAM
ceiling. The stock literal island `[0x00490352,0x00490358)` remains an opaque,
separately pinned six-byte segment. Exact-root Linux placement remains pending
and is not inferred from Apple output.

## Current Apollo-main nanopb private string-field map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `pb_dec_string` entry | `[0x004903EA,0x00490488)` | 158 | Fully recreated routing: `B.W` plus complete NOP fill |
| Successor literal island | `[0x00490488,0x0049048C)` | 4 | Opaque/cut-forward; separately hash-pinned |
| Following `pb_dec_submessage` | `[0x0049048C,0x00490538)` | 172 | Source-replaced with one pinned stock decoder seam; detailed in the following map |
| Source alignment | `[0x007B2FD6,0x007B2FD8)` | 2 | Generated zero fill |
| Source text | `[0x007B2FD8,0x007B304A)` | 114 | Fully recreated from bounded Zlib source; both provider calls source-owned |
| Source diagnostic data | `[0x007B304A,0x007B307B)` | 49 | Fully recreated local size, allocation, and string-overflow diagnostics |

The overlay now ends at `0x007B307B`, below the conservative Apollo MRAM
ceiling. Exact-root Linux placement remains pending and is not inferred from
Apple output.

## Current Apollo-main nanopb private submessage map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `pb_dec_submessage` entry | `[0x0049048C,0x00490538)` | 172 | Recreated routing: `B.W` plus full NOP fill; replacement retains pinned stock `pb_decode_inner` seam |
| Successor literal island | `[0x00490538,0x0049053C)` | 4 | Opaque/cut-forward; separately hash-pinned |
| Following `pb_dec_fixed_length_bytes` | `[0x0049053C,0x004905A8)` | 108 | Opaque/cut-forward; next contiguous stock leaf after the retained decoder dependency |
| Source alignment | `[0x007B307B,0x007B307C)` | 1 | Generated zero fill |
| Source text | `[0x007B307C,0x007B3106)` | 138 | Recreated from bounded Zlib source; make/close helpers source-owned, `pb_decode_inner -> 0x0048FE98` still stock |
| Source diagnostic data | `[0x007B3106,0x007B311F)` | 25 | Fully recreated local `invalid field descriptor` string |

The indirect callback at stock `0x004904E4` is a schema/application callback
ABI seam rather than a fixed firmware target. The overlay now ends at
`0x007B311F`, below the conservative Apollo MRAM ceiling. Exact-root Linux
placement and hardware execution remain pending.

## Current Apollo-main nanopb private decoder-loop map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `pb_decode_inner` | `[0x0048FE98,0x00490112)` | 634 | Fully recreated routing: guarded `B.W` plus complete Thumb NOP fill |
| Successor literal island | `[0x00490112,0x00490120)` | 14 | Opaque/cut-forward; hash-pinned |
| Public `pb_decode` wrapper | `[0x00490120,0x0049012C)` | 12 | Identified wrapper; opaque/cut-forward |
| Source alignment | `[0x007B311F,0x007B3120)` | 1 | Generated zero fill |
| Source text | `[0x007B3120,0x007B3332)` | 530 | Recreated from pinned nanopb source; six stock calls across five helper families remain |
| Source diagnostic data | `[0x007B3332,0x007B338A)` | 88 | Fully recreated defaults, zero-tag, fixed-count, and required-field strings |

The source body directly uses the source-owned `pb_skip_field` leaf and removes
the stock memory-fill helper. Its remaining stock calls are pinned at
`0x004D9384`, `0x0048FDF2`, `0x004D93F8`, `0x004D946E`, `0x0048FC88`,
and `0x0048FBE4`; tag and skip providers are source-owned. The overlay remains below the conservative
Apollo MRAM ceiling. Linux placement and hardware execution remain pending.

## Current Apollo-main nanopb tag-decoder map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `pb_decode_tag` | `[0x0048F66C,0x0048F6A0)` | 52 | Fully recreated routing: guarded `B.W` plus complete Thumb NOP fill |
| Source alignment | `[0x007B338A,0x007B338C)` | 2 | Generated zero fill |
| Source text | `[0x007B338C,0x007B33B6)` | 42 | Fully recreated from pinned nanopb source; varint32/eof provider source-owned |

Stock byte stores at `0x0048F674`, `0x0048F678`, and `0x0048F69A` establish
the one-byte wire-type ABI. No data, callback, heap, or hardware seam remains.

## Current Apollo-main nanopb message-defaults candidate map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| `pb_field_set_to_default` | `[0x0048FCE2,0x0048FDF2)` | 272 | Fully recreated; generated full-span redirect to 256 source bytes at `0x007B38CC` |
| `pb_message_set_to_defaults` | `[0x0048FDF2,0x0048FE98)` | 166 | Fully recreated; generated full-span redirect to 158 source bytes at `0x007B382C` |
| `pb_decode_inner` | `[0x0048FE98,0x00490112)` | 634 | Fully recreated routing to the source leaf described above |

The defaults body has no interior or stored-pointer ingress. Its four callers
and seven outgoing calls are authenticated. Stream, tag, iterator, and paired
default calls now resolve to source; `decode_field @ 0x0048FBE4` is the sole
fixed stock executable seam.

The field-default body has one direct caller, five outgoing calls, and no
alternate/interior/stored-pointer ingress. The paired source internalizes the
three defaults cross-calls, locally eliminates memory fill, and binds the three
iterator operations to their source leaves. A two-byte alignment span occupies
`[0x007B38CA,0x007B38CC)`.

## Current Apollo-main nanopb iterator-cluster production map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Predecessor literal/data island | `[0x004D910A,0x004D914C)` | 66 | Opaque data; hash-pinned, including one classified false branch decode |
| Predecessor shift helper | `[0x004D914C,0x004D916E)` | 34 | Separate non-nanopb helper; opaque/cut-forward |
| `load_descriptor_values` | `[0x004D916E,0x004D930A)` | 412 | Fully recreated; stock private body unreachable/opaque, source provider at `0x007B33B8` |
| `advance_iterator` | `[0x004D930A,0x004D9384)` | 122 | Fully recreated/inlined; stock private body unreachable/opaque |
| `pb_field_iter_begin` | `[0x004D9384,0x004D93A4)` | 32 | Generated full-span redirect to source at `0x007B34A8` |
| `pb_field_iter_begin_extension` | `[0x004D93A4,0x004D93D8)` | 52 | Generated full-span redirect to source at `0x007B3504` |
| `pb_field_iter_next` | `[0x004D93D8,0x004D93F8)` | 32 | Generated full-span redirect to source at `0x007B3584` |
| `pb_field_iter_find` | `[0x004D93F8,0x004D946E)` | 118 | Generated full-span redirect to source at `0x007B35E4` |
| `pb_field_iter_find_extension` | `[0x004D946E,0x004D94B8)` | 74 | Generated full-span redirect to source at `0x007B3690` |
| `pb_const_cast` | `[0x004D94B8,0x004D94BA)` | 2 | Fully recreated/inlined; stock private body unreachable/opaque |
| `pb_field_iter_begin_const` | `[0x004D94BA,0x004D94D2)` | 24 | Generated full-span redirect to source at `0x007B371C` |
| `pb_field_iter_begin_extension_const` | `[0x004D94D2,0x004D94E6)` | 20 | Generated full-span redirect to source at `0x007B3778` |
| `pb_default_field_callback` | `[0x004D94E6,0x004D9522)` | 60 | Generated full-span redirect to source at `0x007B37F8`; stored Thumb pointer at `0x004910BC` lands on redirect |
| Successor TinyFrame wrapper | `[0x004D9522,0x004D9530)` | 14 | Separate identified component boundary; opaque/cut-forward |

The live cluster is production-integrated through 1,132 source bytes, 10 bytes
of alignment, and 412 bytes of generated entry replacement. The 536 stock
private-helper bytes are unreachable but remain opaque ownership. The source
closure contains no retained fixed stock executable or stock-data seam; the
two default-callback `BLX` sites remain dynamic application/schema ABI
dispatches.

## Current Apollo-main nanopb dispatch and extension map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `decode_field` | `[0x0048FBE4,0x0048FC26)` | 66 | Fully recreated; guarded full-span redirect |
| Stock `default_extension_decoder` | `[0x0048FC26,0x0048FC78)` | 82 | Fully recreated; guarded full-span redirect |
| Stock literal island | `[0x0048FC78,0x0048FC88)` | 16 | Bounded and hash-pinned; opaque/cut-forward |
| Stock `decode_extension` | `[0x0048FC88,0x0048FCE2)` | 90 | Fully recreated; guarded full-span redirect |
| `decode_field` source closure | `[0x007B39CC,0x007B3A13)` | 71 | 52 text + 19-byte source diagnostic |
| Alignment | `[0x007B3A13,0x007B3A14)` | 1 | Generated zero padding |
| Default-extension source closure | `[0x007B3A14,0x007B3A70)` | 92 | 74 text + 18-byte source diagnostic |
| `decode_extension` source leaf | `[0x007B3A70,0x007B3AC0)` | 80 | Fully recreated; dynamic callback ABI retained |

The overlay now ends at `0x007B3AC0`. Relocated `pb_decode_inner` binds
directly to `decode_field @ 0x007B39CC` and `decode_extension @ 0x007B3A70`;
the defaults closure also binds the source dispatcher. The successor
field-decoder cluster is production-integrated in the map below.

## Current Apollo-main nanopb field-decoder production map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `decode_basic_field` | `[0x0048F7F4,0x0048F968)` | 372 | Fully recreated; guarded full-span redirect |
| Stock `decode_static_field` | `[0x0048F968,0x0048FB1C)` | 436 | Fully recreated; guarded full-span redirect |
| Stock no-malloc `decode_pointer_field` | `[0x0048FB1C,0x0048FB30)` | 20 | Fully recreated; guarded full-span redirect |
| Stock `decode_callback_field` | `[0x0048FB30,0x0048FBE4)` | 180 | Fully recreated; guarded full-span redirect; two dynamic callback ABI sites |
| Stock `pb_dec_fixed_length_bytes` | `[0x0049053C,0x004905A8)` | 108 | Fully recreated; guarded full-span redirect |
| Fixed-length source closure | `[0x007B3AC0,0x007B3B9B)` | 219 | 170 text + 49 diagnostic bytes |
| Basic alignment | `[0x007B3B9B,0x007B3B9C)` | 1 | Generated zero padding |
| Basic source closure | `[0x007B3B9C,0x007B3C91)` | 245 | 210 text + 35 diagnostic bytes |
| Static alignment | `[0x007B3C91,0x007B3C94)` | 3 | Generated zero padding |
| Static source closure | `[0x007B3C94,0x007B3E52)` | 446 | 408 text + 38 diagnostic bytes |
| Pointer alignment | `[0x007B3E52,0x007B3E54)` | 2 | Generated zero padding |
| Pointer source closure | `[0x007B3E54,0x007B3E7E)` | 42 | 24 text + 18 diagnostic bytes |
| Callback alignment | `[0x007B3E7E,0x007B3E80)` | 2 | Generated zero padding |
| Callback source closure | `[0x007B3E80,0x007B3F34)` | 180 | 164 text + 16 diagnostic bytes |

The overlay now ends at `0x007B3F34`. The complete field-decoder unit has no
fixed stock executable seam; every fixed relocation resolves to a separately
reviewed source-owned nanopb provider. The two indirect callback dispatches
are schema/application ABI, not opaque firmware functions. Linux placement
and hardware execution remain pending.

## Current Apollo-main ring-buffer production map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `ring_buffer_is_empty` | `[0x00598134,0x00598146)` | 18 | Fully reverse engineered/recreated; generated entry redirect |
| Stock `ring_buffer_is_full` | `[0x00598146,0x00598160)` | 26 | Fully reverse engineered/recreated; generated entry redirect |
| Stock `ring_buffer_init` | `[0x00598160,0x0059818C)` | 44 | Fully reverse engineered/recreated; generated entry redirect |
| Stock init literals/alignment | `[0x0059818C,0x00598198)` | 12 | Fully classified; retained stock data |
| Stock `ring_buffer_queue` | `[0x00598198,0x005981C4)` | 44 | Fully reverse engineered/recreated; generated entry redirect |
| Stock `ring_buffer_queue_arr` | `[0x005981C4,0x005981E0)` | 28 | Fully reverse engineered/recreated; generated entry redirect |
| Stock `ring_buffer_dequeue` | `[0x005981E0,0x0059820A)` | 42 | Fully reverse engineered/recreated; generated entry redirect |
| Stock `ring_buffer_dequeue_arr` | `[0x0059820A,0x0059823C)` | 50 | Fully reverse engineered/recreated; generated entry redirect |
| Source `is_empty` | `[0x007B3F34,0x007B3F42)` | 14 | Source compiled |
| Full alignment | `[0x007B3F42,0x007B3F44)` | 2 | Generated alignment |
| Source `is_full` | `[0x007B3F44,0x007B3F56)` | 18 | Source compiled |
| Init alignment | `[0x007B3F56,0x007B3F58)` | 2 | Generated alignment |
| Source `init` | `[0x007B3F58,0x007B3F8C)` | 52 | Source compiled; fixed assertion seam |
| Source `queue` | `[0x007B3F8C,0x007B3FB4)` | 40 | Source compiled |
| Source `queue_arr` | `[0x007B3FB4,0x007B3FD8)` | 36 | Source compiled |
| Source `dequeue` | `[0x007B3FD8,0x007B4000)` | 40 | Source compiled |
| Source `dequeue_arr` | `[0x007B4000,0x007B4030)` | 48 | Source compiled |

The ring-buffer tranche ends at `0x007B4030`. All seven live stock entries are
recreated; no ring-buffer executable byte remains opaque. The retained
12-byte literal island is classified stock data. Two additional alignment
bytes lie inside the redirected callable spans, so the full 264-byte cluster
still classifies as 250 instruction bytes plus 14 alignment/literal bytes.
Linux placement is independently pinned and twice replayed; hardware execution remains pending.

## Current IAR void-EABI memory-provider production map

| Segment | Canonical Apple range | Linux range | Bytes | State |
|---|---:|---:|---:|---|
| Stock `memmove` | `[0x00439710,0x004397A6)` | same | 150 | Fully reverse engineered/recreated; generated redirect |
| Stock public `memcpy` prefix | `[0x00439BE4,0x00439C04)` | same | 32 | Fully reverse engineered/recreated; generated redirect |
| Stock aligned `memcpy` entry | `[0x00439C04,0x00439C8A)` | same | 134 | Fully reverse engineered/recreated; generated redirect |
| Source arbitrary-alignment `memcpy` | `[0x007B4030,0x007B40C8)` | `[0x007B477C,0x007B4814)` | 152 | Source compiled; relocation-free |
| Source aligned-entry `memcpy` | `[0x007B40C8,0x007B4160)` | `[0x007B4814,0x007B48AC)` | 152 | Source compiled; relocation-free |
| Source overlap-safe `memmove` | `[0x007B4160,0x007B42A2)` | `[0x007B48AC,0x007B49EE)` | 322 | Source compiled; relocation-free |

At this historical memory-provider milestone, the canonical overlay ended at
`0x007B42A2` and the Linux overlay at `0x007B49EE`. The subsequent section
records the now-integrated math/errno quartet. Both toolchain layouts are
fail-closed, while hardware timing remains deferred.

## Current IAR hard-float math/errno production map

| Segment | Canonical Apple range | Linux range | Bytes | State |
|---|---:|---:|---:|---|
| Stock `sqrtf` | `[0x004397A8,0x004397C4)` | same | 28 | Fully reverse engineered/recreated; generated redirect |
| Stock EDOM setter | `[0x00439CA4,0x00439CB2)` | same | 14 | Fully reverse engineered/recreated; generated redirect |
| Stock ERANGE setter | `[0x00439CB2,0x00439CC4)` | same | 18 | Fully reverse engineered/recreated; generated redirect |
| Stock errno-address accessor | `[0x00439CC4,0x00439CD0)` | same | 12 | Fully reverse engineered/recreated; generated redirect |
| Errno literals/alignment | `[0x00439CD0,0x00439CE0)` | same | 16 | Fully classified official data; retained, non-executable |
| Source EDOM setter | `[0x007B42A2,0x007B42B6)` | `[0x007B49EE,0x007B4A02)` | 20 | Source compiled; relocation-free |
| Source `sqrtf` | `[0x007B42B6,0x007B42D2)` | `[0x007B4A02,0x007B4A1E)` | 28 | Source compiled; tail relocation to source EDOM setter |
| Source ERANGE setter | `[0x007B42D2,0x007B42E6)` | `[0x007B4A1E,0x007B4A32)` | 20 | Source compiled; relocation-free |
| Source errno-address accessor | `[0x007B42E6,0x007B42F0)` | `[0x007B4A32,0x007B4A3C)` | 10 | Source compiled; relocation-free |

The Apple overlay now ends at `0x007B42F0`; Linux ends at `0x007B4A3C`.
Every executable segment in the bounded ten-unit IAR census is fully recreated
and redirected. The 16-byte literal island remains explicitly classified data,
not opaque executable code. Exact EWARM release/archive provenance and hardware
execution remain open.

## Cordio SMP-main stock and SRAM map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `smp_main.c` envelope | `[0x00537278,0x00537EEC)` | 3,188 | 20 linked functions / 3,076 code bytes identified; 112 literal/alignment bytes |
| `smpCb` | `[0x20070AEC,0x20070BE8)` | 252 | Three 76-byte connection CCBs plus module interface/config fields |
| Security CB used by stale-AES cleanup | `0x20072CD8` | external | `secCb.aesEncQueue` owner; exact enclosing security layout is separate |

Within each SMP CCB, `keyReady` is at `+0x44` and the secure-connections CCB
pointer is at `+0x48`. Module-wide fields begin at `smpCb+0xE4`; the WSF
handler ID is at `+0xEC`, pairing/auth callbacks at `+0xF0/+0xF4`, and the
LESC-supported byte at `+0xF8`. The handler, L2CAP data/control callbacks, and
DM callback have four authenticated stored Thumb pointers; no other aligned
entry or interior pointer targets this module.

## Cordio SMP Secure Connections main stock map

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Stock `smp_sc_main.c` envelope | `[0x0056CDC0,0x0056D8C4)` | 2,820 | 18 linked functions / 2,626 code bytes identified; 194 literal/alignment bytes |
| `smpCb` | `0x20070AEC` | external | Common SMP control block; three connection records |
| `SMP_ScCcb` | `0x200728F4` | external | Three secure-connections records, stride `0x1C` |
| Retained source path | `0x006DE8B4` | 96 | `smp_sc_main.c` path including NUL; referenced at `0x0056D838` |

The object contains no registered function pointer and no real stored pointer
to an entry or strict interior. Its 111 direct calls land only on exact entries.
The four source-only definitions are `SmpScFree`, both peer-public-key
accessors, and `SmpScSetOobCfg`.

## Cordio SMP Secure Connections role state-machine map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Initiator physical object | `[0x00537F14,0x005380DC)` | 456 | `SmpiScInit`, `smpiStateStr`, and owned literal/string-pointer pool |
| Initiator interface | `0x0078C320` | 12 | Roots 51 actions, 38 state pointers, and common table |
| Initiator scattered dispatch data | multiple | 701 | Action/state pointers plus 39 state-entry tables |
| Responder physical object | `[0x00538104,0x005382E4)` | 480 | `SmprScInit`, `smprStateStr`, alignment, and owned pool |
| Responder interface | `0x0078C470` | 12 | Roots 55 actions, 40 state pointers, and common table |
| Responder scattered dispatch data | multiple | 770 | Action/state pointers plus 41 state-entry tables |

The two physical objects contribute 598 code bytes and 338 pool/alignment
bytes. Interfaces plus scattered dispatch data contribute 1,495 bytes, for
2,431 identified bytes total. `SmpiScInit` stores its interface at
`smpCb+0xE8`; `SmprScInit` stores at `smpCb+0xE4`. No function entry is stored
by either translation unit; their four functions have one direct caller each.

## Cordio SMP common-action stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `smp_act.c` object | `[0x0056E5CC,0x0056F178)` | 2,988 | 25 linked functions / 2,924 code bytes; 64 owned data bytes |
| Inline trace categories | `[0x0056EC88,0x0056EC94)` | 12 | `ERR`, `SMP`, `HCI` |
| Owned literal tail | `[0x0056F144,0x0056F178)` | 52 | `pSmpCfg`, `smpCb`, retained-path and logger literals |
| Retained source path | `[0x006E1994,0x006E19F0)` | 92 | NUL-terminated `smp_act.c` path |
| Responder/initiator SC actions | `0x006D0B64`, `0x006D1214` | 424 | 55 + 51 action pointers |
| Responder/initiator legacy actions | `0x006D7E7C`, `0x006DBAC4` | 208 | 27 + 25 action pointers |
| Pairing/auth callback pairs | `0x00537F0C`, `0x005380FC` | 16 | two identical two-pointer pairs |

All 25 source definitions survive. Raw decoding closes 78 direct calls; the
six rooted pointer objects account for exactly 62 stored entries. No stored
strict-interior address exists. `pSmpCfg` is the pointer variable at
`0x200004B8`; `smpCb` is at `0x20070AEC`.

## Cordio SMP responder-action stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `smpr_act.c` object | `[0x005E38C8,0x005E3D7C)` | 1,204 | Ten linked functions / 1,160 code bytes; 44 owned non-code bytes |
| Trace categories | `[0x005E3BC6,0x005E3BD0)` | 10 | alignment plus `ERR` and `SMP` |
| Owned literal pool | `[0x005E3D2C,0x005E3D4C)` | 32 | `HCI`, diagnostics, path, `pSmpCfg`, and `smpCb` |
| Retained source path | `[0x006DE914,0x006DE971)` | 93 | NUL-terminated `smpr_act.c` path; sole pointer at `0x005E3D38` |
| Responder SC action table | `[0x006D0B64,0x006D0C40)` | 220 | 55 total entries, ten rooted in this TU |
| Responder legacy action table | `[0x006D7E7C,0x006D7EE8)` | 108 | 27 total entries, ten rooted in this TU |

All ten source definitions survive. The two tables account for 20 stored
exact-entry pointers; two internal BL sites enter the confirmation and key-send
helpers. No external direct BL or stored strict-interior address exists. The
r20-only `keyReady=TRUE` write is at `0x005E3C18`, targeting `smpCcb_t+0x44`.

## Cordio SMP initiator-action stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `smpi_act.c` object | `[0x005E3118,0x005E3474)` | 860 | Ten linked functions / 852 code bytes; eight owned literal bytes |
| Owned literal island | `[0x005E3404,0x005E340C)` | 8 | `pSmpCfg=0x200004B8`, `smpCb=0x20070AEC` |
| Initiator SC action table | `[0x006D1214,0x006D12E0)` | 204 | 51 total entries, ten rooted in this TU |
| Initiator legacy action table | `[0x006DBAC4,0x006DBB28)` | 100 | 25 total entries, ten rooted in this TU |

All ten source definitions survive. The 20 table cells are the only genuine
entry ingress. The raw candidate at `0x005E1CEC` is inside the wide multiply
beginning at `0x005E1CEA` and is not a call. No stored strict-interior value
exists. The r20-only `keyReady=TRUE` write is at `0x005E333C`, targeting
`smpCcb_t+0x44`.

## Cordio SMP Secure Connections role-action stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `smpi_sc_act.c` object | `[0x005E3474,0x005E38C8)` | 1,108 | 16 linked functions / 1,070 code bytes; 38 owned tail bytes |
| Initiator SC action table | `[0x006D1214,0x006D12E0)` | 204 | 51 total entries, 16 rooted in this TU |
| Initiator owned tail | `[0x005E38A2,0x005E38C8)` | 38 | `Cai`/`Cbi`, calculation labels, `calc128Zeros`, and `pSmpCfg` |
| Stock `smpr_sc_act.c` object | `[0x005E3D7C,0x005E4228)` | 1,196 | 20 linked functions / 1,162 code bytes; 34 owned tail bytes |
| Responder SC action table | `[0x006D0B64,0x006D0C40)` | 220 | 55 total entries, 20 rooted in this TU |
| Responder owned tail | `[0x005E4206,0x005E4228)` | 34 | `Cbi`/`Ca`, calculation labels, `calc128Zeros`, and `pSmpCfg` |

All 36 source definitions survive. The initiator table cells are its only
entry ingress. The responder has four internal helper calls and no exterior
entry call. Five even packed-data windows numerically resemble responder body
interiors but lack the Thumb bit and are not function pointers; no accepted
stored pointer or direct branch reaches a strict interior. The r20-only
`keyReady=TRUE` stores occur at `0x005E3840` and `0x005E41AA`, both targeting
`smpCcb_t+0x44`.

## Cordio SMP shared Secure Connections action stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `smp_sc_act.c` object | `[0x005E267C,0x005E3118)` | 2,716 | 20 linked functions / 2,662 code bytes; 54 owned tail bytes |
| Shared owned tail | `[0x005E30E2,0x005E3118)` | 54 | F5 length/key/salt, `MAC`/`LTK`, trace labels, `smpCb`, and `pSmpCfg` |
| Common SMP callback cells | `0x0056D824`, `0x0056D828` | 8 | `smpScProcPairing`, `smpScAuthReq` |
| Role-table pointer cells | responder/initiator SC tables | 96 | 24 stored pointers into 13 common action roots |

Twenty of 21 source definitions survive; `SmpScEnableZeroDhKey` is disabled by
its default-false qualification guard. Nineteen direct calls and 26 stored
pointer cells land at entries. Two even packed-data windows and two raw
wide-instruction overlaps are explicitly rejected; no genuine strict-interior
ingress survives. The stock branch at `[0x005E2938,0x005E294E)` retains the
R4/r19 no-input/no-output pairing behavior absent from Packetcraft r20.05-c.

## Cordio SMP legacy role state-machine stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| `SmpiInit` physical object | `[0x00537EEC,0x00537F14)` | 40 | 22-byte initializer plus alignment and four literals |
| Initiator legacy interface | `0x0078C344` | 12 | roots state pointers, actions, and common transitions |
| Initiator legacy actions | `[0x006DBAC4,0x006DBB28)` | 100 | 25 Thumb action pointers |
| Initiator state pointers | `[0x007235E8,0x00723620)` | 56 | 14 state-table roots |
| Initiator state entries | scattered | 162 | common plus 14 terminated tables |
| `SmprInit` physical object | `[0x005380DC,0x00538104)` | 40 | 22-byte initializer plus alignment and four literals |
| Responder legacy interface | `0x0078C4AC` | 12 | roots state pointers, actions, and common transitions |
| Responder legacy actions | `[0x006D7E7C,0x006D7EE8)` | 108 | 27 Thumb action pointers |
| Responder state pointers | `[0x00718E50,0x00718E8C)` | 60 | 15 state-table roots |
| Responder state entries | scattered | 195 | common plus 15 terminated tables |

Combined exact identified ownership is 785 bytes. The initializers install
the interfaces at `smpCb+0xE8/+0xE4` and shared callbacks at `+0xF0/+0xF4`.
Their only direct calls are `0x004B807C` and `0x004B8084`; no stored or
branched strict-interior address survives. The responder's 27-entry action
table and timeout/cleanup rows select the r20/R4 state-machine topology.

### Non-SMP alternative exclusion

`smp_non.c` owns no stock flash or SRAM interval. The two complete fixed-
channel registration windows are `[0x004B5132,0x004B513C)` for ATT/CID 4 and
`[0x00537CE4,0x00537CEE)` for full SMP/CID 6. The latter loads the unique
stored callbacks `0x00537ED8 -> 0x00537279` and
`0x00537ED4 -> 0x00537445`. No third `L2cRegister` call or alternate callback
root exists, so all three non-SMP definitions remain source-only and contribute
zero bytes to the memory map.

## Ambiq Cordio HCI event-port stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `hci_evt.c` physical object | `[0x00569D4C,0x0056B7EC)` | 6,816 | 79 linked functions / 6,718 code bytes; 98 owned data bytes |
| Parser table | `[0x006C910C,0x006C9260)` | 340 | 85 cells / 74 non-null / 69 unique parser entries |
| Callback-size table | `[0x006E3720,0x006E3775)` | 85 | exact size for each internal callback event |
| Retained source path | `[0x006E0518,0x006E0574)` | 92 | NUL-terminated Ambiq `hci_evt.c` path |
| `hciCb` | `0x20073870` | external | event/security callback ownership confirmed by field loads |
| `hciEvtStats` | `0x20073BC0` | external | counter object; sole literal reference is in the TU tail |
| Clean-room event leaves/alignment | `[0x007EFE9C,0x007F5AE0)` | 23,620 | 79 compiled leaves / 23,590 text bytes plus 30 alignment bytes; 52 strict relocations |

The physical object hashes to
`4d7dfa091432416e0eab04bedee540929d97fd640295906f64ce36ea71d85b2d`.
The parser and callback-size tables hash to `b61db547...fb60` and
`72451d4e...3ef8`. Ten direct calls plus 74 stored parser cells close all
linked entries; no aligned strict-interior pointer survives. `hciEvtGetStats`
has no body before the next TU and owns no stock interval.

All 79 stock entries are now source-routed: 78 guarded branches and the exact
two-byte scan-timeout no-op copied in place. The canonical overlay ends at
`0x007F5AE0`, leaving 34,080 bytes before the protected bootloader update
record at `0x007FE000`. The overlay builder and package installer both enforce
that exact boundary; the former conservative `0x007F0000` policy did not mark
a physical object and is no longer used as the acceptance limit.

## Ambiq Cordio HCI core stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `hci_core.c` physical object | `[0x0052A67C,0x0052AE38)` | 1,980 | 22 linked functions / 1,964 code bytes; 16 literal bytes |
| Owned literal pool | `[0x0052AE14,0x0052AE24)` | 16 | `hciCoreCb`, `hciCb`, 64-bit LE-feature object, CIS-array address |
| `hciCoreCb` | `0x20071478` | at least `0xA4` | three 28-byte connection records, six CIS handles, ACL queue/configuration |
| `hciCoreCb.cis` | `0x200714CC` | 12 | six `uint16_t` controller handles |
| `hciLeSupFeatCfg` | `0x20000028` | 8 | 64-bit configured LE feature mask |
| external `hciCb` | `0x20073870` | external | reset state and flow callback at `+0x14` |

The physical object hashes to
`89aa38ab7907c0b6a8b18d1949c7dbf9d85dc382b528e396ac3a6e8f35b505e3`.
Thirty-two direct calls close all 22 linked entries; no aligned stored entry or
strict-interior pointer exists. `hciCoreTxAclDataFragmented` and
`HciSetAclQueueWatermarks` are source-only and own no stock interval.

## Ambiq Cordio HCI platform-shim stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `hci_core_ps.c` physical object | `[0x00530C00,0x00530D74)` | 372 | 9 linked functions / 360 code bytes; 12 literal bytes |
| Owned literal pool | `[0x00530D68,0x00530D74)` | 12 | `hciCoreCb`, `hciCb`, and `hciCoreCb.bdAddr` |
| `hciCoreCb.bdAddr` | `0x200714E0` | 6 | control-block offset `+0x68` |
| Source leaves and alignment | `[0x007ED8AE,0x007EDAB6)` | 520 | 514 compiled bytes plus three two-byte alignment spans |

The physical object hashes to
`af477f877f3e5fff17af792d0e5cb5ac459bdbb84b784725d701bd911bfed904`.
Twenty-one direct calls close all nine entries; no stored entry or strict-
interior pointer survives. Eleven public getter definitions are source-only
and target-compile. All nine stock entries now guard-route to source leaves;
the retained `hciCoreCb` and `hciCb` addresses remain the production ABI.

## Ambiq Cordio HCI transport stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `hci_tr.c` physical object | `[0x0053013C,0x00530364)` | 552 | 3 linked functions / 524 code bytes; 28 literal bytes |
| Receive-state literal pool | `[0x00530348,0x00530364)` | 28 | seven pointers to the complete persistent RX state |
| RX header scratch | `0x2007464C` | 4 | temporary event/ACL header |
| RX packet/data pointers | `0x20074650`, `0x20074654` | 8 | allocation base and current write cursor |
| RX count/state/type | `0x20074F30`, `0x20074FCE..0x20074FCF` | 4 | remaining count, state, and packet indicator |
| Receive-in-progress flag | `0x20074FCD` | 1 | set from packet type through complete delivery |
| Clean-room `hciTrSendAclData` | `0x007ED6E8` | 52 | source-compiled production leaf; one strict driver relocation |
| Clean-room `hciTrSendCmd` | `0x007ED71C` | 32 | source-compiled production leaf; one strict driver relocation |
| Clean-room `hciTrSerialRxIncoming` | `0x007ED73C` | 370 | source-compiled production leaf; four strict core/getter/allocator relocations |

The physical object hashes to
`89831c5be3644e40fe6007f24df12f2929d7ffe4ae525ab190e28e7d9e9fc069`.
Four direct callers reach the three entries; six direct provider calls leave
the TU. No stored entry or strict-interior pointer survives. The omitted
`hciTrReceivingPacket` getter owns no stock interval but remains in the
maintained translation unit and target-compiles. Guarded redirects at all
three stock entries route to the source leaves above; the seven retained SRAM
cells remain the production ABI.

## Ambiq Cordio HCI command stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `hci_cmd.c` physical object | `[0x0052AE38,0x0052B8A4)` | 2,668 | 50 linked functions / 2,654 code bytes; 14 alignment/literal bytes |
| Alignment/literal island | `[0x0052B6AE,0x0052B6BC)` | 14 | two zero bytes, queue pointer, `hciCmdCb`, and `hciCb` |
| `hciCmdCb` | `0x20073A90` | at least `0x1B` | timer `+0x00`, queue `+0x10`, opcode `+0x18`, command credit `+0x1A` |
| external `hciCb` | `0x20073870` | external | shared HCI controller state |

The physical object hashes to
`dc34dc1f11085b6c7e8748c7edebf2e1b4dbc1568774dd8352b7fc064ca15119`.
Raw decoding closes 156 direct ingress sites and 127 direct calls issued by
the linked bodies. No stored word reaches an entry. The sole word resembling
a strict-interior pointer, `0x0052B5EF` at `0x006317C0`, is packed data and
is explicitly rejected as ingress. Twenty-two source definitions own no stock
interval.

## Ambiq Apollo3 HCI-driver stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| `error_check` helper | `[0x004B47AE,0x004B47CC)` | 30 | linked recovery helper |
| Main linked driver interval | `[0x004B48A6,0x004B4D2C)` | 1,158 | 11 contiguous linked bodies |
| Shared mixed-owner literal pool | `[0x004B4D2C,0x004B4DC4)` | 152 | driver state, transport buffers, timers, and adjacent literals |
| TX records | `0x20065A10` | 2,080 | eight 260-byte queue records |
| Write queue | `0x20073BA8` | external | eight-record blocking transport queue |
| RX buffer | `0x20000DAC` | 256 | blocking BLEIF read buffer |
| Heartbeat / wake timers | `0x20073E64`, `0x20073E74` | 16 each | ten-second heartbeat and wake control |
| BLE MAC / NVDS buffer | `0x20074148`, `0x20074150` | 6 / 8 | controller address and runtime vendor payload |
| WSF handler pointer cell | `0x004B8798` | 4 | `0x004B4AB3`, Thumb `HciDrvHandler` |

The main interval hashes to
`809a750836b2494d4d71125db43181e4f84f12333a07b2d4d8147ee59a9be983`;
the 12 source-ordered bodies hash to
`82d378d8a979e3cede7a46f2d0c9027840afbeb931c42e3484acf15b6bde154a`.
Thirty direct ingress sites and all 66 provider calls are pinned. Thirty words
in unrelated packed data happen to equal interior address `0x004B4B00`; they
are rejected, leaving no accepted pointer or branch to a strict interior.

## G2 product BLE-startup and GPIO-vector map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| inferred subsystem init | `[0x004B7478,0x004B748C)` | 20 | four product manager initializers |
| inferred DM callback | `[0x004B748C,0x004B74F0)` | 100 | variable-sized event forwarding |
| inferred ATT callback | `[0x004B74F0,0x004B7532)` | 66 | ATT event/value forwarding |
| inferred CCC callback | `[0x004B7532,0x004B758A)` | 88 | connection update and event forwarding |
| inferred delayed callback | `[0x004B758A,0x004B75CE)` | 68 | event `0xBC`; 10/20-second rearm |
| inferred product message processor | `[0x004B75CE,0x004B7D32)` | 1,892 | DM/ATT/profile state machine |
| `_bleCommHandler` | `[0x004B7D32,0x004B7E74)` | 322 | exact retained product handler |
| inferred handler/config init | `[0x004B7E74,0x004B7EC2)` | 78 | WSF ID, runtime SMP config, app frameworks |
| inferred stack registration | `[0x004B7EC2,0x004B7F5E)` | 156 | DM/ATT/CCC/profile/service registration |
| `_bleExactleStackInit` | `[0x004B7F64,0x004B80BE)` | 346 | exact retained product name/path |
| Apollo510 GPIO group ISR | `[0x004B80BE,0x004B80EA)` | 44 | vector 75 / external IRQ 59 / `GPIO0_607F_IRQn` |
| inferred BLE-address getter | `[0x004B80EA,0x004B80F0)` | 6 | returns six-byte address at `0x200737BF` |
| inferred product BLE start | `[0x004B80F0,0x004B8122)` | 50 | radio/stack/profile/reset startup wrapper |
| WSF buffer memory | `0x2004FA98` | 10,560 | initialized here; owned by the WSF pool audit |
| WSF pool descriptor input | `0x200003B0` | 16 | four descriptors; independently bounded |
| Vector pointer cell | `0x0043812C` | 4 | `0x004B80BF`, Thumb GPIO handler |
| Product WSF-handler cell | `0x004B8794` | 4 | `0x004B7D33`, Thumb `_bleCommHandler` |

The thirteen-body concatenation hashes to
`60845b967cc5c6fb4c87f827d863defa45504ff642966e07aad9e2f4a284c025`;
the complete mixed interval hashes to
`1c36c8ffbc29b94e18b2a4f1804c30ac5389805a4833bb3c9e5d4b48bc0d7090`.
Nine direct entry calls and all 267 body calls are pinned. Seven stored
pointers root callbacks/handlers; two unaligned interior-looking byte windows
are rejected, leaving no accepted strict-interior pointer or wide/direct
branch. The GPIO handler is foreign ownership, so the enclosing range is not
represented as an exclusively owned contiguous `app_ble.c` translation unit.
It also disproves the previous assumption that the retained
`HciDrvIntService` had an out-of-payload vector caller.

## Ambiq HCI vendor reset-sequence stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Linked vendor/reset bodies | `[0x00569B04,0x00569D26)` | 546 | two feature helpers, reset start, reset sequence |
| Alignment/literal tail | `[0x00569D26,0x00569D4C)` | 38 | two zero bytes plus nine state/mask pointers |
| `hciCoreCb` / `hciCb` | `0x20071478`, `0x20073870` | external | reset sequence and completion callback state |
| 64-bit LE feature configuration | `0x20000028` | 8 | privacy/data-length branch gating |
| Reset random counter | `0x20074FD0` | 1 | four LE Random completions |
| Event masks | `0x0078D6DC`, `0x0078D6E4`, `0x0078D6EC` | 8 each | standard, LE, and page-2 masks |

The complete interval hashes to
`9509223fa164fab9f580b13bb3cab31e17d41929c636f43b1a4ba5fc435af441`;
the four body concatenation hashes to
`6c3463af9d30f55b582fd4bf51cfeb90931c2bfc1b72b8544803d75c65dee3a0`.
Five direct ingress and 25 provider calls close the object with no stored
entry or strict-interior pointer.

## Cordio HCI PHY-command stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| `HciLeSetPhyCmd` body | `[0x00539E48,0x00539E92)` | 74 | sole linked definition; SHA-256 `99adfd21...d4d2c` |
| TU alignment | `[0x00539E92,0x00539E94)` | 2 | zero padding before the next object |

The sole direct caller is `DmSetPhy` at `0x004C5844`; the only outbound calls
are `hciCmdAlloc` and `hciCmdSend`. No stored entry or strict-interior pointer
survives. `HciLeReadPhyCmd` and `HciLeSetDefaultPhyCmd` own no stock interval.

## Cordio ATT client-core stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `attc_main.c` object | `[0x00530D74,0x00531BD4)` | 3,680 | 20 linked functions / 3,540 code bytes; 140 owned data bytes |
| Retained source path | `[0x006DC814,0x006DC874)` | 96 | NUL-terminated `attc_main.c` path plus alignment |
| Request dispatch | `[0x00700920,0x00700964)` | 68 | 17 entries / 13 stored function pointers |
| Client interface | `[0x00785250,0x00785260)` | 16 | data, control, message, and connection callbacks |
| `attcCb` | `0x2006F904` | `0x1B8` | nine 44-byte CCBs, three on-deck messages, signing pointer, auto-confirm flag |

The physical object hashes to
`3571bc76a244b81e8a605b4da8386fc1f3007b49eb3fae763ab077101422970d`.
Raw decoding closes 32 direct calls and the two rooted tables account for all
17 stored entries; no stored strict-interior address exists. The nine CCBs
encode three connections by three bearers, selecting the r20 EATT layout.

## Cordio ATT client request/response stock map

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Mandatory PDU processor | `[0x004B5230,0x004B59C0)` | 1,936 | 15 linked functions / 1,884 code bytes; 52 owned data bytes |
| Optional read unit | `[0x0056C3B0,0x0056C550)` | 416 | 4 linked functions / 414 code bytes; 2 alignment bytes |
| Optional write unit | `[0x00539DCC,0x00539E48)` | 124 | 2 linked functions; no owned tail |
| Response dispatch | `[0x00700964,0x007009A8)` | 68 | 17 entries; 13 non-null pointers |
| Minimum-PDU table | `[0x00785270,0x0078527D)` | 13 | methods 0--12 only; following bytes are not table-owned |

The three physical objects hash to `7e521c56...b73a`,
`d3286218...4495`, and `72a705a8...adc9`, respectively. Raw decoding closes
24 direct calls and thirteen local stored response entries with no real
strict-interior ingress. Nine source APIs are dead-stripped. Method values
16 and 17 can index beyond the minimum-PDU and response tables in the
inherited R4 behavior; adjacent string bytes remain explicitly outside the
owned table ranges.

### Optional ATT client signing exclusion

`attc_sign.c` owns no stock interval. `AttcInit [0x00531B1C,0x00531B90)`
stores null at `attcCb + 0x1B0` (`0x2006FAB4`), and no later store installs
the two-callback signing interface. The only image literals for
`attcCb=0x2006F904` are at `0x004B59A8` and `0x00531BAC`, both within already
bounded ATT objects. All seven source definitions are dead-stripped.

## Cordio ATT server-signing partial object

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Linked `atts_sign.c` physical object | `[0x0052DA58,0x0052DBF0)` | 408 | Four linked functions / 370 code bytes; 38 owned alignment/literal bytes |
| Connection helper | `[0x0052DA58,0x0052DB92)` | 314 | Assertion-expanded `attsSignCcbByConnId` |
| Owned literal gap | `[0x0052DB92,0x0052DBB8)` | 38 | Categories, retained path, function/global literals |
| Three public state APIs | `[0x0052DBB8,0x0052DBF0)` | 56 | CSRK/auth flag setter and sign-counter set/get |
| `attsSignCb` | `[0x2007335C,0x20073394)` | 56 | Three 16-byte records plus 8-byte queue |
| `attsCb.signMsgCback` | `0x2006E854` | 4 | Initialized to `attEmptyHandler`; signing initializer absent |

Each signing record stores the counter at `+0`, CSRK pointer at `+4`, current
buffer pointer at `+8`, and authenticated flag at `+0x0C`. There is one raw
literal for `attsSignCb`, no direct callback-slot literal, no stored function
entry/interior pointer, and no branch into a strict interior. The four absent
processing definitions own no stock interval.

## Cordio ATT server indication/notification object

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `atts_ind.c` physical object | `[0x005338AC,0x00533EF4)` | 1,608 | Thirteen linked functions / 1,552 code bytes; 56 owned data bytes |
| Callback interface | `[0x007852C0,0x007852D0)` | 16 | Empty data callback plus control, message, and connection callbacks |
| ATT server processor table | `0x2000045C` | 72 | Live initialized SRAM table; method 15 cell at `0x20000498` points to `attsProcValueCnf+1`; raw `0x00791AD0` is the compressed initializer-stream word, not the runtime cell |
| Retained source path | `[0x006DC994,0x006DC9F1)` | 93 | NUL-terminated `atts_ind.c` path |
| `attsCb` | `0x2006E5F0` | external | Nine server CCBs plus shared ATTS state; `pInd` at `+0x260` |

The server CCB array has three connections by three bearers, 64 bytes per
record and `0xC0` bytes per connection. Timer/main-CCB/connection/slot fields
are at `+0/+0x10/+0x24/+0x25`; outstanding and pending indication handles are
at `+0x26/+0x28`, followed by ten notification handles at `+0x2A`. Twenty-two
direct calls and three interface pointers land only at exact entries. The
method-15 word is separately recovered from the IAR initializer. The two
zero-copy wrappers own no stock interval.

## Cordio ATT server owner/dispatcher object

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `atts_main.c` physical object | `[0x0053498C,0x00535488)` | 2,812 | Seventeen linked functions / 2,710 code bytes; 102 owned data bytes |
| Server callback interface | `[0x007852F0,0x00785300)` | 16 | Data, L2CAP control, message, and connection callbacks |
| Minimum-PDU table | `[0x0077E2D0,0x0077E2E2)` | 18 | One byte per ATT method 0--17 |
| Live processor table | `[0x2000045C,0x200004A4)` | 72 | Initialized SRAM; 18 method pointers, method 15 cell at `0x20000498` |
| Retained source path | `0x006DC9F4` | 94 | NUL-terminated R4-family `atts_main.c` path |
| `attsCb` | `0x2006E5F0` | external | Group queue `+0x258`, indication interface `+0x260`, signing callback `+0x264` |

The live processor table is reconstructed from the authenticated IAR scatter
record. The raw matching word at `0x00791AD0` is inside its compressed stream,
not a memory-mapped runtime table cell. `AttsInit` initializes nine 64-byte
server CCBs and stores the server interface at `attCb+0x40`. Forty-five direct
calls and four registered callbacks target exact entries; four source helpers
have no standalone stock interval.

## Cordio common ATT server-processor object

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `atts_proc.c` physical object | `[0x0056C550,0x0056CDC0)` | 2,160 | Nine linked functions / 2,106 code bytes; 54 owned data bytes |
| Live method roots | `0x20000460`, `0x20000464`, `0x20000470`, `0x2000049C` | 16 | Methods 1, 2, 5, and 16 in initialized `attsProcFcnTbl` |
| Retained source path | `[0x006DCA54,0x006DCAB2)` | 94 | NUL-terminated `atts_proc.c` path |

The object owns the UUID, attribute/range lookup, permission, MTU, find-info,
read, and read-multiple-variable implementations. Twenty-six direct calls and
four live initialized method roots target exact entries; no strict-interior
pointer or branch survives.

## Cordio ATT core object and default interfaces

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `att_main.c` physical object | `[0x004B4DE0,0x004B5230)` | 1,104 | 21 linked functions / 1,030 code bytes; 74 owned noncode bytes |
| `attCb` | `0x200610AC` | at least 100 | Three 20-byte CCBs; legacy/EATT pointers at `+0x3C..+0x54`; handler ID `+0x60` |
| `attFcnDefault` | `[0x007851E0,0x007851F0)` | 16 | Legacy data/control/message/connection no-op interface |
| `eattFcnDefault` | `[0x007851F0,0x00785200)` | 16 | Enhanced CoC/CoC/message/connection no-op interface |
| ATT base UUID | `[0x2000044C,0x2000045C)` | 16 | Initialized SRAM Bluetooth base UUID |
| Retained source path | `[0x006DC754,0x006DC7B1)` | 93 | NUL-terminated `att_main.c` path |

`AttHandlerInit` writes the default interfaces to `attCb+0x3C..+0x48` and
registers the L2CAP/DM callbacks. The WSF handler pointer is stored at
`0x004B8788`. Sixty-five direct BL sites and 14 stored pointers land only at
exact entries; the apparent interior values are unrelated packed/string byte
windows rather than accepted pointers.

### Enhanced ATT server exclusion state

| State | Address/value | Meaning |
|---|---:|---|
| `attCb.pEnServer` boot default | `attCb+0x44 -> 0x007851F0` | `eattFcnDefault`; never overwritten in stock |
| Enhanced server initializer | absent | No `EattsInit` or TU-owned `attsFcnIf` root |
| L2CAP CoC | absent | Zero linked functions in the optional CoC TU |
| `atts_eatt.c` linked bytes | 0 | All twelve source definitions dead-stripped |

### Enhanced ATT core/client exclusion state

| State | Address/value | Meaning |
|---|---:|---|
| `attCb.pEnClient` boot default | `attCb+0x48 -> 0x007851F0` | `eattFcnDefault`; never overwritten by `EattcInit` |
| EATT WSF handler | `attCb+0x4C` | Never installed by `EattInit` |
| EATT DM callback | `attCb+0x50` | Never installed by `EattInit` |
| EATT CoC transmit callback | `attCb+0x54` | Never installed by `EattInit` |
| `att_eatt.c` linked bytes | 0 | All 26 source definitions dead-stripped |
| `attc_eatt.c` linked bytes | 0 | All 20 source definitions dead-stripped |
| Complete enhanced bearer implementation | absent | Core, client, server, and L2CAP CoC TUs all have zero linked functions |

### Dynamic ATT service exclusion state

| State | Address/value | Meaning |
|---|---:|---|
| Dynamic ATT private heap | absent | Optional 1,280-byte `attsDynHeap` not instantiated |
| `AttsAddGroup` dynamic callers | 0 | Eight stock callers belong to static service builders |
| `AttsRemoveGroup` dynamic callers | 0 | Sole stock caller belongs to the CSF/database path |
| `atts_dyn.c` linked bytes | 0 | All seven source definitions dead-stripped |

## Cordio ATT UUID constant-object block

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Retained `att_uuid.c` objects | `[0x0078F53A,0x0078F550)` | 22 | 11 source-ordered two-byte UUID constants; SHA-256 `abd74006...735e3` |
| Prior unrelated halfword | `[0x0078F538,0x0078F53A)` | 2 | Value `0x003D`; excluded from TU |
| Following `atts_read.c` UUIDs | `[0x0078F550,0x0078F556)` | 6 | Local `0x2800,0x2801,0x2800`; separately owned |
| Stored reference cells | whole image | 216 | 54 aligned four-byte pointers; zero unaligned windows |

The retained values are GATT service, primary service, characteristic,
client-configuration, device-name, appearance, service-changed, CAR, RPAO,
client-supported-features, and database-hash UUIDs. The other 141 exported
objects are dead-stripped. Equal-valued UUID bytes elsewhere belong to local
attribute/service tables and are not merged into this physical ownership span.

## Cordio optional ATT server-read object

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `atts_read.c` physical object | `[0x0056D93C,0x0056E4F8)` | 3,004 | Seven linked functions / 2,984 code bytes; 20 owned literal bytes |
| Live method roots | `0x20000468`, `0x2000046C`, `0x20000474`, `0x20000478`, `0x2000047C` | 20 | Methods 3, 4, 6, 7, and 8 in initialized `attsProcFcnTbl` |
| Literal tail | `[0x0056E4E4,0x0056E4F8)` | 20 | `attsCb`, primary/secondary service, database-hash, and read-group UUID pointers |

The object owns the range helpers and read-blob, find-by-type-value,
read-by-type, read-multiple, and read-by-group-type processors. Nine direct
calls and five initialized method roots reach exact entries. One unaligned raw
interior-valued byte window is accidental; no accepted stored pointer or
direct branch reaches a strict interior.

## Cordio ATT server-write object

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `atts_write.c` physical object | `[0x005A5D94,0x005A6260)` | 1,228 | Four linked functions / 1,220 code bytes; 8 owned literal bytes |
| Live method roots | `0x20000480`, `0x20000484`, `0x20000488`, `0x2000048C` | 16 | Methods 9--12; methods 9/10 share `attsProcWrite` |
| Prepared-write queues | `0x2006E828` (`attsCb+0x238`) | 24 | Three eight-byte WSF queues, one per connection |
| Literal tail | `[0x005A6258,0x005A6260)` | 8 | `attsCb=0x2006E5F0`, `pAttCfg=0x200004B4` |

The object owns prepared-write execution plus write, prepare-write, and
execute-write processors. One internal helper call and four initialized
method cells reach exact entries. `AttsContinueWriteReq` has no stock body.
Three unaligned raw interior-valued windows are accidental; no accepted stored
pointer or direct branch reaches a strict interior.

## G2 BLE WSF product thread

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Product `thread_ble_wsf.c` physical TU | `[0x004D0A4C,0x004D0D24)` | 728 | Twelve linked bodies / 656 code bytes; 72 owned literal bytes |
| Owned literal pool | `[0x004D0CDC,0x004D0D24)` | 72 | Product state, path, names, diagnostics, task attributes, and Thumb task entry |
| Static `osThreadAttr_t` | `[0x0075B838,0x0075B85C)` | 36 | `ble_wsf`, CB `0x20072140`/`0x70`, stack `0x20043A98`/`0x4000`, priority `0x31` |
| Product thread state | `0x20004068` | at least 24 | Thread handle `+0x08`; transmit-ready semaphore handle `+0x14` |
| Static CMSIS thread control block | `0x20072140` | 112 | Passed to `osThreadNew` |
| Static task stack | `[0x20043A98,0x20047A98)` | 16,384 | `ble_wsf` worker stack |

The task entry is the aligned odd pointer `0x004D0A4D` stored at
`0x004D0CF8`. It starts BLE and dispatches WSF forever. The semaphore is
created with maximum/initial counts `1/1`; completion notification releases
it only when its current count is zero.

## G2 BLE message TX/RX product threads

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Product `thread_ble_msgtx.c` physical TU | `[0x00475290,0x00475FC0)` | 3,376 | 21 source-replaced bodies / 3,096 code bytes; four retained data islands / 280 bytes |
| TX static `osThreadAttr_t` | `[0x0075B85C,0x0075B880)` | 36 | `ble_msgtx`, CB `0x200721B0`/`0x70`, stack `0x20047A98`/`0x4000`, priority `0x30` |
| Product `thread_ble_msgrx.c` physical TU | `[0x0048EDB0,0x0048F3A4)` | 1,524 | 13 identified stock bodies / 1,390 code bytes; two owned data islands / 134 bytes |
| RX lifecycle/task bodies | `[0x0048EDB0,0x0048EEAC)` | 252 | Task, two no-op hooks, queue init, enter/ready, create, and destroy |
| RX queue drain | `[0x0048EEAC,0x0048EFAC)` | 256 | Dispatches types `0x80`, `0xC0..0xC7`, `0x200`, and `0x400`, then frees records |
| RX flags and exit | `[0x0048EFAC,0x0048F018)` | 108 | Queue bit `0x00400000`, exit bit `0x00800000`, lifecycle index 7 |
| RX queue clear | `[0x0048F018,0x0048F126)` | 270 | Zero-timeout drain and record release |
| RX inline alignment/string | `[0x0048F126,0x0048F12C)` | 6 | Two zero bytes plus `mac\0` |
| `Thread_MsgRxFromBle` | `[0x0048F12C,0x0048F324)` | 504 | Allocates aligned `{type,len,payload}` record, queues with timeout 500, wakes RX task |
| RX diagnostic/literal tail | `[0x0048F324,0x0048F3A4)` | 128 | Product state, retained path, task attributes/entry, names, diagnostics, and dependencies |
| RX static `osThreadAttr_t` | `[0x0075B880,0x0075B8A4)` | 36 | `ble_msgrx`, CB `0x20072220`/`0x70`, stack `0x2004BA98`/`0x4000`, priority `0x30` |

The RX end is exact: the following nanopb function begins at `0x0048F3A4`.
The task entry is stored at `0x0048F340`; the external receive callback is
stored at `0x004C9C64`. No accepted pointer or branch reaches a strict
interior. See `research/g2-thread-ble-message-recovery.md`.

## FreeRTOS ISR receive and CMSIS pool-operation source replacements

| Stock range | Bytes | Current state |
|---|---:|---|
| `[0x00441DA6,0x00441E66)` | 192 | Source-replaced FreeRTOS V10.5.1 `xQueueReceiveFromISR` |
| `[0x00441F5E,0x00441F88)` | 42 | Source-replaced private `prvCopyDataFromQueue` |
| `[0x0044994E,0x004499B8)` | 106 | Source-replaced CMSIS-FreeRTOS v10.5.1 `osSemaphoreAcquire` |
| `[0x00449D3E,0x00449DD0)` | 146 | Source-replaced `osMemoryPoolAlloc` |
| `[0x00449DD4,0x00449E8E)` | 186 | Source-replaced `osMemoryPoolFree` |
| `[0x00449E98,0x00449EB8)` | 32 | Source-replaced private `CreateBlock` |
| `[0x00449EB8,0x00449ECA)` | 18 | Source-replaced private `AllocBlock` |
| `[0x00449ECA,0x00449ED2)` | 8 | Source-replaced private `FreeBlock` |

The manifest splits every complete stock span from intervening literal or
alignment gaps, so unrelated compatibility bytes remain opaque. The appended
Apple leaves occupy overlay offsets `133048..133794`; Linux uses
`134924..135670`. See the three focused source audits under `docs/research`.
## FreeRTOS task-receive and CMSIS message-operation replacements

| Stock range | Bytes | Current state |
|---|---:|---|
| `[0x00441952,0x00441A42)` | 240 | Source-replaced `xQueueGenericSendFromISR` |
| `[0x00441B0A,0x00441C44)` | 314 | Source-replaced `xQueueReceive` |
| `[0x00441ED8,0x00441F5E)` | 134 | Source-replaced `prvCopyDataToQueue` |
| `[0x00441F88,0x00441FF6)` | 110 | Source-replaced `prvUnlockQueue` |
| `[0x00449ABE,0x00449B3C)` | 126 | Source-replaced `osMessageQueuePut` |
| `[0x00449B3C,0x00449BBC)` | 128 | Source-replaced `osMessageQueueGet` |
| `[0x00449376,0x00449398)` | 34 | Source-replaced `osDelay` |
| `[0x004491B2,0x004491E4)` | 50 | Source-replaced `osThreadSetPriority` |
| `[0x004491FE,0x00449238)` | 58 | Source-replaced `osThreadTerminate` |
| `[0x00449238,0x004492C2)` | 138 | Source-replaced `osThreadFlagsSet` |
| `[0x004492C2,0x00449376)` | 180 | Source-replaced pre-`bb8a350a` `osThreadFlagsWait` |
| `[0x00454AAE,0x00454B4C)` | 158 | Source-replaced `vTaskDelete` |
| `[0x00454B4C,0x00454B88)` | 60 | Source-replaced `vTaskDelay` |
| `[0x00454B88,0x00454C12)` | 138 | Source-replaced `eTaskGetState` |
| `[0x00454C12,0x00454CEC)` | 218 | Source-replaced `vTaskPrioritySet` |
| `[0x00455282,0x004552AE)` | 44 | Source-replaced `vTaskPlaceOnEventList` |
| `[0x0045596E,0x00455A12)` | 164 | Source-replaced `xTaskPriorityDisinherit` |
| `[0x00455836,0x00455876)` | 64 | Source-replaced private `prvDeleteTCB` |
| `[0x00455B84,0x00455C48)` | 196 | Source-replaced `xTaskGenericNotifyWait` including its literal pool |
| `[0x00455C48,0x00455DB8)` | 368 | Source-replaced `xTaskGenericNotify` |
| `[0x00455DB8,0x00455DC0)` | 8 | Retained stock alignment/literal gap |
| `[0x00455DC0,0x00455F5C)` | 412 | Source-replaced `xTaskGenericNotifyFromISR` |
| `[0x00455FA8,0x0045601E)` | 118 | Source-replaced `prvAddCurrentTaskToDelayedList` |

The appended Apple leaves occupy overlay offsets `133794..137090`; the
thread-termination subtranche occupies `135654..136064` and the subsequent
thread-flags subtranche occupies `136064..137090`. Exact-root Linux closes at
`138970`. Intervening alignment and unrelated stock bytes remain separately
classified.

## CMSIS-FreeRTOS thread-creation replacement

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `osThreadNew` | `[0x004490E2,0x004491AA)` | 200 | Complete entry redirect and NOP fill |
| Retained `xTaskCreateStatic` | `[0x00454820,0x004548BA)` | 154 | Authenticated FreeRTOS V10.5.1 creator with G2 TCB seam |
| Retained `xTaskCreate` | `[0x004548BA,0x00454938)` | 126 | Authenticated FreeRTOS V10.5.1 dynamic creator |
| Apple source leaf | `0x007B5AA8` | 168 | Overlay offset 137,092 |
| Linux source leaf | overlay offset 138,972 | 166 | Exact-root Clang 22 profile |

The preceding two-byte appended alignment is generated. The following stock
`osThreadGetId` span remains separately bounded; the redirect does not widen
into it. CMSIS wrapper ownership is 36/38 public APIs plus all five private
helpers.

## CMSIS-FreeRTOS kernel-lifecycle replacement

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock `osKernelInitialize` | `[0x0044903C,0x0044906C)` | 48 | Complete entry redirect and NOP fill |
| Stock `osKernelGetState` | `[0x0044906C,0x00449094)` | 40 | Existing source redirect, now explicit in manifest accounting |
| Stock `osKernelStart` | `[0x00449094,0x004490CC)` | 56 | Complete entry redirect and NOP fill |
| Retained `vTaskStartScheduler` | `[0x00454CEC,0x00454D7C)` | 144 | Authenticated FreeRTOS V10.5.1 scheduler-start boundary |
| Apple initialize leaf | `0x007B5B50` | 50 | Overlay offset 137,260 |
| Apple start leaf | `0x007B5B84` | 56 | Overlay offset 137,312 after two-byte alignment |
| Linux initialize/start leaves | offsets 139,140 / 139,192 | 50 / 56 | Exact-root Clang 22 profile |

The three wrappers share the fixed CMSIS `KernelState` word at `0x20074384`.
With the two writers admitted atomically, the linked wrapper object is fully
source-owned: 38 public entries and five private helpers.

## Cordio common HCI core replacement

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock linked bodies | 22 spans in `[0x0052A67C,0x0052AE38)` | 1,964 | Guarded redirects to maintained C |
| Retained literal pool | `[0x0052AE14,0x0052AE24)` | 16 | Authenticated `hciCoreCb`, `hciCb`, feature, and CIS addresses |
| Apple compiled leaves | overlay offsets `366484..370198` | 3,690 text + 26 alignment | Source-owned common HCI core |
| Connection control block | `0x20071478` | 3 × 28-byte records | Authenticated production ABI |
| CIS handle array | `0x200714CC` | 6 × 2-byte handles | Authenticated production ABI |

The adjacent `hci_core_ps` routes remain independently source-owned. Prefix
ownership is resolved by longest registered module prefix so synchronizing or
re-promoting `hci_core` cannot remove `hci_core_ps` routes or regions.

## Cordio vendor reset-sequence replacement

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock linked bodies | `[0x00569B04,0x00569D26)` | 546 | Four guarded redirects to clean-room C |
| Retained pool | `[0x00569D26,0x00569D4C)` | 38 | Authenticated alignment and nine-word state/mask pool |
| Apple compiled leaves | overlay offsets `370200..371066` | 862 text + 6 alignment | Source-owned reset/NVDS sequence |
| Reset random counter | `0x20074FD0` | 1 | Four-command completion counter |

The source uses the authenticated control blocks at `0x20071478` and
`0x20073870`, the 64-bit feature configuration at `0x20000028`, and retained
event-mask data at `0x0078D6DC..0x0078D6F4`.

## Cordio HCI command replacement

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock linked command bodies | 50 spans in `[0x0052AE38,0x0052B8A4)` | 2,654 | Guarded redirects to clean-room C |
| Retained alignment/literal island | `[0x0052B6AE,0x0052B6BC)` | 14 | Authenticated non-executable data |
| Apple compiled leaves | overlay offsets `371068..375186` | 4,052 text + 68 alignment | Source-owned complete command layer |
| Source-only command APIs | no stock interval | 22 functions | Maintained and Cortex-M55 target-compiled |

The maintained layer preserves the authenticated `hciCmdCb` at `0x20073A90`
and external `hciCb` at `0x20073870`. All linked executable spans in the stock
object are source-owned; the retained 14 bytes are alignment/literal data.

## Bootloader MX25U25643G quad-mode selector

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock quad selector | `[0x00420E8C,0x00420F0C)` | 128 | Complete entry redirect and NOP fill |
| Retained successor pool | `[0x00420F0C,0x00420F10)` | 4 | Authenticated non-executable literal |
| Apple source leaf | `0x00437BCC` | 152 | Overlay offset 14,164 |
| Linux source leaf | `0x00437BB4` | 152 | Overlay offset 14,140 |

The Apple provider closes at `0x00437C64`, leaving `0x39C` bytes before the
protected main-image boundary. The next retained executable service begins at
`0x00420F10`; it remains a software frontier.

## Bootloader MX25U25643G serial-mode selector

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Retained predecessor pool | `[0x00420F0C,0x00420F10)` | 4 | Authenticated non-executable literal |
| Stock serial selector | `[0x00420F10,0x00420F6A)` | 90 | Complete entry redirect and NOP fill |
| Retained successor gap | `[0x00420F6A,0x00420F70)` | 6 | Authenticated non-executable/alignment bytes |
| Apple source leaf | `0x00437C64` | 124 | Overlay offset 14,316 |
| Linux source leaf | `0x00437C4C` | 124 | Overlay offset 14,292 |

The Apple provider closes at `0x00437CE0`, leaving `0x320` bytes before the
protected main-image boundary. The next retained executable service begins at
`0x00420F70`; it remains a software frontier.

## Bootloader MX25U25643G guarded blocking read

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Retained predecessor gap | `[0x00420F6A,0x00420F70)` | 6 | Authenticated non-executable/alignment bytes |
| Stock guarded read | `[0x00420F70,0x00420FF2)` | 130 | Complete entry redirect and NOP fill |
| Retained successor pool | `[0x00420FF2,0x004210C8)` | 214 | Authenticated literal/alignment data |
| Apple source leaf | `0x00437CE0` | 152 | Overlay offset 14,440 |
| Linux source leaf | `0x00437CC8` | 152 | Overlay offset 14,416 |

The Apple provider closes at `0x00437D78`, leaving `0x288` bytes before the
protected main-image boundary. The next retained executable service begins at
`0x004210C8`; it remains a software frontier.

## Bootloader LittleFS directory bootstrap

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Retained predecessor pool | `[0x00420FF2,0x004210C8)` | 214 | Authenticated literal/alignment data |
| Stock directory bootstrap | `[0x004210C8,0x004211B0)` | 232 | Complete entry redirect and NOP fill |
| Retained successor initializer | `[0x004211B0,0x00421210)` | 96 | Authenticated executable software frontier |
| Apple source leaf | `0x00437D78` | 220 | Overlay offset 14,592 |
| Linux source leaf | `0x00437D60` | 224 | Overlay offset 14,568 |

The Apple provider closes at `0x00437E54`, leaving `0x1AC` bytes before the
protected main-image boundary. The next retained executable service begins at
`0x004211B0`; it remains a software frontier.

## Bootloader LittleFS format/bootstrap service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock format/bootstrap | `[0x004211B0,0x00421210)` | 96 | Complete entry redirect and NOP fill |
| Retained successor initializer | `[0x00421210,0x004212D8)` | 200 | Authenticated executable software frontier |
| Apple source leaf | `0x00437E54` | 108 | Overlay offset 14,812 |
| Linux source leaf | `0x00437E40` | 112 | Overlay offset 14,792 |

The Apple provider closes at `0x00437EC0`, leaving `0x140` bytes before the
protected main-image boundary. The next retained executable service begins at
`0x00421210`; it remains a software frontier.

## Bootloader LittleFS initializer and boot counter

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock initializer | `[0x00421210,0x004212D8)` | 200 | Complete entry redirect and NOP fill |
| Retained successor read callback | `[0x004212D8,0x00421310)` | 56 | Authenticated executable software frontier |
| Apple source leaf | `0x00437EC0` | 260 | Overlay offset 14,920 |
| Linux source leaf | `0x00437EB0` | 260 | Overlay offset 14,904 |

The Apple provider closes at `0x00437FC4`, leaving `0x3C` bytes before the
protected main-image boundary. The next retained executable service begins at
`0x004212D8`; it remains a software frontier. Physical mount, format,
external-flash persistence, power-loss, and cold-boot evidence is unavailable.

## Bootloader LittleFS block-read callback

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock read callback | `[0x004212D8,0x00421310)` | 56 | Complete entry redirect and NOP fill |
| Source-replaced program callback | `[0x00421310,0x00421348)` | 56 | Redirects to fixed source cave `[0x00421214,0x00421250)` |
| Source-replaced erase callback | `[0x00421348,0x00421372)` | 42 | Redirects to fixed source cave `[0x00421250,0x00421280)` |
| Source-replaced sync callback | `[0x004213D4,0x004213D8)` | 4 | Redirects to fixed source cave `[0x00421280,0x00421284)` |
| Exact in-place address helpers | `[0x004213D8,0x004213E6)` | 14 | Byte-identical Apple/Linux source compilations |
| Apple source leaf | `0x00437FC4` | 60 | Overlay offset 15,180 |
| Linux source leaf | `0x00437FB4` | 60 | Overlay offset 15,164 |

The Apple provider closes exactly at the protected `0x00438000` main-image
boundary and has no append headroom. Linux closes at `0x00437FF0` with 16
bytes remaining. The program callback uses authenticated reclaimed body space;
the next retained executable service begins at `0x004213E6`. Future source
leaves must continue using reviewed cave placement rather than crossing the
protected boundary. Live flash-read/program and filesystem evidence is
unavailable.

## Bootloader LittleFS block-program callback

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock program callback | `[0x00421310,0x00421348)` | 56 | Complete entry redirect and NOP fill |
| Fixed source cave | `[0x00421214,0x00421250)` | 60 | Compiled program callback inside the authenticated initializer replacement tail |
| Source-replaced erase callback | `[0x00421348,0x00421372)` | 42 | Redirects to fixed source cave `[0x00421250,0x00421280)` |

The cave builder authenticates the original initializer and program spans,
generates the initializer redirect/NOP tail, authenticates the exact 60-byte
NOP subspan, and only then writes the fixed-address source leaf. The entry at
`0x00421310` branches backward to `0x00421214`. No append bytes or protected
main-image bytes are consumed.

## Bootloader LittleFS block-erase callback

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Stock erase callback | `[0x00421348,0x00421372)` | 42 | Complete entry redirect and NOP fill |
| Fixed source cave | `[0x00421250,0x00421280)` | 48 | Compiled erase callback immediately after the program cave |
| Source-replaced sync callback | `[0x004213D4,0x004213D8)` | 4 | Redirects to fixed source cave `[0x00421280,0x00421284)` |
| Exact in-place address helpers | `[0x004213D8,0x004213E6)` | 14 | Byte-identical Apple/Linux source compilations |

The containing initializer tail now holds three separately pinned,
non-overlapping cave leaves and retains 84 generated NOP bytes after them. The
erase entry branches backward to `0x00421250`; append size and the protected
main boundary are unchanged.

## Bootloader LittleFS sync and address-index helpers

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Fixed sync source cave | `[0x00421280,0x00421284)` | 4 | Exact constant-success C callback |
| Sync entry redirect | `[0x004213D4,0x004213D8)` | 4 | Complete authenticated B.W replacement |
| Identity helper | `[0x004213D8,0x004213DA)` | 2 | Exact in-place source compilation |
| Thresholded mapper | `[0x004213DA,0x004213E6)` | 12 | Exact in-place source compilation |
| Retained successor | `0x004213E6` | — | Authenticated executable software frontier |

The direct-leaf builder authenticates each original stock span and compiler
digest before installing the exact source bytes and classifying them as
source-owned. Because both helpers reproduce stock, provider and package bytes
are unchanged; only the ownership map and flash-plan partition advance.

## Bootloader mapped-memory selector and copy service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Primary stock entry replacement | `[0x004213E6,0x004213EC)` | 6 | Branch and alignment into the primary source cave |
| Primary source cave | `[0x004213EC,0x004214C8)` | 220 | Complete selector, bounds/security policy, address mapping, and copy dispatch |
| Odd-selector source cave | `[0x004214C8,0x004214E6)` | 30 | Complete `1/3/5` wrapper and tail branch |
| Primary generated tail | `[0x004214E6,0x00421548)` | 98 | Authenticated NOP fill |
| Wrapper stock entry replacement | `[0x00421548,0x0042156E)` | 38 | Backward branch and NOP fill |
| Retained literal/alignment pool | `[0x0042156E,0x00421584)` | 22 | Authenticated non-executable control/security and mapped-window constants |
| Retained successor | `0x00421584` | — | Authenticated executable software frontier |

Both reviewed toolchains emit identical 220-byte and 30-byte relocated cave
bodies. The builder authenticates each stock body, generated-NOP cave subspan,
fixed runtime address, compiler digest, and strict relocation before
installation. The Apple provider remains bounded by the protected main-image
boundary. Live register/security state and mapped-memory behavior remain
blocked by unavailable authorized hardware evidence.

## Bootloader 32-bit population-count helper

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Population-count helper | `[0x00421584,0x004215AE)` | 42 | Exact in-place Apple/Linux source compilation |
| Sole direct caller | `0x0042161C` | 4 | Retained call from the two-word selector-table count helper |
| Retained successor | `0x004215AE` | — | Authenticated executable software frontier |

The direct-leaf builder authenticates the original span, both compiler
digests, zero-relocation closure, and exact runtime address before classifying
the byte-identical source body. Provider and package bytes are unchanged;
only ownership and flash-plan partitioning advance.

## Bootloader two-word bitmap helpers

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Nonempty helper | `[0x004215AE,0x004215DC)` | 46 | Exact in-place Apple/Linux source compilation |
| Membership helper | `[0x004215DC,0x004215FE)` | 34 | Exact in-place Apple/Linux source compilation |
| Population-count helper | `[0x004215FE,0x00421632)` | 52 | Exact in-place source compilation with one strict call to `0x00421584` |
| Bitmap table root literal | `0x00422210` | 4 | Retained authenticated pointer to `0x20026E74` |
| Retained successor | `0x00421632` | — | Authenticated executable software frontier |

The table contract uses the low selector byte and two 32-bit words per row.
The direct-leaf builder authenticates each complete stock span, compiler
digest, runtime address, and the count leaf's sole `R_ARM_THM_CALL` before
classifying all 132 bytes as source-owned. Provider and package bytes remain
unchanged; only ownership and flash-plan partitioning advance. Live table
ownership and concurrency remain blocked by unavailable authorized physical
evidence.

## Bootloader validated bitmap update helper

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Bitmap update helper | `[0x00421632,0x004216B2)` | 128 | Exact in-place Apple/Linux source compilation |
| Shared bitmap table | `0x20026E74` | 56 B used | Seven two-word rows addressable by the validated mutator |
| Retained successor | `0x004216B2` | — | Authenticated executable software frontier |

The helper narrows inputs to bytes, rejects row `>=7` or bit `>=57` with
status 6, and otherwise performs the exact set/clear read-modify-write and
returns zero. The direct-leaf builder authenticates the complete stock span,
both compiler digests, zero executable relocations, and the exact runtime
address. Live ownership, concurrency, and atomicity remain blocked by
unavailable authorized physical evidence.

## Bootloader bounded poll-delay helper

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Poll-delay helper | `[0x004216B2,0x004216D4)` | 34 | Exact in-place Apple/Linux source compilation |
| Retained delay dependency | `0x0041D1C0` | — | Strict `R_ARM_THM_CALL`, duration 10 |
| Direct callers | `0x00421BB4`, `0x00421D38`, `0x00421E9C` | — | Authenticated retained call sites |
| Retained successor | `0x004216D4` | — | Authenticated executable software frontier |

The helper checks the 32-bit remaining counter and activity byte before each
iteration, delays, then decrements. The direct-leaf builder authenticates the
complete stock span, both compiler digests, the sole delay relocation, and the
exact runtime address. Live timing and producer/consumer memory visibility
remain blocked by unavailable authorized physical evidence.

## Bootloader mode/configuration transaction service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Mode transaction | `[0x004216D4,0x004217D2)` | 254 | Exact in-place Apple/Linux source compilation |
| Default configuration | `0x00433F08` | 12 | Authenticated `0x0025B800,0,0` template |
| Shared state cells | `0x20027030`, `0x20026FEC`, `0x2002719C`, `0x20027044`, `0x20000550` | — | Current, configuration, auxiliary and ready state |
| Sole dispatcher caller | `0x004222B8` | 4 | Authenticated retained call site |
| Retained successor | `0x004217D2` | — | Authenticated executable software frontier |

Eight strict calls cover optional query, interrupt-state save, source-owned
bitmap count, apply/disable fallback, and source-owned copy. The direct-leaf
builder authenticates the complete stock span, both compiler digests, every
relocation, and exact runtime address. Live interrupt timing, state ownership,
and physical mode changes remain blocked by unavailable authorized evidence.

## Bootloader dual-mode transaction service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Dual-mode transaction | `[0x004217D2,0x00421978)` | 422 | Exact in-place Apple/Linux source compilation |
| Default configuration | `0x00433F14` | 12 | Authenticated `0x00020000,0x000C49BA,0` template |
| Shared configuration/current/ready | `0x20026FF8`, `0x20027034`, `0x20000551` | — | Published transaction state |
| Sole dispatcher caller | `0x004222C0` | 4 | Authenticated retained call site |
| Retained successor | `0x00421978` | — | Authenticated executable software frontier |

Sixteen strict calls cover optional query, critical-state save, source-owned
bitmap count and copy, both mode enable/disable families, and commit providers.
The direct-leaf builder authenticates the complete stock span, both compiler
digests, every relocation, and exact runtime address. The previous 19,764-byte
retained region is therefore split into this 422-byte source body and a
19,342-byte retained successor. Live interrupt timing, state ownership,
controller/register behavior and physical mode changes remain blocked by
unavailable authorized evidence.

## Bootloader bitmap-client configuration and mutation services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Configuration/query publisher | `[0x00421978,0x00421A30)` | 184 | Exact in-place Apple/Linux source compilation |
| Row-zero set / clear | `[0x00421A30,0x00421A94)` | 100 | Two exact in-place helpers |
| Guarded row-one set | `[0x00421A94,0x00421AD6)` | 66 | Exact in-place helper with controller requirement |
| Row-one clear | `[0x00421AD6,0x00421B08)` | 50 | Exact in-place cleanup helper |
| Controller table | `0x2000007C` | — | Controller seams at offsets 4, 12 and 16 |
| Published state | `0x20027004`, `0x20027038`, `0x2002719A` | — | Configuration, current instance and ready byte |
| Retained successor | `0x00421B08` | — | Authenticated executable software frontier |

Sixteen strict calls cover query, critical-state save, source-owned bitmap
count/test/update and source-owned copy. The previous 19,342-byte retained
successor is split into five source bodies totaling 400 bytes and an
18,942-byte retained successor. Live interrupt timing, bitmap/publication
ownership, controller/register behavior and physical clients remain blocked
by unavailable authorized evidence.

## Bootloader mode-one enable, disable and cleanup services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Mode-one enable | `[0x00421B08,0x00421B5C)` | 84 | Exact in-place Apple/Linux source compilation |
| Mode-one disable | `[0x00421B5C,0x00421BA4)` | 72 | Exact in-place last-client control helper |
| Poll/state cleanup | `[0x00421BA4,0x00421BD2)` | 46 | Exact in-place bounded cleanup helper |
| Enable/disable words | `0x0043414C`, `0x00434150` | 4 each | Authenticated control values |
| Active/state cells | `0x2002719B`, `0x20027040` | — | Poll and cleanup state |
| Retained successor | `0x00421BD2` | — | Authenticated executable software frontier |

Eleven strict calls cover source-owned bitmap test/update/nonempty and poll,
critical-state save, and retained control. The previous 18,942-byte retained
successor is split into three source bodies totaling 202 bytes and an
18,740-byte retained successor. Live interrupt timing, state ownership,
control/register behavior and physical mode-one effects remain blocked by
unavailable authorized evidence.

## Bootloader mode-zero enable service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Mode-zero enable | `[0x00421BD2,0x00421CCE)` | 252 | Exact in-place Apple/Linux source compilation |
| Controller table | `0x2000007C` | — | Mode byte and controller-pointer compatibility seam |
| Row-two bitmap | source-owned helper row 2 | — | Low-byte-selected client ownership |
| Active/state cells | `0x2002719B`, `0x20027040` | — | Timeout publication and bounded cleanup state |
| Retained successor | `0x00421CCE` | — | Authenticated executable software frontier |

Nine strict calls cover source-owned bitmap test/update and cleanup, two
critical-state saves, and retained state-query/control providers. The previous
18,740-byte retained successor is split into this 252-byte source body and an
18,488-byte retained successor. Live interrupt timing, state ownership,
controller/register behavior and physical mode-zero effects remain blocked by
unavailable authorized evidence.

## Bootloader row-four enable service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Row-four enable | `[0x00421D5E,0x00421E4A)` | 236 | Exact in-place Apple/Linux source compilation |
| Current/configuration | `0x20027030`, `0x20026FEC` | — | Retained apply inputs |
| Ready/active/complete | `0x20000550`, `0x2002719C`, `0x2002719E` | — | Transaction state |
| Published state | `0x20027044` | — | Timeout pointer |
| Retained successor | `0x00421E4A` | — | Authenticated executable software frontier |

Ten strict calls cover source-owned bitmap test/count/update and cleanup,
critical-state save, and retained switch/apply providers. The previous
18,344-byte retained successor is split into this 236-byte source body and an
18,108-byte retained successor. Live interrupt timing, switch/apply behavior,
state ownership and physical row-four effects remain blocked by unavailable
authorized evidence.

## Bootloader row-four disable and cleanup services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Row-four disable | `[0x00421E4A,0x00421E8C)` | 66 | Exact in-place Apple/Linux source compilation |
| Row-four poll cleanup | `[0x00421E8C,0x00421EBA)` | 46 | Exact in-place active/state cleanup helper |
| Active/state cells | `0x2002719D`, `0x20027048` | — | Poll and publication state |
| Retained successor | `0x00421EBA` | — | Authenticated executable software frontier |

Seven strict calls cover source-owned bitmap test/update/nonempty and poll,
critical-state save, and retained switch. The previous 18,108-byte retained
successor is split into two source bodies totaling 112 bytes and a
17,996-byte retained successor. Live interrupt timing, switch behavior, state
ownership and physical row-four effects remain blocked by unavailable
authorized evidence.

## Bootloader row-five client services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Row-five enable | `[0x00421EBA,0x00422040)` | 390 | Exact in-place Apple/Linux source compilation |
| Row-five disable | `[0x00422040,0x004220B2)` | 114 | Exact in-place final-client cleanup helper |
| Selector/ready cells | `0x20026FF8`, `0x20000551` | — | Mode selection and readiness |
| Pending/active/state cells | `0x2002719F`, `0x2002719D`, `0x20027048` | — | Transaction and timeout publication state |
| Retained successor | `0x004220B2` | — | Authenticated executable software frontier |

Twenty-six strict calls cover source-owned bitmap, critical, selector-mode and
cleanup services plus retained dual switch/commit/null-commit providers. The
previous 17,996-byte retained successor is split into two source bodies
totaling 504 bytes and a 17,492-byte retained successor. Live interrupt timing,
retained provider behavior, state ownership and physical row-five effects
remain blocked by unavailable authorized evidence.

## Bootloader row-six services and mode-family dispatcher

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Row-six enable | `[0x004220B2,0x0042220E)` | 348 | Exact in-place Apple/Linux source compilation |
| Enable literal seam | `[0x0042220E,0x00422220)` | 18 | Authenticated retained data |
| Row-six disable | `[0x00422220,0x0042228E)` | 110 | Exact in-place final-client cleanup helper |
| Disable literal seam | `[0x0042228E,0x004222A0)` | 18 | Authenticated retained data |
| Mode-family dispatcher | `[0x004222A0,0x004222D2)` | 50 | Exact in-place kind-4/5/6 dispatcher |
| Padding/literal seam | `[0x004222D2,0x004222F0)` | 30 | Authenticated retained non-executable bytes |
| Retained executable successor | `0x004222F0` | — | Authenticated executable software frontier |

Thirty-one strict calls cover maintained bitmap, critical, selector-mode and
mode-family services plus retained handle lifecycle providers. The previous
17,492-byte retained successor is split into 508 source bytes, 36 retained
inter-body literal bytes and a 16,948-byte retained suffix. Live interrupt
timing, retained provider behavior, state ownership and physical row-six
effects remain blocked by unavailable authorized evidence.

## Bootloader mode routes, all-row cleanup, and configuration copy

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Seven-kind enable router | `[0x004222F0,0x00422364)` | 116 | Exact in-place Apple/Linux source compilation |
| Seven-kind disable router | `[0x00422364,0x004223D8)` | 116 | Exact in-place Apple/Linux source compilation |
| Selective all-row cleanup | `[0x004223D8,0x00422416)` | 62 | Exact in-place bitmap-driven cleanup helper |
| Fixed configuration copy | `[0x00422416,0x00422430)` | 26 | Exact in-place 20-byte copy helper |
| Literal pool | `[0x00422430,0x00422468)` | 56 | Authenticated retained non-executable bytes |
| Retained executable successor | `0x00422468` | — | Authenticated executable software frontier |

Seventeen strict calls cover the maintained row-specific enable/disable
services, bitmap query, reviewed disable-route alias and retained memcpy
provider. The prior 16,948-byte retained suffix is split into 320 source bytes,
a 56-byte retained literal pool and a 16,572-byte retained executable suffix.
Live bitmap ownership, routed service behavior, concurrent cleanup and
configuration persistence remain blocked by unavailable authorized evidence.

## Bootloader Ambiq debug-domain services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| General debug disable | `[0x00422468,0x004224B2)` | 74 | Exact in-place Apple/Linux source compilation |
| Debug power ownership | `[0x004224B2,0x0042252E)` | 124 | Exact in-place reference-counted domain service |
| Trace disable | `[0x0042252E,0x00422574)` | 70 | Exact in-place `DEMCR.TRCENA` release/poll service |
| Literal pool | `[0x00422574,0x00422590)` | 28 | Authenticated retained non-executable bytes |
| Retained executable successor | `0x00422590` | — | Authenticated executable software frontier |

Nine strict calls cover critical-save, debug power query/enable/disable,
register status polling and the two reviewed same-cluster aliases. The prior
16,598-byte retained region is split into a 56-byte leading literal pool, 268
source bytes, a 28-byte trailing literal pool, and a 16,246-byte retained
suffix. Live debug power, MCUCTRL/DCB register effects, trace quiescence and
timing remain blocked by unavailable authorized evidence.

## Bootloader mode-zero disable and cleanup services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Mode-zero disable | `[0x00421CCE,0x00421D28)` | 90 | Exact in-place Apple/Linux source compilation |
| Mode-zero poll cleanup | `[0x00421D28,0x00421D5E)` | 54 | Exact in-place completion/state cleanup helper |
| Active/completion cells | `0x2002719C`, `0x2002719E` | — | Poll and completion state |
| Published state | `0x20027040`, `0x20027044` | — | Enable and cleanup state pointers |
| Retained successor | `0x00421D5E` | — | Authenticated executable software frontier |

Seven strict calls cover source-owned bitmap test/update/nonempty and poll,
critical-state save, and retained control. The previous 18,488-byte retained
successor is split into two source bodies totaling 144 bytes and an
18,344-byte retained successor. Live interrupt timing, state ownership,
controller/register behavior and physical mode-zero effects remain blocked by
unavailable authorized evidence.
## Bootloader constraint dispatcher and memchr

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Constraint dispatcher | `[0x00422590,0x004225AC)` | 28 | Exact in-place Apple/Linux source compilation |
| Handler/message pool | `[0x004225AC,0x004225D0)` | 36 | Authenticated retained data |
| Optimized `memchr` | `[0x004225D0,0x00422628)` | 88 | Exact in-place relocation-free source compilation |
| Handler registration cell | `0x20027190` | — | Retained runtime binding |
| Retained default handler | `0x00417C28` | — | Strict reviewed call target |
| Retained executable successor | `0x00422628` | — | Authenticated executable software frontier |

The prior retained suffix is split into 116 exact source bytes, a 36-byte
retained pool, and a 16,094-byte retained suffix. Live handler registration,
default-handler behavior, accessible-memory boundaries and physical fault
qualification remain blocked by unavailable authorized evidence.
## Bootloader double-runtime helpers

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| `frexp` wrapper/core | `[0x00422628,0x00422698)` | 112 | Exact in-place Apple/Linux source compilation |
| Ordered comparators | `[0x00422698,0x00422700)` | 104 | Two exact flag-setting leaves |
| `ldexp` wrapper | `[0x00422700,0x00422712)` | 18 | Exact soft-float wrapper |
| Alignment | `[0x00422712,0x00422714)` | 2 | Authenticated retained data |
| `ldexp` VFP core | `[0x00422714,0x00422804)` | 240 | Exact normalization/range helper |
| VFP conversions/arithmetic | `[0x00422804,0x00422872)` | 110 | Seven exact leaves |
| Retained range-error tail | `0x004275D2` | — | Strict reviewed jump target |
| Retained executable successor | `0x00422874` | — | Authenticated executable software frontier |

The prior 16,094-byte retained suffix is split into 584 source bytes, a
two-byte retained alignment and a 15,508-byte retained suffix. Live VFP
exception, range-error and caller-ABI qualification remains blocked by
unavailable authorized evidence.
## Bootloader IAR thread-pointer leaf

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Trailing double-runtime alignment | `[0x00422872,0x00422874)` | 2 | Authenticated retained data |
| Thread-pointer body and anchor literal | `[0x00422874,0x0042287C)` | 8 | Exact in-place Apple/Linux source compilation |
| Returned SRAM anchor | `0x20000518` | — | Authenticated runtime address |
| Retained executable successor | `0x0042287C` | — | Authenticated executable software frontier |

The prior 15,508-byte retained suffix is split into a two-byte alignment,
eight source bytes and a 15,498-byte retained suffix. Physical SRAM-anchor
lifecycle qualification remains blocked by unavailable authorized evidence.
## Bootloader unsigned 64-bit divide/modulo runtime

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Unsigned 64-bit divmod | `[0x0042287C,0x00422AAC)` | 560 | Exact in-place Apple/Linux source compilation |
| Retained divide-by-zero tail | `0x004275E8` | — | Strict reviewed jump target |
| Direct callers | `0x0041F1D0`, `0x0041F1EA`, `0x00422E74` | — | Authenticated start-only ingress |
| Retained executable successor | `0x00422AAC` | — | Authenticated executable software frontier |

The prior 15,498-byte retained suffix is split into 560 source bytes and a
14,938-byte retained suffix. Live divide-by-zero, register-return and caller
ABI qualification remains blocked by unavailable authorized evidence.
## Bootloader atomic snapshot and wrappers

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Atomic three-sample snapshot | `[0x00422AAC,0x00422AC8)` | 28 | Exact in-place Apple/Linux source compilation |
| No-op leaf | `[0x00422AC8,0x00422ACA)` | 2 | Exact in-place source compilation |
| Retained-query wrapper | `[0x00422ACA,0x00422AD2)` | 8 | Exact in-place source compilation |
| Alignment | `[0x00422AD2,0x00422AD4)` | 2 | Authenticated retained data |
| Retained query provider | `0x0041CDB8` | — | Strict reviewed call target |
| Retained executable successor | `0x00422AD4` | — | Authenticated executable software frontier |

The prior 14,938-byte retained suffix is split into 38 source bytes and a
14,900-byte retained suffix. Live interrupt, volatile-sampling and retained-
provider qualification remains blocked by unavailable authorized evidence.

## Bootloader four-instance hardware-service initializer

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Leading alignment | `[0x00422AD2,0x00422AD4)` | 2 | Authenticated retained data |
| Four-instance initializer | `[0x00422AD4,0x00422BA8)` | 212 | Exact in-place Apple/Linux source compilation |
| Instance pool | `0x20024400` | `4 x 0x11C` | Authenticated SRAM base and stride |
| Type/base literal pool | `0x004233E0`, `0x004233E4`, `0x00423430` | 12 | Authenticated retained data |
| Direct caller | `0x0041F744` | — | Authenticated start-only ingress |
| Retained executable successor | `0x00422BA8` | — | Authenticated executable software frontier |

The prior 14,900-byte retained suffix is split into a two-byte alignment, 212
source bytes and a 14,686-byte retained suffix. Live SRAM ownership,
concurrency, peripheral effects and cold-boot lifecycle qualification remains
blocked by unavailable authorized evidence.

## Bootloader instance register-transfer and lifecycle service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Register service | `[0x00422BA8,0x00422D20)` | 376 | Exact in-place Apple/Linux source compilation; five strict calls |
| Revision threshold/register | `0x0016E361` / `0x4002000C` | — | Authenticated retained literals |
| Clock register | `0x400201B0` | — | Revision-gated per-instance bit `0x00400000 << index` |
| Register-bank base | `0x40039000` | `4 x 0x1000` stride | Authenticated MMIO layout |
| Direct callers | `0x0041F66E`, `0x0041F86C`, `0x0041F912` | — | Authenticated start-only ingress |
| Retained executable successor | `0x00422D20` | — | Authenticated executable software frontier |

The prior 14,686-byte retained suffix is split into 376 source bytes and a
14,310-byte retained suffix. Live MMIO/revision/clock/mode/resource/lifecycle
qualification remains blocked by unavailable authorized evidence.

## Bootloader per-instance register-clear leaves

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Primary clear | `[0x00422D20,0x00422D4C)` | 44 | Exact relocation-free Apple/Linux source compilation |
| Secondary clear | `[0x00422D4C,0x00422D7A)` | 46 | Exact relocation-free Apple/Linux source compilation |
| Retained datum | `[0x00422D7A,0x00422D7E)` | 4 | Authenticated non-executable data |
| Register-bank base | `0x40039000` | `4 x 0x1000` stride | Authenticated MMIO layout |
| Retained executable successor | `0x00422D7E` | — | Authenticated executable software frontier |

The prior 14,310-byte retained suffix is split into 90 source bytes and a
14,220-byte retained suffix. Live MMIO/bank/peripheral/cold-boot qualification
remains blocked by unavailable authorized evidence.

## Bootloader per-instance status mapper

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Retained datum | `[0x00422D7A,0x00422D7E)` | 4 | Authenticated non-executable data |
| Status mapper | `[0x00422D7E,0x00422DC6)` | 72 | Exact relocation-free Apple/Linux source compilation |
| Register-bank base | `0x40039000` | `4 x 0x1000` stride | Reads register offset `0x3C` |
| Result pools | `0x00423768..0x00423778`, `0x0042382C` | 24 | Authenticated retained status literals |
| Retained executable successor | `0x00422DC6` | — | Authenticated executable software frontier |

The prior 14,220-byte retained suffix is split into a four-byte datum, 72
source bytes, and a 14,144-byte retained suffix. Live MMIO/status/bank/timing
qualification remains blocked by unavailable authorized responsive evidence.

## Bootloader per-instance register services

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Register OR | `[0x004236CE,0x004236FA)` | 44 | Exact relocation-free Apple/Linux source compilation |
| Alignment and literal | `[0x004236FA,0x00423700)` | 6 | Authenticated retained data |
| Register write | `[0x00423700,0x0042372A)` | 42 | Exact relocation-free Apple/Linux source compilation |
| Register query | `[0x0042372A,0x00423764)` | 58 | Exact relocation-free Apple/Linux source compilation |
| Register/literal table | `[0x00423764,0x0042377C)` | 24 | Authenticated retained data |
| Retained executable successor | `0x0042377C` | — | Next executable body after the cluster |

The source-owned services use the authenticated `0x40039000` register base,
`0x1000` bank stride, instance type, and `+0x38/+0x3C/+0x40/+0x44` offsets.
Live register/MMIO/concurrency/peripheral qualification remains blocked by
unavailable authorized responsive evidence.

## Bootloader per-instance service dispatcher

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Service dispatcher | `[0x0042377C,0x0042382C)` | 176 | Exact Apple/Linux source compilation; six strict calls |
| Literal/status table | `[0x0042382C,0x00423864)` | 56 | Authenticated retained data |
| Retained executable successor | `0x00423864` | — | Next executable body after the cluster |

The source-owned dispatcher preserves the authenticated active/inactive flag
routing, register-relative progress, callback status/context, state cleanup,
and progress latch. Live interrupt/register/callback/concurrency/MMIO
qualification remains blocked by unavailable authorized responsive evidence.

## Bootloader bounded memory-exchange helpers

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Literal/status table | `[0x0042382C,0x00423864)` | 56 | Authenticated retained data |
| Two-buffer exchange | `[0x00423864,0x004238BA)` | 86 | Exact Apple/Linux source compilation; three strict copy calls |
| Three-buffer rotation | `[0x004238BA,0x00423928)` | 110 | Exact Apple/Linux source compilation; four strict copy calls |
| Retained executable successor | `0x00423928` | — | Next executable body after the cluster |

The helpers exchange directly below 64 bytes and use bounded 128-byte scratch
chunks for larger elements. They are software-only; no hardware operation is
required for their completed offline qualification.

## Bootloader rotate-to-front helper

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Rotate-to-front | `[0x00423928,0x00423972)` | 74 | Exact Apple/Linux source compilation; two copy and one overlap-safe move call |
| Retained executable successor | `0x00423972` | — | Next executable body after the helper |

The helper shifts the intervening span right and brings the last width-byte
element to the front in bounded 128-byte chunks. It is software-only.

## Bootloader three-element comparator/exchange helper

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Comparator/exchange | `[0x00423972,0x004239C2)` | 80 | Exact Apple/Linux source compilation; two strict calls and one authenticated fixed tail branch |
| Retained executable successor | `0x004239C2` | — | Next executable body after the helper |

## Bootloader Floyd max-heap sift helper

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Floyd max-heap sift | `[0x004239C2,0x00423A48)` | 134 | Exact Apple/Linux source compilation; two strict exchange calls |
| Retained executable successor | `0x00423A48` | — | Next executable body after the helper |

## Bootloader introspective qsort runtime

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Introspective sort core | `[0x00423A48,0x00423D08)` | 704 | Exact Apple/Linux source compilation; sampled partition, heap fallback, insertion finish |
| Public qsort wrapper | `[0x00423D08,0x00423D20)` | 24 | Exact Apple/Linux source compilation; fixed-address core call |
| Retained executable successor | `0x00423D20` | — | Next executable body after the runtime |

## Bootloader global hardware-control services

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Global service | `[0x00423D20,0x00423D58)` | 56 | Exact Apple/Linux source compilation; register/debug calls |
| Initializer | `[0x00423D58,0x00423D7A)` | 34 | Exact Apple/Linux source compilation; fixed sibling calls and delay |
| Register query | `[0x00423D7A,0x00423D9A)` | 32 | Exact Apple/Linux source compilation |
| Register literal/alignment | `[0x00423D9A,0x00423DA0)` | 6 | Authenticated retained data |
| Indexed test and wrapper | `[0x00423DA0,0x00423DCE)` | 46 | Exact Apple/Linux source compilation |
| Alignment | `[0x00423DCE,0x00423DD0)` | 2 | Authenticated retained alignment |
| Interrupt-atomic control | `[0x00423DD0,0x00423E0C)` | 60 | Exact Apple/Linux source compilation |
| SRAM literals | `[0x00423E0C,0x00423E14)` | 8 | Authenticated retained data |
| Hardware-control state mapper | `[0x00423E14,0x00423E40)` | 44 | Exact Apple/Linux source compilation; state transition and flag mapping |
| MSPI FIFO write | `[0x00423E40,0x00423E8A)` | 74 | Exact Apple/Linux source compilation; one retained status-check call |
| MSPI FIFO read | `[0x00423E8A,0x00423F28)` | 158 | Exact Apple/Linux source compilation; word/remainder paths and two retained status-check calls |
| MSPI command-queue init | `[0x00423F28,0x00423F54)` | 44 | Exact Apple/Linux source compilation; retained `am_hal_cmdq_init` seam |
| MSPI command-queue term | `[0x00423F54,0x00423F8E)` | 58 | Exact Apple/Linux source compilation; force termination and handle clear |
| MSPI command-queue enable | `[0x00423F8E,0x00423FAC)` | 30 | Exact Apple/Linux source compilation; source-owned clock route plus retained enable seam |
| MSPI command-queue disable | `[0x00423FAC,0x00423FB8)` | 12 | Exact Apple/Linux source compilation; retained disable seam |
| MSPI command-queue pause | `[0x00423FB8,0x0042403E)` | 134 | Exact Apple/Linux source compilation; bounded pause and DMA-idle checks |
| MSPI high-priority DMA programming | `[0x0042403E,0x004240AA)` | 108 | Exact Apple/Linux source compilation; clock request and five ordered DMA-register writes |
| Retained executable successor | `0x004240AA` | — | Next executable body, `sched_hiprio` |

## Bootloader per-instance dual-descriptor initializer

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Descriptor initializer | `[0x00422DC6,0x00422E28)` | 98 | Exact Apple/Linux source compilation; two strict calls |
| Instance descriptors | offsets `0x34`, `0x4C` | `2 x 24` | Optional pair-gated initialization |
| Publication flags | offsets `0xDC`, `0xDD` | 2 | Cleared then independently set after initialization |
| Retained constructor | `0x004275EA` | 24 | Strict reviewed call target |
| Retained signature literal | `0x00423830` | 4 | `0x01EA9E06` low-25-bit header |
| Retained executable successor | `0x00422E28` | — | Authenticated executable software frontier |

The prior 14,144-byte retained suffix is split into 98 source bytes and a
14,046-byte retained suffix. Live descriptor ownership, DMA/controller timing,
buffer lifetime and interrupt qualification remains blocked by unavailable
authorized responsive evidence.

## Bootloader per-instance clock-divider service

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Clock-divider service | `[0x00422E28,0x00422EE2)` | 186 | Exact Apple/Linux source compilation; one strict call |
| Register-bank base | `0x40039000` | `4 x 0x1000` stride | Mode at `0x30`; divider at `0x24`/`0x28` |
| Reference pools | `0x004236FC`, `0x00423834..0x00423848` | 24 | 3/49.152/48/24/12/6 MHz |
| Status pools | `0x00423838`, `0x0042384C` | 8 | Range/invalid-mode statuses |
| Source-owned divmod | `0x0042287C` | — | Strict reviewed call target |
| Retained executable successor | `0x00422EE2` | — | Authenticated executable software frontier |

The prior 14,046-byte retained suffix is split into 186 source bytes and a
13,860-byte retained suffix. Live clock selection, divider MMIO, peripheral
rate and cold-boot qualification remains blocked by unavailable authorized
responsive evidence.

## Bootloader per-instance configuration latch

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Configuration latch | `[0x00422EE2,0x00422F4C)` | 106 | Exact Apple/Linux source compilation; one strict call |
| Instance payload | offsets `0xA0..0xB8`, `0xD4` | 29 | Seven words plus one configuration byte |
| Latch/runtime state | offsets `0x119`, `0xD8`, `0xDE` | 6 | Published latch plus cleared runtime state |
| Retained critical provider | `0x0041B8EC` | — | Saves interrupt token; caller restores `PRIMASK` |
| Retained busy status | `0x00423850` | 4 | `0x08000004` |
| Retained executable successor | `0x00422F4C` | — | Authenticated executable software frontier |

The prior 13,860-byte retained suffix is split into 106 source bytes and a
13,754-byte retained suffix. Live interrupt atomicity, instance ownership,
concurrency, downstream MMIO effects and cold-boot qualification remain
blocked by unavailable authorized responsive evidence.

## Bootloader secondary per-instance configuration latch

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Secondary configuration latch | `[0x00422F4C,0x00422FA2)` | 86 | Exact Apple/Linux source compilation; one strict call |
| Instance payload | offsets `0x64..0x7C`, `0x98` | 29 | Seven words plus one configuration byte |
| Latch/runtime state | offsets `0x11A`, `0x9C` | 5 | Published latch plus cleared runtime word |
| Retained critical provider | `0x0041B8EC` | — | Saves interrupt token; caller restores `PRIMASK` |
| Retained busy status | `0x00423854` | 4 | `0x08000005` |
| Retained executable successor | `0x00422FA2` | — | Authenticated executable software frontier |

The prior 13,754-byte retained suffix is split into 86 source bytes and a
13,668-byte retained suffix. Live interrupt atomicity, secondary-instance
ownership, concurrency, downstream MMIO effects and cold-boot qualification
remain blocked by unavailable authorized responsive evidence.

## Bootloader secondary configuration release

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Secondary release | `[0x00422FA2,0x00422FDE)` | 60 | Exact Apple/Linux source compilation; two strict calls |
| Reset span | instance offsets `0x64..0x9F` | 60 | 56-byte retained memset plus explicit final word clear |
| State gate | instance offset `0x11A` | 1 | Requires one, then clears before reset |
| Retained critical provider | `0x0041B8EC` | — | Saves interrupt token; caller restores `PRIMASK` |
| Retained memset | `0x0041560C` | — | Strict reviewed call target |
| Retained executable successor | `0x00422FDE` | — | Authenticated executable software frontier |

The prior 13,668-byte retained suffix is split into 60 source bytes and a
13,608-byte retained suffix. Live interrupt atomicity, release/latch
concurrency, retained memset ABI, SRAM/MMIO consumers and cold-boot
qualification remain blocked by unavailable authorized responsive evidence.

## Bootloader per-instance hardware shutdown

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Shutdown service | `[0x00422FDE,0x0042308E)` | 176 | Exact Apple/Linux source compilation; four strict calls |
| Register-bank base | `0x40039000` | `4 x 0x1000` stride | Offset `0x30` bits 14/11/9; offset `0x18` bit 3 |
| Delay numerator | `0x00423858` | 4 | `10000000` |
| Source providers | `0x00422D4C`, `0x00422FA2` | — | Secondary register clear and release |
| Retained providers | `0x0041D1C0`, `0x00423342` | — | Delay and hardware shutdown |
| Retained executable successor | `0x0042308E` | — | Authenticated executable software frontier |

The prior 13,608-byte retained suffix is split into 176 source bytes and a
13,432-byte retained suffix. Live MMIO, clock/peripheral state, delay accuracy,
concurrency, provider effects and cold-boot qualification remain blocked by
unavailable authorized responsive evidence.

## Bootloader primary and secondary progress services

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Primary progress | `[0x00423524,0x00423608)` | 228 | Exact Apple/Linux source compilation; four strict calls |
| Secondary progress | `[0x00423608,0x004236CE)` | 198 | Exact Apple/Linux source compilation; four strict calls |
| Retained executable successor | `0x004236CE` | — | Next executable body after the cluster |

Both services preserve the authenticated descriptor/FIFO selection, bounded
count, progress mirror, completion/exhaustion callback and interrupt-token
semantics. Live FIFO/descriptor/interrupt/DMA/callback/concurrency/MMIO
qualification remains blocked by unavailable authorized responsive evidence.

## Bootloader per-instance mode-dispatch services

| Segment | Range | Bytes | State |
|---|---:|---:|---|
| Dispatcher | `[0x004233E8,0x00423430)` | 72 | Exact Apple/Linux source compilation; four strict routes |
| Literal/register-base data | `[0x00423430,0x00423444)` | 20 | Authenticated retained data |
| Mode-zero wait | `[0x00423444,0x0042348E)` | 74 | Exact Apple/Linux source compilation |
| Mode-one wait | `[0x0042348E,0x004234D8)` | 74 | Exact Apple/Linux source compilation |
| Mode-two start | `[0x004234D8,0x004234FA)` | 34 | Exact Apple/Linux source compilation |
| Mode-three start | `[0x004234FA,0x00423524)` | 42 | Exact Apple/Linux source compilation |
| Retained executable successor | `0x00423524` | — | Next executable body after the cluster |

All 296 executable bytes in this cluster are source-compiled. Live latch,
register, timer, interrupt, concurrency and peripheral qualification remains
blocked by unavailable authorized responsive evidence.

## Bootloader per-instance FIFO services

| Segment | Range/address | Bytes | State |
|---|---:|---:|---|
| Retained initializer | `[0x0042308E,0x004232C8)` | 570 | Earliest retained executable software frontier |
| FIFO read | `[0x004232C8,0x0042330E)` | 70 | Exact relocation-free Apple/Linux source compilation |
| FIFO write | `[0x0042330E,0x00423342)` | 52 | Exact relocation-free Apple/Linux source compilation |
| FIFO drain | `[0x00423342,0x00423350)` | 14 | Exact Apple/Linux source compilation; strict read call |
| FIFO snapshot adapter | `[0x00423350,0x00423390)` | 64 | Exact Apple/Linux source compilation; critical/read/consume calls |
| FIFO pump adapter | `[0x00423390,0x004233E0)` | 80 | Exact Apple/Linux source compilation; critical/descriptor/write calls |
| Register-bank base | `0x40039000` | `4 x 0x1000` stride | Status at `0x18`; data at `0x00` |
| Retained data successor | `[0x004233E0,0x004233E8)` | 8 | Two authenticated literal words |

The prior 13,432-byte retained suffix is split into a 570-byte retained body,
280 source bytes, and a 12,582-byte retained suffix. Live FIFO flags/data,
descriptor state, interrupt restoration, MMIO ordering, concurrency and peripheral qualification remain blocked by
unavailable authorized responsive evidence.
