# Upstream library recovery inventory

openCFW classifies each opaque firmware cluster before attempting clean-room
source re-creation. An exact upstream match is vendored or ported under its
original license; focused disassembly recovers only G2 configuration, ABI,
port hooks, and proprietary glue. A family-level match is not assigned a
specific revision until discriminating binary evidence supports it.

The current completion assessment reports zero unclassified bytes, but it does
not report source completion: typed retained/external and unavailable-source
boundaries remain. Historical “opaque” counts below are contemporaneous builder
ownership labels; they map to those classified retained/external boundaries and
must not be read as current unclassified-byte counts.

The current cross-family identity and functional-gap ordering is in
[`research/third-party-utility-gap-priority.md`](research/third-party-utility-gap-priority.md).
The machine-readable origin/version/commit disposition and aggregate closure
checks are in the
[`research/third-party-dependency-closure-audit.md`](research/third-party-dependency-closure-audit.md).

## Strongly identified source candidates

| Library | Recovered identity | Current action |
|---|---|---|
| FreeRTOS Kernel | V10.5.1, commit `def7d2df2b0506d3d249334974f51e427c17a41c` | Reviewed queue/list/task/port boundaries are source-integrated; the selected bounded `heap_4` adapter owns initialization, insertion/coalescing, allocation, and free, `vQueueDelete` closes over source heap free, both tick-count getters bind to a source-owned provider for the recovered `xTickCount` seam, `vTaskMissedYield` binds the recovered `xYieldPending` word, and `xTaskCheckForTimeOut` now closes over source-owned timeout/critical providers; fixed scheduler/hook and remaining queue/task seams stay explicit |
| CMSIS-FreeRTOS | v10.5.1, commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`, exact `cmsis_os2.c` blob first at `13acfbef7be85119fc6bc56832c455d4547d92c7`, with CMSIS_5 5.9.0 at `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` | The complete 43-function linked wrapper object is authenticated, version-bounded, and production source-owned: all 38 public APIs plus private `IRQ_Context`, `TimerCallback`, `CreateBlock`, `AllocBlock`, and `FreeBlock` |
| TLSF | v3.1 source-equivalent range ending at `deff9ab509341f264addbd3c8ada533678591905` | Already vendored and source-integrated |
| littlefs | v2.10.1 source-equivalent release, commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | Core is authenticated and vendored; both images source-integrate the scalar/alignment quartet, exact `LFS_NO_INTRINSICS` fallback-bitops trio, endian-conversion quartet, and sixteen private dual-image leaves including `lfs_alloc_lookahead`, `lfs_tag_chunk`, `lfs_tag_isvalid`, `lfs_tag_type1`, `lfs_tag_type3`, `lfs_tag_id`, and `lfs_tag_size`, while Apollo main also owns `lfs_file_tell_`, `lfs_file_rewind_`, `lfs_file_size_`, and the relocation-free `lfs_tag_type2` scalar helper. The current `lfs_tag_size` promotion passes five focused tests and has closed cross-profile and aggregate build pins; the bounded read-only G2 block port remains gated on an external-flash capture |
| LVGL | G2 uses a hybrid LVGL 9.3.0-development vendor fork: official core history is compatible from `60d976c466e8…` through selected ceiling `344c7c318047…`, while the Ambiq backend is exact subtree `1e774257…` at canonical commit `5be8e0ae…` (byte-identical replay `67fd93e2…`) | The production-excluded official snapshot verifies 65 mapped translation units, 252 headers, MIT license, signed commit, 107 trees, and all blobs offline. Ambiq commits `d4dcd26…`/`925470dd…` explain and wire the 32-byte handler ABI. The recovered config reproduces G2 `lv_global_t==0x1EC`, every internal offset, the Nema backend/VG enables, 100 x 1,024-byte command-list geometry, and retained-context GPU power policy. Production stays fail-closed on stock-IAR/GPU-patch/HAL admission, hardware, display/FreeType system/assets, managers, and Even integration—not on an unexplained ABI or dependency identity. See the [snapshot README](../third_party/lvgl/README.openCFW.md), [Ambiq source/ABI audit](research/lvgl-ambiq-source-abi-recovery-audit.md), and [Nema dependency audit](research/nemagfx-ambiq-g2-provenance-audit.md) |
| NemaGFX / NemaVG / Ambiq GPU patch | AmbiqSuite 5.1.0 revision `release_sdk5p1p0-634f7c117b`; NemaGFX 1.4.12; NemaVG 1.1.8 | Exact 50-file public subtree tree `e690768a…` at reproduction commit `b853fded…`; Apollo5 archive first public at `c6f54a95…`; GPU-patch archive/header first public at `e3eec7f3…`. Stock independently forces the NemaGFX 1.4.12 floor. All 11 patch exports / 4,232 exact section bytes and all 18 stock bare-metal HAL functions / 614 bytes are source-qualified. The no-argument/global-context `draw_start_cap`, `draw_end_cap`, and `draw_caps` entries are all production-routed over 6,614 stock bytes; zero stroke-cap endpoint bytes remain retained or candidate-only. Public HAL ancestry begins on the package lineage at `4e7d4276…`, but the public files are Zephyr ports rather than stock-generating source. The original IAR/private HAL commits, remaining internal Nema source, bare-metal HAL binding, and authorized hardware validation remain explicit boundaries. |
| Google liblc3 | Tagged v1.1.3 baseline, commit `96a3af0beb5487aca3b98a4b992a539a1f6d80d1`; stock-compatible public interval `bb85f7d…1de85e2`, with `9f1e206…` excluded | A byte-identical 38-file Apache-2.0 snapshot is admitted. Four public entries and five `service_audio.c` calls authenticate the linked encoder; SNS `FLT_MAX` supplies the lower bound and the byte-0/1/2 encoder layout supplies the upper bound. The exact producing checkout is unobservable because the post-v1.1.3 compatible delta affects a dead-stripped misspelled API. Target build/performance, buffer integration, and interoperability remain gated. See the [snapshot README](../third_party/liblc3/README.openCFW.md) and [source recovery](research/g2-liblc3-source-recovery.md). |
| FreeType | **2.9.1**, official annotated tag object `ad55868d889b6ba8d2aed846b4b4b460f8a83e42`, peeled commit `86bc8a95056c97a810986434a3f268cbe67f2902` | The unchanged FTL and 297 byte-exact source files are authenticated offline; a recovered header pins the ten-module G2 order, and focused audits prove v40/minimal TrueType, substantive GX variation services, the `am_ftsystem.c` allocator and constructor seams, plus exact `FT_Done_Face` at `[0x00526814,0x0052687E)` and its caller closure. Whole-image branch/pointer evidence shows the conventional `FT_Done_FreeType` topology is absent, so no entry may be assigned safely and this is not a remaining linked-function gap. Remaining unknowns are other configuration toggles, exact IAR compiler/linker details, and external font asset identities, payloads, and runtime arrays. The snapshot remains production-excluded pending explicit source-configuration and promotion review. See the [snapshot audit](research/freetype-2.9.1-snapshot-audit.md) and [binary recovery audit](research/freetype-recovery-audit.md) |
| FlashDB | 2.1.1 (armink), lightweight tag/commit `2.1.1` / `714d6159e7e6afb267a3953756abca445c350e61` | The selected 14-file Apache-2.0 KVDB/FAL snapshot is byte-exact to the official tag and verified offline; this is an openCFW compatibility selection, not proof that Even used the checkout unchanged. The analyzer authenticates the 1-bit write granularity, 4-KiB sectors, 64-entry caches, short-enum `0x8AC` object ABI, partitions, callbacks, and `sysenv@kvdb` / `factory@NVdb` bindings. All 21 default values are recovered, including zero-initialized `kvbooCount`; its persisted read/increment/write lifecycle and eleven record migrations are bounded. A production-excluded port matches upstream partition reads, preserves the shared CMSIS mutex, maps every nonzero MX25 result to `-1`, and denies write/erase. Production admission still waits for a golden capture, non-destructive mount policy, and schema semantics. See the [snapshot README](../third_party/flashdb/README.openCFW.md), [configuration audit](research/flashdb-configuration-recovery-audit.md), [system-KVDB recovery](research/g2-service-kvdb-recovery.md), and [read-only port audit](research/flashdb-readonly-port-source-candidate-audit.md) |
| EasyLogger | `2.2.99` source-equivalent core from `cd93d9c768415f4b7279f2d3ef2366ce15ea087c` through vendored `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; no upstream tag | Main control/filter/output/hexdump paths and the shared four-helper quartet are source-integrated. The bootloader production-routes its ten-entry control cluster, complete 115-caller interrupt-gated `elog_output`, output-lock-enable transition, all eleven mutex/time/task-info boot-port entries, and the G2-specific channel-one driver/four-channel descriptor transport under dual-profile pins. `elog_async_api.c` is proven downstream G2 code; its clean-room queue/worker implementation remains production-excluded. Live concurrency, DMA/interrupt completion, and hardware stress remain explicit physical-evidence boundaries. |
| G2 bootloader delay and initializer services | No separate upstream dependency; first-party Even compatibility boundary | Four complete entries / 102 stock executable bytes at `[0x0041F9D8,0x0041FA40)` are production-routed to 96 relocation-free clean-room Thumb bytes. The delay seams, initializer table and scratch addresses, sort ABI, stored comparator pointer, 256-record cap, and callback dispatch are authenticated. Host, Cortex-M55, dual-profile, routing, package, and flash-plan gates pass; live timing, callback effects, and cold-boot validation are blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [source closure](research/g2-bootloader-boot-services-41f9d8-41fa40-source-closure.md). |
| G2 bootloader guarded teardown | No separate upstream dependency; first-party Even compatibility boundary | The complete 56-byte entry at `[0x0041FA98,0x0041FAD0)` is production-routed to one 72-byte relocation-free clean-room leaf. Exact guard/state addresses, two status stages, fail-stop policy, pin-28 configuration, sole caller, and literal pool are authenticated. Host, Cortex-M55, dual-profile, routing, package, and flash-plan gates pass; live pin/power/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [source closure](research/g2-bootloader-guarded-teardown-41fa98-41fad0-source-closure.md). |
| G2 bootloader platform setup | No separate upstream dependency; first-party Even compatibility boundary | The complete 72-byte entry at `[0x0041FA50,0x0041FA98)` is production-routed to one 96-byte relocation-free clean-room leaf. Guarded teardown, reset/mode calls, hard-float `25.0f` derive ABI, 20-byte stock configuration copy/submit, channels four/five, and the sole caller are authenticated. Host, Cortex-M55, dual-profile, routing, package, and flash-plan gates pass; live configuration/channel/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [source closure](research/g2-bootloader-platform-setup-41fa50-41fa98-source-closure.md). |
| G2 bootloader pin-group dispatcher | No separate upstream dependency; first-party Even compatibility boundary | The complete 538-byte entry at `[0x0041FADC,0x0041FCF6)` is production-routed to one 428-byte relocation-free clean-room leaf. Two-bank subtype fall-through, 30 SRAM configuration-word references, ordered pin numbers, no-op cases, and both callers are authenticated. Host, Cortex-M55, dual-profile, routing, package, and flash-plan gates pass; live pinmux/GPIO/electrical validation is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [source closure](research/g2-bootloader-pin-groups-41fadc-41fcf6-source-closure.md). |
| G2 bootloader allocator initializer | No separate upstream dependency; first-party Even compatibility boundary using the retained TLSF v3.1 provider | The complete 56-byte entry at `[0x0041FD70,0x0041FDA8)` is production-routed to one 88-byte relocation-free clean-room leaf. Pool clear/size/address, TLSF create call, handle publication, diagnostic record, return, sole caller, and adjacent literals are authenticated. Host, Cortex-M55, dual-profile, routing, package, and flash-plan gates pass; live allocator/SRAM/logging/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [source closure](research/g2-bootloader-allocator-init-41fd70-41fda8-source-closure.md). |
| G2 bootloader IRQ services | CMSIS-compatible NVIC semantics plus retained AmbiqSuite 5.1.0 MSPI HAL seams; clean-room first-party wrappers | Three complete entries / 104 bytes at `[0x0041FDC0,0x0041FE28)` are production-routed to 112 relocation-free clean-room Thumb bytes. Signed IRQ gating, register/index arithmetic, external/system priority choice, MSPI handle/status/order, two direct callers, and vector ingress are authenticated. Host, Cortex-M55, dual-profile, routing, package, and flash-plan gates pass; live NVIC/MSPI validation is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [source closure](research/g2-bootloader-irq-services-41fdc0-41fe28-source-closure.md). |
| G2 bootloader MSPI controls | Retained AmbiqSuite 5.1.0 MSPI control seam; clean-room first-party wrappers | The complete 58-byte enable/disable pair `[0x0041FE28,0x0041FE62)` is routed to 64 relocation-free Thumb bytes. Active-state idempotence, handle/mode/flag arguments, state updates, and all callers are authenticated; live MSPI validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-control-41fe28-41fe62-source-closure.md). |
| G2 bootloader event-flags service | CMSIS-compatible retained create/acquire/release and EasyLogger seams; clean-room first-party wrappers | The complete 166-byte init/acquire/release cluster `[0x0041FE62,0x0041FF08)` is routed to 208 relocation-free Thumb bytes. Handle/config addresses, null guards, wait-forever timeout, error policy, exact diagnostics, and all callers are authenticated; live RTOS/contention/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-event-flags-service-41fe62-41ff08-source-closure.md). |
| G2 bootloader MSPI guards | Retained event-flags and MSPI control seams; clean-room first-party paired wrappers | The complete 44-byte pair `[0x0041FF08,0x0041FF34)` is routed to 68 relocation-free Thumb bytes. The `0x200271C5` bypass byte, six direct callers, conditional MSPI transitions, and acquire/disable versus enable/release order are authenticated; live contention/MSPI/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-guard-41ff08-41ff34-source-closure.md). |
| G2 bootloader MSPI XIP configuration | Retained MSPI handle/configuration and control seam; clean-room first-party updater | The complete 44-byte entry `[0x0041FF34,0x0041FF60)` is routed to a 36-byte relocation-free Thumb leaf. The selector-dependent write to config byte five, request 16, handle/config addresses, ignored status, and three callers are authenticated; live XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-xip-config-41ff34-41ff60-source-closure.md). |
| G2 bootloader bit-run helpers | Clean-room first-party scalar reconstruction | The complete 162-byte pair `[0x0041FF60,0x00420002)` is routed to relocation-free run-length and center-selection leaves. Stock bodies/callers and exact behavior across boundary plus deterministic random words are pinned; live training-mask meaning, timing, and cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-bit-run-helpers-41ff60-420002-source-closure.md). |
| G2 bootloader MSPI timing scan | Retained AmbiqSuite-compatible MSPI control/read-ID seams plus clean-room first-party scan | The complete 440-byte entry `[0x00420002,0x004201BA)` is routed to a 420-byte strict-relocation leaf. Stock seams, all 1,152 candidates, pass-mask construction, first-longest row selection, center helper, result bytes, and diagnostics are pinned; live signal-integrity, external-flash, XIP, and cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-timing-scan-420002-4201ba-source-closure.md). |
| G2 bootloader automatic MSPI timing selection | Clean-room first-party wrapper over the source-owned exhaustive scan and retained EasyLogger seam | The complete 154-byte entry `[0x004201BA,0x00420254)` is routed to a strict one-relocation leaf. Zero initialization, six-byte success publication, failure preservation, both diagnostic branches, and adjacent-byte safety are pinned; live signal-integrity, external-flash, XIP, and cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-timing-auto-4201ba-420254-source-closure.md). |
| G2 bootloader low-level MSPI initializer | Clean-room first-party orchestration over retained Ambiq-compatible HAL/EasyLogger seams and source-owned XIP, pin-group, and NVIC helpers | The complete 546-byte entry `[0x00420254,0x00420476)` is routed to a four-relocation 492-byte leaf. Busy-state rejection, HAL order, default/custom configuration, cleanup, TCB/pin/interrupt settings, publication, and diagnostics are pinned; live HAL/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-low-level-init-420254-420476-source-closure.md). |
| G2 bootloader MX25U25643G public initializer | Clean-room first-party orchestration over retained device/JEDEC helpers and source-owned MSPI services | The complete 180-byte entry `[0x00420476,0x0042052A)` is routed to a five-relocation 204-byte leaf. Initialization failure, delay, timing selection, JEDEC-ID logging, final mode/service setup, and return policy are pinned; live JEDEC/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-driver-init-420476-42052a-source-closure.md). |
| G2 bootloader MX25U25643G soft reset | Clean-room first-party command sequencing over retained command/logger seams and source-owned delay | The complete 116-byte entry `[0x0042052A,0x0042059E)` is routed to a 136-byte leaf. Reset-enable/reset commands, delays, failure-only diagnostics, and continuation policy are pinned; live reset/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-soft-reset-42052a-42059e-source-closure.md). |
| G2 bootloader MX25U25643G JEDEC-ID reader | Clean-room first-party command, error, and byte-packing implementation over retained transaction/logger seams | The complete 86-byte entry `[0x0042059E,0x004205F4)` is routed to a relocation-free 100-byte leaf. Command `0x9F`, three-byte receive, failure output preservation, diagnostics, and big-endian packing are pinned; live JEDEC/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-read-id-42059e-4205f4-source-closure.md). |
| G2 bootloader MX25U25643G read-transfer wrapper | Clean-room first-party validation and descriptor orchestration over retained Ambiq blocking-transfer and source-routed logging seams | The complete 170-byte entry `[0x004205F4,0x0042069E)` is routed to a relocation-free 172-byte leaf. Status mapping, 25-bit address bound, exact 24-byte descriptor, timeout, five callers, HAL status, and failure diagnostics are pinned; live HAL/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-read-transfer-4205f4-42069e-source-closure.md). |
| G2 bootloader MX25U25643G write-transfer wrapper | Clean-room first-party validation and descriptor orchestration over retained Ambiq blocking-transfer and source-routed logging seams | The complete 176-byte entry `[0x0042069E,0x0042074E)` is routed to a relocation-free 148-byte leaf. Status mapping, address and 256-byte length ceilings, exact 24-byte write descriptor, timeout, eight callers, HAL status, and failure diagnostics are pinned; live HAL/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-write-transfer-42069e-42074e-source-closure.md). |
| G2 bootloader MX25U25643G busy-status reader | Clean-room first-party status-register orchestration over the source-routed read-transfer and logging seams | The complete 84-byte entry `[0x0042074E,0x004207A2)` is routed to a relocation-free 88-byte leaf under both profiles. Command `0x05`, zeroed scratch bytes, one-byte transfer, raw failure status and diagnostic, bit-7 Boolean result, and both callers are pinned; live HAL/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-busy-status-42074e-4207a2-source-closure.md). |
| G2 bootloader MX25U25643G ready polling | Clean-room first-party two-phase polling over source-routed context, notification, delay, and status seams | The complete 94-byte cluster `[0x004207A2,0x00420800)` is routed to dependency-free 88- and 12-byte leaves. The 200-poll fast phase, five-unit backoff, caller-bounded context-aware phase, fixed bound 500, return policy, and all callers are pinned; live RTOS/timing/MSPI/XIP/external-flash/cold-boot validation is blocked by unavailable physical evidence; future qualification requires authorized hardware. See the [source closure](research/g2-bootloader-mspi-wait-ready-4207a2-420800-source-closure.md). |
| G2 bootloader MX25U25643G address-mode reading | Clean-room first-party command `0x15` register read and bit-5 decoder | The complete 108-byte body `[0x00420800,0x0042086C)` routes to a relocation-free 124-byte leaf on both reviewed toolchains. Raw transport errors, the sole caller, and both diagnostics are pinned; live MSPI/external-flash/cold-boot validation is blocked by unavailable physical evidence and requires future authorized hardware evidence. See the [source closure](research/g2-bootloader-mspi-4byte-mode-420800-42086c-source-closure.md). |
| G2 bootloader MX25U25643G enter-four-byte-mode | Clean-room first-party `0xB7` command state machine over source-routed ready-poll, address-mode, and retained write-latch seams | The complete 232-byte body `[0x00420890,0x00420978)` routes to a relocation-free 220-byte leaf on both reviewed toolchains. Handle/busy mappings, raw error propagation, command, ignored post-command poll, permissive verification quirk, write-disable, sole caller, and diagnostics are pinned; live MSPI/external-flash/XIP/cold-boot validation is blocked by unavailable physical evidence and requires future authorized hardware evidence. See the [source closure](research/g2-bootloader-mspi-enter-4byte-mode-420890-420978-source-closure.md). |
| G2 bootloader MX25U25643G write-latch commands | Clean-room first-party command `0x06` / `0x04` wrappers over the source-routed write-transfer seam | The complete 58-byte write-enable and 56-byte write-disable bodies route to relocation-free 72-byte leaves on both reviewed toolchains. All seven callers, zeroed transfer fields, raw statuses, and exact failure-only diagnostics are pinned; three surrounding literal pools remain authenticated retained data, and live MSPI/external-flash/XIP/cold-boot validation is blocked by unavailable physical evidence and requires future authorized hardware evidence. See the [source closure](research/g2-bootloader-mspi-write-latch-420984-4209fc-source-closure.md). |
| G2 bootloader MX25U25643G sector erase | Clean-room first-party guarded command `0x20` service over source-routed ready-poll, write-latch, transfer, guard, and mode seams | The complete 210-byte body `[0x00420A08,0x00420ADA)` routes to a relocation-free 244-byte leaf on both reviewed toolchains. Handle, 4-KiB alignment, 32-MiB bound, all failure mappings, diagnostic arguments, cleanup order, transfer tuple, and sole caller are pinned; live erase/MSPI/external-flash/XIP/cold-boot validation is blocked by unavailable physical evidence and requires future authorized hardware evidence. See the [source closure](research/g2-bootloader-mspi-sector-erase-420a08-420ada-source-closure.md). |
| G2 bootloader MX25U25643G page program | Clean-room first-party guarded command `0x02` service over source-routed ready-poll, write-latch, transfer, guard, and mode seams | The complete 264-byte body `[0x00420B0C,0x00420C14)` routes to the same relocation-free 256-byte leaf on both reviewed toolchains. Handle/buffer/length validation, 32-MiB bound, 256-byte page splitting, address/buffer advancement, all failure mappings, diagnostics, cleanup, transfer tuples, and sole caller are pinned; live programming/MSPI/external-flash/XIP/cold-boot validation is blocked by unavailable physical evidence and requires future authorized hardware evidence. See the [source closure](research/g2-bootloader-mspi-program-420b0c-420c14-source-closure.md). |
| G2 bootloader MX25U25643G QE configuration | Clean-room first-party status-register-2 read/update/verify service over source-routed ready, write-enable, and transfer seams | The complete 414-byte body `[0x00420C5C,0x00420DFA)` routes to the same relocation-free 364-byte leaf on both reviewed toolchains. Fixed-handle rejection, commands `0x05`/`0x01`, QE bit 6, protection mask `0x3C`, ignored waits, raw failures, verification, diagnostics, non-Boolean low-byte behavior, and sole caller are pinned; live QE/MSPI/external-flash/XIP/cold-boot validation is blocked by unavailable physical evidence and requires future authorized hardware evidence. See the [source closure](research/g2-bootloader-mspi-quad-enable-420c5c-420dfa-source-closure.md). |
| mpaland/printf | `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e` | All linked reverse-output, integer, float, exponential, string, variadic-core, public-wrapper, and G2 `%PV`/`%pV` extension behavior is production source-owned. Only the binary-unobservable historical checkout remains; there is no linked functional gap. |
| AmbiqSuite | 5.1.0-lineage Apollo510 source at public replay commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`, with CMSIS Core pinned at `d23a6949a0331ca96853bcd98b0fdcc4db47184c` | The licensed Apollo510/CMSIS MSPI closure is vendored; both production overlays retain the exact-upstream interrupt-clear leaf. The complete stock system-sleep body adds a decisive version proof: its two WFI operations match 5.1.0 and exclude 5.0.0. Independent I2S and PDM consumers map 24 public HAL APIs to the same replay; the PDM source is pinned to Git blob `23a440bf…`. The stock build predates the public import, so the private pre-release generating commit remains unavailable; see the [product RTOS recovery](research/g2-product-rtos-recovery.md) and [PDM recovery](research/g2-drv-pdm-production-recovery.md) |
| AmbiqSuite ANCC profile | 2.2.0-4.5.0 implementation-equivalent ANCS client; selected 2.5.1 public import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` | Exact BSD-licensed 17-definition source/header admitted as the oracle. G2's 21-function object retains 12 Ambiq-derived bodies and adds nine bounded message/sync/whitelist adapters; all 21 entries are now production-routed from maintained C with the exact SRAM ABI and hardened fragmented parser. The source-identical interval still prevents recovery of one private producing commit. Live ANCS/controller/dual-temple validation is blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. See the [ANCC source recovery](research/ambiqsuite-ancc-profile-source-recovery.md) |
| AmbiqSuite AMOTA profile | 2.2.0-2.5.1 stable application skeleton; selected 2.5.1 public import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` | Exact BSD-licensed 2.5.1 application/API oracle admitted. G2 OTA retains the CCC, A0/A1 event, initializer, and handler skeleton across four functions while three actions are product-local. The binary cannot select one changed release file or private commit. See the [OTA/Ring recovery](research/g2-ble-ota-ring-profiles-recovery.md) |
| Goodix GR551x application-error utility | SDK 1.7.0 byte-exact `components/libraries/app_error/app_error.c` snapshot, blob `d5027735dd01b0948a7315d9c595356fcb91f59b`; first located incompatible version 2.0.1 | G2's `utils/assert` handler and 43-row table are copied/adapted source. Selected earliest public carrier `854c43e0b96a24051ffce4c06ff629255aa56c59` is not claimed as an official release or Even checkout. The utility is source-closed, production-excluded, and does not imply a linked Goodix BLE stack. See the [Goodix utility recovery](research/g2-util-error-check-goodix-recovery.md) and [provenance](../third_party/goodix-gr551x-app-error/PROVENANCE.json) |
| G2 EUS/ESS/EFS/NUS profile boundary | No separate upstream dependency | Four contiguous first-party Cordio adapters are authenticated across 25 linked functions / 2,698 body bytes / 3,000 physical bytes and are production-routed from clean-room C. AmbiqSuite has no matching profiles and Nordic `ble_nus_*` does not match the G2 NUS API. Physical peer validation is blocked by unavailable physical evidence; future qualification requires authorized responsive evidence. See the [profile recovery](research/g2-ble-transport-profiles-recovery.md) |
| CmBacktrace | armink CmBacktrace, compatible with unmodified upstream interval `4abadfa0…73714489` on the untagged post-1.4.1 line advertising `1.4.2`; no exact vendor commit is proven | FreeRTOS, stack dumping, IAR `.out`, depths 32/16, name limit 40, M33-class effective behavior, exact init arguments, and the 39-entry message table are recovered. Upstream `55e7b69` and later are excluded because G2 lacks its stacked-xPSR fix. A production-excluded seven-file **MIT** snapshot selects `73714489` as an explicit openCFW compatibility choice and verifies its commit, six tree objects, and blobs offline; see the [snapshot README](../third_party/cmbacktrace/README.openCFW.md) and [version/configuration audit](research/cmbacktrace-version-recovery-audit.md) |
| AndersKaloer/Ring-Buffer | Dynamic-buffer source-equivalent interval `cda00e1efb815bad5100757f0d10d117f633ced6`…`190e30bebcec22d7311fd941179d70b4f439c441`; selected compatibility commit `190e30b` | Exact assertion, 16-byte ABI, seven-function control flow, overwrite-oldest policy, all boundaries, and direct callers are authenticated. All seven live entries are production-integrated as 248 source bytes plus four alignment bytes; Linux replay remains pending. See the [snapshot README](../third_party/ring-buffer/README.openCFW.md) and [lineage audit](research/ring-buffer-lineage-recovery-audit.md) |
| TinyFrame | Exact core blobs introduced by `eb75483e035916ef9f3e9fce0d2ae389cb09785f`; historical checkout interval ends at core-identical `a29167a69f052975b0e0134a73b4d31d03afa8fa` | The MIT snapshot, license, recovered G2 config, `-fshort-enums` ABI, pristine `0x7158` core, and `0x7160` magic-extended layout are authenticated offline and compile-tested for Cortex-M55. All 31 linked functions / 2,994 code bytes and the 124-byte non-executable pool are accounted for. The separate adapter closes the one-instance role census and bookended layout without modifying upstream. Production atomically routes eight public entries over a 14-function live graph, uses source-owned `heap_4`, retains the authenticated first-party sync wrapper at `0x00541790`, and selects no-op diagnostics. Placement, ownership, and Apple/Linux roots are pinned; only hardware golden frames remain. See the [snapshot README](../third_party/tinyframe/README.openCFW.md), [send/version audit](research/tinyframe-send-version-recovery-audit.md), and [source-admission audit](research/tinyframe-source-admission-boundary-audit.md) |
| DaveGamble cJSON | Version interval v1.7.9–v1.7.12 from four binary discriminators: the ≥1.7.9 issue-#315 `get_object_item` fix, the <1.7.13 `buffer_skip_whitespace` offset behavior, the absent <1.7.14 `parse_array`/`parse_object` `head->prev` tail store, and the <1.7.19 64-byte stack `parse_number` buffer | An authenticated pristine three-file **MIT** snapshot selects ceiling tag v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`) as an explicit openCFW compatibility baseline — not proof of the vendor checkout. All 21 linked parse-side functions are re-verified byte-identical C text across the interval; the whole-file tag diff is confined to dead-stripped print/create/edit/utils code. The parser shared by `service_android_notify.c` and `service_whitelist.c` was bounded as 21 functions / 2,572 stock body bytes at `[0x004D798C,0x004D83D8)`. It is now **production-routed** through maintained freestanding C: all 21 entries, strict branch and relocation contracts, fixed allocator/error SRAM ABI, dual Apple/Linux compiler payload pins (2,442/2,434 bytes), and zero undefined runtime symbols or hardware operations are verified. Live caller behavior on the product remains blocked by unavailable physical evidence. See the [source-candidate and admission audit](research/g2-json-parser-source-candidate-audit.md) and [snapshot README](../third_party/cJSON/README.openCFW.md) |

Every third-party family embedded in the G2 `2.2.6.10` build tree is now
identified: FreeRTOS-Kernel, FreeRTOS-Plus-CLI, littlefs, TLSF, EasyLogger,
TinyFrame, Cordio/Packetcraft, LVGL v9.3 (with its bundled FreeType 2.9.1,
NemaGFX 1.4.12, NemaVG 1.1.8, the Ambiq GPU patch, an LZ4-family
decompressor, and `bin_decoder`/`bmp`/`fsdrv`), Google liblc3 v1.1.3-era,
FlashDB 2.1.1,
nanopb (compatible with pristine upstream 0.4.7–0.4.9),
mpaland/printf, AmbiqSuite 5.1.0 / CMSIS, the AmbiqSuite ANCC and AMOTA clients,
the copied Goodix GR551x 1.7.0 application-error helper, the generic `ringBuffer`,
DaveGamble cJSON v1.7.9–v1.7.12 (snapshot admitted at ceiling tag v1.7.12,
production-excluded), and
CmBacktrace. The remaining source-unavailable retained/external bytes include
first-party Even code (`platform`/`app`/`framework`/`driver`/`product`/`service`, including the
proprietary `fw_event_loop`, audio DSP, and application services). The formerly
speculative cryptographic-backend boundary is now identified as Packetcraft
Cordio r20.05c `sec_api`; its 20 service functions are production-routed from
Apache-2.0 source while HCI/controller primitives remain the explicit hardware
boundary. See the [security API recovery](research/cordio-sec-api-source-recovery.md).

The authenticated whole-image [embedded source-path census](research/apollo-embedded-source-path-census.md)
closes the retained-path lower bound: 357 unique C paths comprise 123
`third_party` markers across seven already inventoried directory families and
234 project/first-party markers. Lorelei corpus correlation anchors 530
functions to those third-party paths and 1,230 to project/first-party paths;
43 paths and 5,610 discovered functions remain unanchored. Absence from this
set is not evidence that a library was not linked, so families such as LZ4,
nanopb, FlashDB, FreeRTOS, and compiler runtime continue to rely on their
independent binary/version proofs.

Every vendored import must pin its revision or defensible source-equivalent
range, preserve its license and notices, record unmodified-file hashes, and
keep G2-specific changes in a separate port or patch layer.

## FreeRTOS-Kernel V10.5.1 authenticated release

`third_party/freertos-kernel` preserves 49 official upstream files from
annotated tag object `d7b40dbed508c305c2a32ccf3982045ec9ba8734`, peeled
commit `def7d2df2b0506d3d249334974f51e427c17a41c`, and tree
`7496dfa815c3cea2f45a090c6e92d113f494b930`. The tag is not
cryptographically signed. Authentication therefore pins the official
repository/ref identities and every selected file by byte count, Git blob
SHA-1, and SHA-256.

The snapshot includes all seven kernel implementation units, all 19 released
headers, the common MPU wrapper, and both complete released IAR Cortex-M55
port alternatives: `ARM_CM55` and `ARM_CM55_NTZ`. It also preserves exact
`portable/MemMang/heap_4.c`, 20,608 CRLF bytes with SHA-256
`d48a51e34caed771e6650d95f6c2527e52fde2a6ebc6f83b49d003aef0135e05`
and Git blob `3af0caf2b60fc4adfb103a115fefbf1b09b21dd8`, as the authenticated MIT
algorithm reference for the selected bounded G2 adapter. The pristine snapshot
does not itself supply G2 selection or placement. The port alternatives
must not be linked together. Focused instruction comparison unequivocally selects
`portable/IAR/ARM_CM55_NTZ/non_secure` with TrustZone and MPU disabled and
FPU context support enabled. The recovered port uses `BASEPRI=0x30`, Apollo
STIMER compare A on IRQ 32, a 1,024-Hz tick derived from 32.768 kHz / 32, and
tickless idle. The kernel has 56 priorities, 32-byte task names, static and
dynamic allocation, timers, mutexes, notifications, trace fields, and a
`heap_4`-shaped `0x2F000`-byte heap at `0x20004558`.

This is not permission to link pristine `tasks.c`: the exact 112-byte G2 TCB
stores a vendor stack-depth word at `+0x54`, where unmodified V10.5.1 has no
equivalent field under the compatible configuration. That incompatibility is
now closed by the reviewed one-field
`components/shared/freertos/g2-tcb-v10.5.1.patch`, SHA-256
`cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3`.
It applies to the authenticated base and target-layout compiles to the exact
112-byte ABI; the original private patch commit and field identifier remain
unobservable. A complete source port still needs the recovered
`FreeRTOSConfig.h`, Apollo STIMER tick/tickless glue, production admission of
the now-bounded application hooks, and the reviewed bounded
selection/integration of authenticated V10.5.1 `heap_4`. MVE, the exact
private AmbiqSuite pre-release commit, and
unrelated `INCLUDE_*` switches remain unresolved. The complete configuration
and port proof is in `docs/research/freertos-g2-config-port-audit.md`, with a
read-only 21-span verifier in `tools/analyze_g2_freertos_port.py`.
The focused patch proof is in
`docs/research/freertos-g2-tcb-vendor-patch-audit.md` and
`tools/analyze_g2_freertos_tcb_patch.py`.

The currently integrated queue subset uses the upstream V10.5.1 algorithms
with the recovered 80-byte `Queue_t` ABI. Five public queue operations, four
generic/private creation entries, three public
static-mutex/static-counting/dynamic-counting constructor wrappers, and the
private empty/full predicates are source-owned. The wrappers link
only to the source-owned generic creators and mutex initializer; their one
retained assertion branch enters source-generated
`ulSetInterruptMask` at the unchanged Thumb address `0x005FA0A5`.
Exact upstream
`vListInitialise`, `vListInsertEnd`, `vListInsert`, and `uxListRemove` are
also source-owned at stock spans `[0x0045607C,0x0045609A)`,
`[0x0045609A,0x004560B2)`, `[0x004560B2,0x004560E8)`, and
`[0x004560E8,0x0045610E)`, using the recovered 32-bit `List`/`ListItem` ABI.
The four leaves compile to relocation-free 22-, 26-, 58-, and 34-byte Thumb
functions and pass their focused
upstream-oracle, ABI, topology, target-body, and manifest gates. Remaining
task, list, port, and queue-private calls are explicit reviewed stock seams.
`vListInitialiseItem` is deliberately not claimed because the official
binary inlines it and exposes no standalone stock body.

The paired `ulSetInterruptMask` and `vClearInterruptMask` portable-layer
leaves are exact FreeRTOS V10.5.1 Cortex-M55 assembly from
`IAR/ARM_CM55_NTZ/non_secure/portasm.s`, syntax-adapted for Clang without
changing the instruction sequence. Source copies remain in place at
`[0x005FA0A4,0x005FA0BA)` and `[0x005FA0BA,0x005FA0C8)`, preserving all
existing callers and save/set/restore latency. Their only recovered
configuration parameter is shifted `BASEPRI=0x30`; both leaves retain the
released DSB/ISB ordering and have no relocations, data, or private state.

The remaining five NTZ port leaves are now source-assembled in place from
the 5,487-byte `runtime_freertos_ntz_port.S` adapter, SHA-256
`38c6a259ca2fbfbefb373ef5a80216f2e5f1cad998173ca2b4c9cfde6c01aee8`.
The authenticated upstream `portasm.s` is 11,686 bytes, Git blob
`4d02a431e1d759f12f50e70fc55a7b0b4d368e89`, and SHA-256
`eaa83b3867edec5560c69f2a21facd7aff3c0f3bfcdfc5751722375ae328ee8f`.
The production spans are:

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---|---:|---|
| `vRestoreContextOfFirstTask` | `[0x005FA058,0x005FA07E)` | 38 | `10edd4871b5f0c829e38618f1003ef0c45ec3629219317e23c62a2e255b0f4f8` |
| `vRaisePrivilege` | `[0x005FA07E,0x005FA08C)` | 14 | `29bceedf776515c291813e4eecd9a836378b81550c42d08aee35cf15df3bd8db` |
| `vStartFirstTask` | `[0x005FA08C,0x005FA0A4)` | 24 | `44ba0097fbbc1d0691837d5c51bee83e6b61509c9d89efffee9c202d930e6347` |
| `PendSV_Handler` | `[0x005FA0C8,0x005FA120)` | 88 | `d8e234bfa34805ad160e41ef54801973c9c871b36cf7ac0f365b56fe503253e3` |
| `SVC_Handler` | `[0x005FA120,0x005FA132)` | 18 | `d0fac197473b52d6ed466462d237ddb20dd8096a6507ea559e75d4bd9d88da94` |

Their exact ELF allowlist has four `R_ARM_THM_PC8` relocations to the
authenticated words at `0x005FA134` and `0x005FA138`, a
`R_ARM_THM_CALL` to `vTaskSwitchContext` at `0x004551B4`, and a
`R_ARM_THM_JUMP24` to `vPortSVCHandler_C` at `0x00442134`. The SVC and
PendSV vector values remain `0x005FA121` and `0x005FA0C9`.
`in_place_leaves` keeps the five names out of the appended overlay ABI and
ordinary patch-site graph, requires exact source/compiler/stock/output pins
and relocation order, authenticates the literal dependencies, and rejects
overlapping writes. The component therefore reports 182 source-owned
in-place bytes without changing the overlay or provider hash.

Five additional exact-upstream `tasks.c` leaves are source-integrated in
Apollo main:

| Function | Stock range | Recovered fixed-state seam |
|---|---|---|
| `xTaskGetTickCount` | `[0x00454EFE,0x00454F06)` | `xTickCount` at `0x20074A34` |
| `xTaskGetTickCountFromISR` | `[0x00454F06,0x00454F10)` | `xTickCount` at `0x20074A34` |
| `uxTaskGetNumberOfTasks` | `[0x00454F10,0x00454F16)` | `uxCurrentNumberOfTasks` at `0x20074A30` |
| `xTaskGetCurrentTaskHandle` | `[0x0045589C,0x004558A4)` | `pxCurrentTCB` at `0x20074A20` |
| `xTaskGetSchedulerState` | `[0x004558A4,0x004558C4)` | `xSchedulerRunning` at `0x20074A3C`; `uxSchedulerSuspended` at `0x20074A58` |

Each algorithm is independent of the vendor-extended TCB layout:
task-current returns the TCB pointer without dereferencing it, task-count
returns the authenticated population word, the tick getters read the
authenticated tick word through a shared source provider, and
scheduler-state implements the released three-state zero/nonzero policy.
Their focused writer/caller topology, target ABI, and integration contracts
are recorded in
`docs/research/freertos-task-current-source-boundary-audit.md`,
`docs/research/freertos-task-count-source-boundary-audit.md`, and
`docs/research/freertos-scheduler-state-source-boundary-audit.md`. These
incremental fixed-address globals remain an explicit seam until a complete
kernel link migrates the FreeRTOS RAM layout atomically.

## CMSIS-FreeRTOS v10.5.1 authenticated compile-input closure

`third_party/cmsis-freertos` now authenticates ten unmodified upstream files
from CMSIS-FreeRTOS tag `v10.5.1` and its package-declared CMSIS_5 tag
`5.9.0` dependency. The CMSIS-FreeRTOS unsigned annotated tag object is
`34e6e4c403c17de35ec0acf29610e374dc938604`, peeled commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, tree
`d3689a816acc77a3f0b7d35439d666ad8434b6ba`. The CMSIS_5 unsigned annotated
tag object is `61e36449f53c25ef7825c40f7dd93685736f457f`, peeled commit
`2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`, tree
`b88e747b2a2309b81ea77831481a58393465cd7b`.

The constructor root `cmsis_os2.c` is 70,106 bytes, Git blob
`88dca1d881f1a960872572a8a0efd94cde19dcea`, SHA-256
`8a0d60b56ad30c4f7957f64fa581158017b6812ec94b832d974c773ae4f2bc36`.
The closure pins its public/private wrapper headers, GNU-compatible CMSIS
compiler path, CMSIS RTOS2 headers, package descriptor, and license files.
`python3 third_party/cmsis-freertos/verify_snapshot.py` checks every path,
byte count, Git blob, SHA-256, direct include, selected compiler branch, and
license notice without compiling, linking, or touching hardware.

The stock linked translation unit is independently closed at
`[0x0044900E,0x00449ED2)`. Its 43 functions comprise 38 public APIs and five
private helpers; 3,758 executable bytes plus 22 literal bytes exactly tile the
3,780-byte physical object. The census authenticates 831 external direct BL
callers, 41 internal calls, no external interior ingress, and the sole stored
entry word for `TimerCallback`; 33 possible public APIs are explicitly absent.
Live `osTimerStart`, `osEventFlagsSet`, and `osEventFlagsWait` behavior requires
commit `600ba38a`, while linked `osThreadFlagsWait` lacks the later `bb8a350a`
re-notification repair. The selected v10.5.1 commit is therefore the maintained
baseline; its exact `cmsis_os2.c` blob first appeared at `13acfbef`, but
source-identical/dead-code-only history prevents a unique Even checkout claim.
See the
[`CMSIS-FreeRTOS linked-function census`](research/cmsis-freertos-linked-function-census.md)
and its fail-closed analyzer.

The first post-census production tranche adds private `IRQ_Context`,
`osKernelGetTickCount`, `osThreadGetId`, and
`osMessageQueueGetCapacity`. Complete stock entries totaling 88 bytes redirect
to a dual-toolchain-pinned 84-byte source tranche plus four alignment bytes.
The dependencies are already source-owned FreeRTOS scheduler/tick/current-task
providers and the authenticated Queue_t `uxLength` offset at `+0x3C`; no TCB
field is read. See the
[`core-leaf source-boundary audit`](research/cmsis-freertos-core-leaves-source-boundary-audit.md).

The second production tranche adds `osSemaphoreGetCount` and
`osMessageQueueGetCount`. Their two 36-byte stock entries redirect to
selector-isolated 36-byte source leaves with the same call topology: IRQ
classification followed by the already source-owned normal or ISR FreeRTOS
queue-count provider. They add no TCB-layout dependency. See the
[`count-leaf source-boundary audit`](research/cmsis-freertos-count-leaves-source-boundary-audit.md).

`osMessageQueueDelete` is subsequently source-owned through the IRQ helper and
the source-owned FreeRTOS `vQueueDelete` provider. The next production tranche
adds `osThreadYield`, `osKernelGetState`, `osMutexDelete`, and
`osTimerIsRunning`, all closed over already source-owned providers and pinned
under both complete package profiles.

Candidate-only shims at
`components/apollo_main/core_overlay/candidates/cmsis_freertos_constructors/`
provide `{FreeRTOSConfig.h,portmacro.h,cmsis_freertos_target.h,string.h}`.
With them, the authenticated, unmodified `cmsis_os2.c` compiles for
Cortex-M55 with `-Oz -Werror`. Garbage collection retains 370 text bytes:
`IRQ_Context` 46, `osMessageQueueNew` 88, `osMutexNew` 98, and
`osSemaphoreNew` 138. It retains zero read-only or writable data and four
8-byte EHABI `.ARM.exidx` sections. The isolated candidate gate passes 6/6
tests in 0.231 seconds.

That broad closure remains candidate-only for unrelated CMSIS services. The
bounded `osMessageQueueNew` algorithm is
production-integrated from
`runtime_cmsis_message_queue_new.c`, 8,427 bytes with SHA-256
`8897019aa7a2beca32a88dc60808fb1f99b1538933b8ab4fbd9ed4fed38d433c`.
Its 124-byte target closes directly over three source-owned FreeRTOS
dependencies. The separately bounded `osMutexNew` algorithm is also
production-integrated from `runtime_cmsis_mutex_new.c`, 9,798 bytes with
SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`;
its 116-byte target closes directly over the source-owned scheduler-state
getter and static/dynamic mutex creators. The separately bounded
`osSemaphoreNew` production adapter is 11,566 bytes with SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`;
its 178-byte target closes over source-owned scheduler, queue creation/send,
counting-semaphore, and `vQueueDelete` dependencies. The unresolved device-header,
`SystemCoreClock`, MVE, broad
`INCLUDE_*`, assert/NVIC/libc, and candidate `StaticTask_t` questions remain
outside the admitted leaf. This source boundary does not claim Even
Realities' historical checkout. The wrapper and CMSIS source retain
Apache-2.0 terms; separately supplied FreeRTOS remains MIT.

## littlefs v2.10.1 source-equivalent release

Apollo main contains an 84-byte non-threadsafe `struct lfs_config` at
`0x006E83A4`, with SHA-256
`f38bd899e180d29ee60609a2452d25c2d2d6c6fef4eb455064e23a6ca7c6e813`.
Its exact configuration is:

| Field | Value |
|---|---:|
| Read callback | `0x004763B9` |
| Program callback | `0x004763F1` |
| Erase callback | `0x00476429` |
| Sync callback | `0x004764DD` |
| Read size | 16 bytes |
| Program size | 256 bytes |
| Block size | 4,096 bytes |
| Block count | 3,008 |
| Block cycles | 500 |
| Cache size | 4,096 bytes |
| Lookahead size | 256 bytes |
| Compact threshold | 0 |
| Static buffers and limit overrides | Null/zero |
| Thread-safe hooks | Disabled |

The bootloader contains the same 84-byte layout and identical geometry at
`0x00431070`, SHA-256
`724c351d2136e3c2f10b59ad84d547da4632739ea1f20eb839e9af2cfbd5b6e8`.
Only its callbacks differ:

```text
read  0x004212D9
prog  0x00421311
erase 0x00421349
sync  0x004213D5
```

The complete assertion-line fingerprint uniquely matches official release
`v2.10.1`: all 38 upstream `v2.*` tags were checked, and the adjacent
`v2.10.0`, `v2.10.2`, and `v2.11.0` releases disagree on the recovered
compact-threshold, block-count, global-state, demove, and directory-open
lines. Assertions and debug/warn/error diagnostics are enabled, trace,
`LFS_THREADSAFE`, and `LFS_MULTIVERSION` are disabled, and dynamic allocation
is enabled.

The released tag commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318` is an exact source-equivalent
pin, not a claim about Even's historical checkout. Three upstream source
states within this generation compile byte-identically under the recovered
configuration, so the stripped binary cannot distinguish their repository
provenance. The complete audit is in
`docs/research/littlefs-version-audit.md`.

The Apollo-main public boundary comprises `lfs_format`, mount/unmount,
remove/rename/stat, file open/close/sync/read/write/seek/truncate/rewind/size,
mkdir, and directory open/close/read/rewind at
`0x004CFA58...0x004CFD0C`. The bootloader uses the subset from `lfs_format`
through directory close at `0x00415128...0x0041531C`.

This supports one vendored v2.10.1 core with main-firmware and bootloader port
tables. Before redirecting any API, capture a complete external-flash image,
mount a copy read-only, validate the superblock/disk version/tree/content
against stock behavior, and exercise mutating and power-loss cases only on
disposable copies. Device format and erase remain prohibited until that gate
passes.

Focused port disassembly recovers the standard littlefs callback ABI and the
exact address mapping:

```text
external address = 0x01400000 + block * 0x1000 + offset
partition         = 0x01400000...0x01FC0000
driver success    = 0
driver failure    = -5 (LFS_ERR_IO)
```

Apollo main calls the retained MSPI driver at `0x00471021` for reads,
`0x004708A9` for programs, and `0x0047075D` for erases. The bootloader uses
`0x00420F71`, `0x00420B0D`, and `0x00420A09`, respectively. The callbacks
ignore their `cfg` argument; `sync` is a no-op. The stock ports have
insufficient defensive bounds checking, allow partial program behavior, and
do not consistently propagate mutex, mode-transition, or busy-timeout
failures. A source port must therefore validate the full block/offset/size
range itself rather than reproduce those hazards.

A read-only source port is feasible with littlefs v2.10.1,
`LFS_READONLY`, explicit partition bounds, and stock auto-format/boot-count
paths bypassed. Full read/write ownership still requires the G2 board MSPI
initialization, timing, XIP, and power policy plus a golden external-flash
capture. The reproducible audit and analyzer are
`docs/research/littlefs-g2-block-port-audit.md` and
`tools/analyze_g2_littlefs_ports.py`.

The transport audit further identifies AmbiqSuite 5.1.0 MSPI HAL as reusable
upstream code while keeping G2 board policy in a separate adapter: Apollo510B
MSPI1/CE0, SPI mode 0, 96 MHz, IRQ 21 priority 4, interrupt mask `0x1A80`,
the recovered GPIO set, calibration sweep, mutex/timeouts, retained
sleep/wake policy, and main-only read-only 32 MiB XIP at `0x80000000`.
`tools/analyze_g2_littlefs_mspi_transport.py` validates those parameters and
the report is `docs/research/littlefs-g2-mspi-transport-audit.md`.

Twenty-one dual-image littlefs boundaries are source-integrated directly
from authenticated v2.10.1-equivalent source. Apollo main additionally owns
the main-only `lfs_file_tell_` leaf at `[0x004CE45C,0x004CE460)` and
`lfs_file_rewind_` at `[0x004CE460,0x004CE472)` and `lfs_file_size_` at
`[0x004CE472,0x004CE48A)`, for 24 littlefs boundaries in that image. Both
images own the following scalar and alignment quartet,
fallback-bitops trio, endian-conversion quartet, and ten private boundaries:

| Function | Apollo-main stock range | Bootloader stock range |
|---|---|---|
| `lfs_max` | `[0x004CA6F8,0x004CA700)` | `[0x00410400,0x00410408)` |
| `lfs_min` | `[0x004CA700,0x004CA708)` | `[0x00410408,0x00410410)` |
| `lfs_aligndown` | `[0x004CA708,0x004CA714)` | `[0x00410410,0x0041041C)` |
| `lfs_alignup` | `[0x004CA714,0x004CA720)` | `[0x0041041C,0x00410428)` |
| `lfs_npw2` | `[0x004CA720,0x004CA77A)` | `[0x00410428,0x00410482)` |
| `lfs_ctz` | `[0x004CA77A,0x004CA78A)` | `[0x00410482,0x00410492)` |
| `lfs_popc` | `[0x004CA78A,0x004CA7B2)` | `[0x00410492,0x004104BA)` |
| `lfs_scmp` | `[0x004CA7B2,0x004CA7B6)` | `[0x004104BA,0x004104BE)` |
| `lfs_fromle32` | `[0x004CA7B6,0x004CA7D8)` | `[0x004104BE,0x004104E0)` |
| `lfs_tole32` | `[0x004CA7D8,0x004CA7E0)` | `[0x004104E0,0x004104E8)` |
| `lfs_frombe32` | `[0x004CA7E0,0x004CA802)` | `[0x004104E8,0x0041050A)` |
| `lfs_tobe32` | `[0x004CA802,0x004CA80A)` | `[0x0041050A,0x00410512)` |
| `lfs_mlist_isopen` | `[0x004CB082,0x004CB0A0)` | `[0x00410D8A,0x00410DA8)` |
| `lfs_mlist_remove` | `[0x004CB0A0,0x004CB0BC)` | `[0x00410DA8,0x00410DC4)` |
| `lfs_mlist_append` | `[0x004CB0BC,0x004CB0C4)` | `[0x00410DC4,0x00410DCC)` |
| `lfs_fs_disk_version` | `[0x004CB0C4,0x004CB0CA)` | `[0x00410DCC,0x00410DD2)` |
| `lfs_fs_disk_version_major` | `[0x004CB0CA,0x004CB0D6)` | `[0x00410DD2,0x00410DDE)` |
| `lfs_fs_disk_version_minor` | `[0x004CB0D6,0x004CB0E0)` | `[0x00410DDE,0x00410DE8)` |
| `lfs_alloc_ckpoint` | `[0x004CB0E0,0x004CB0E6)` | `[0x00410DE8,0x00410DEE)` |
| `lfs_alloc_drop` | `[0x004CB0E6,0x004CB0F6)` | `[0x00410DEE,0x00410DFE)` |
| `lfs_alloc_lookahead` | `[0x004CB0F6,0x004CB12E)` | `[0x00410DFE,0x00410E36)` |

The utility quartet is compiled from one shared source file with SHA-256
`2730d0f39e02d7b6e07396894b796b26d9f73332deff23a685b5a06da0f7fb22`.
The pure `max`, `min`, and `aligndown` leaves are call-free; the sole
`alignup` relocation closes over source-owned `aligndown`. Four authenticated
stock entries in each image become eight total non-linking Thumb `B.W`
redirects. Exact spans, stock hashes, caller topology, and current placements
are recorded in
`docs/research/littlefs-next-closed-leaves-audit.md`.

The shared fallback-bitops source is 2,795 bytes with SHA-256
`405092c6e8fc65a740f951cb2affaad8766e2553c7b8d290ff58f435e8830f47`.
It compiles the exact v2.10.1 `LFS_NO_INTRINSICS` implementations of
`lfs_npw2`, `lfs_ctz`, and `lfs_popc`, preserving `npw2(0) == 32`,
`npw2(1) == 1`, and `ctz(0) == 0`. The only new relocation is the internal
Thumb call `lfs_ctz -> lfs_npw2`; there are no external, undefined, literal,
or data dependencies.

The shared endian-conversion source has SHA-256
`830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac`.
Apollo510 and both reviewed compiler profiles are little-endian, so
`lfs_fromle32` and `lfs_tole32` compile to two-byte identity leaves while
`lfs_frombe32` and `lfs_tobe32` compile to four-byte byte-swap leaves.
Optimization closes the upstream helper relationships without a relocation;
all eight target bodies have no literal, data, or undefined-symbol
dependency. Complete-image scans pin 26, 19, 4, and 2 direct callers per
image and find no stored entry, non-linking incoming edge, or external
interior entry.

The shared `lfs_mlist_isopen` integration source has SHA-256
`7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c`.
Focused disassembly supplies only the 32-bit pointer and unsigned 0/1 return
ABI plus the `struct lfs_mlist.next` offset-zero prefix. The 44-byte main and
18-byte bootloader bodies have no relocation, literal, undefined symbol,
stored entry, or interior entry.

The list helpers pin the recovered `lfs_t.mlist`/node-prefix ABI,
`lfs_fs_disk_version` closes its stock distant literal with a source-local
`0x00020001` constant, and `lfs_alloc_drop` closes its checkpoint operation
in source. The original seven main and boot private-leaf redirects
authenticate their complete stock bodies and whole-image entry/interior
topology; those emitted functions have no undefined symbol or `.text`
relocation.

The current disk-version-parts source is 1,734 bytes with SHA-256
`920d03e80c9d16a1d0b4299f8151eefe4d9f3ac1ba89c2d40bcc5830335eb5a7`.
It ports exact `lfs_fs_disk_version_major` and
`lfs_fs_disk_version_minor` from the authenticated v2.10.1 `lfs.c` at
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. Each profile emits two
ten-byte leaves whose sole reviewed `R_ARM_THM_CALL` relocation closes over
the existing source-owned disk-version provider. Apollo main places them at
`[0x007B01B8,0x007B01C2)` and `[0x007B01C4,0x007B01CE)`, separated by two
generated alignment bytes. The bootloader places them contiguously at
`[0x00434592,0x0043459C)` and `[0x0043459C,0x004345A6)`.

The current allocator-lookahead source is 5,445 bytes with SHA-256
`44ab9037747a4cb209404423d52cf817b035cbab5177a8c0cb05090df4b68491`.
It reuses the exact v2.10.1 `lfs_alloc_lookahead` algorithm; focused
disassembly recovers only `lfs_t.lookahead.start` at `0x54`,
`lookahead.size` at `0x58`, `lookahead.buffer` at `0x64`, and
`block_count` at `0x6C`. The identical 56-byte stock spans have SHA-256
`58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf`.
Apollo main redirects `0x004CB0F6` to a 50-byte source leaf at
`0x007B01D0`; the bootloader redirects `0x00410DFE` to a 48-byte source
leaf at `0x004345A6`. Both target bodies are relocation-free and pass
20,000 deterministic upstream-oracle cases.

The two main-only file accessors preserve the recovered 32-bit
`lfs_file_t` ABI. `lfs_file_tell_` returns `pos +0x34`; the current
`lfs_file_size_` leaf reads `ctz.size +0x2C`, `flags +0x30`, and `pos +0x34`,
preserves `LFS_F_WRITING = 0x00020000`, and computes the writing-state maximum
through the already source-owned `open_cfw_littlefs_util_max`. The 20-byte
file-size leaf is placed at `0x007B28D4` on Apple and `0x007B2FF0` on Linux.
Its only relocation is therefore within the authenticated littlefs source
closure; it adds no stock helper, block-device callback, filesystem format, or
erase path.

The separate raw bootloader source-overlay component appends the current
source-generated bodies below `0x00438000` and redirects the authenticated
boot spans listed above. Its builder checks every complete original body
before patching and leaves EVENOTA CRC generation to the package assembler.
The current component also closes the first-party S200 bootloader
`redirect_init` entry with clean-room C: two retained `osMutexNew` calls, two
recovered SRAM handle words, exact success/failure logging, and a 275-byte
strict relocated text/string closure. Canonical provider accounting is 935
source-owned bytes before the following runtime tranche. The component now
also closes the Arm EABI byte-fill/forward-copy, bounded-comparison,
reject/accept string-span, reflected CRC-32, sole-caller `0x200270CC` setter,
and 41 numeric/formatter/dispatch/string/context/gate/runtime bodies. These leaves cover unsigned
64-bit divide by ten, digit counts, wrapping parsing, decimal/hex output,
nullable string length, repeated output, fixed-point float conversion, and the
complete formatter core, variadic logging dispatch, substring search, and
critical-context detection, gate acquisition, state mapping, release,
context-value dispatch, the address-identified `0x004160FE` dispatcher, and
the `0x004161C6` retained-value wrapper, the validated runtime-call wrapper at
`0x004161CE`, the guarded runtime-action wrapper at `0x00416200`, and the
two-phase runtime-transfer wrapper at `0x0041623A`, the masked runtime-wait
wrapper at `0x004162C4`, the optional runtime-notification wrapper at
`0x00416378`, the registered runtime-callback adapter at `0x0041639A`, and the
registered runtime-object constructor at `0x004163B2`, guarded submission,
object creation, event-flags operations, tagged-handle acquire/release, and
semaphore/message-queue creation, message-queue put/get, bit width,
count-trailing-zeros, floor-log2, twelve authenticated TLSF v3.1
block-header primitives, eight TLSF physical-block/state/alignment helpers,
three TLSF request-size/class-mapping helpers, three TLSF free-list
selection/mutation helpers, ten allocator-operation helpers, and seven public
TLSF allocator entries, with 181 strict relocations.
Final accounting is 6,931 source-owned bytes, 8,208 generated patch bytes,
14 alignment bytes, and 140,391 retained
official bytes. The
following EasyLogger executable bodies from `0x0041733C` remain an explicit
software gap after 98 authenticated transition-data bytes, and physical
boot/stream validation is blocked by unavailable physical evidence; future qualification requires authorized
responsive hardware.
Focused evidence is recorded in
`docs/research/littlefs-file-tell-source-boundary-audit.md`,
`docs/research/littlefs-file-size-source-audit.md`,
`docs/research/littlefs-scmp-source-boundary-audit.md`,
`docs/research/littlefs-alloc-ckpoint-source-boundary-audit.md`,
`docs/research/littlefs-alloc-drop-source-boundary-audit.md`,
`docs/research/littlefs-mlist-remove-source-boundary-audit.md`,
`docs/research/littlefs-mlist-append-source-boundary-audit.md`,
`docs/research/littlefs-disk-version-source-boundary-audit.md`, and
`docs/research/littlefs-next-closed-leaves-audit.md`, plus
`components/bootloader/core_overlay/EVIDENCE.md` and
`docs/research/g2-bootloader-redirect-init-source-closure.md`, plus
`docs/research/g2-bootloader-aeabi-memset-source-closure.md` and
`docs/research/g2-bootloader-aeabi-memcpy-source-closure.md`, plus
`docs/research/g2-bootloader-memcmp-source-closure.md`, plus
`docs/research/g2-bootloader-string-spans-source-closure.md` and
`docs/research/g2-bootloader-crc32-source-closure.md`, plus
`docs/research/g2-bootloader-store-200270cc-source-closure.md`, plus
`docs/research/g2-bootloader-numeric-source-closure.md` and
`docs/research/g2-bootloader-format-primitives-source-closure.md`, plus
`docs/research/g2-bootloader-float-format-source-closure.md`.

### Historical fallback-bitops and FreeRTOS NTZ milestones

The historical fallback-bitops production release placed the main bodies at
`0x007AEF74`, `0x007AEFBC`, and `0x007AEFCC` and the bootloader bodies at
`0x004344D2`, `0x0043450A`, and `0x0043451A`. Its 114,324-byte main overlay,
282-byte boot overlay, 3,637,720-byte main provider, and 148,882-byte boot
provider are authenticated in the component evidence. The 4,415,834-byte
package has SHA-256
`058782604ab6cb946aff0acedbbef7d367bb1d82114f28c9a70276bcdf178e9a`;
`./make.sh source`, `./make.sh verify`, all three offline inspection lanes,
and three byte-identical output-isolated reproducibility lanes passed. The
focused production gate passed 6/6 tests in 13.693 seconds, and the inherited
focused gate passed 55/55 tests in 39.997 seconds: 61 tests in 53.690
seconds summed. The canonical repository run passed all 1,806 tests in
1,139.177 seconds; inside it, all 248 Apollo-main aggregate methods passed.

The subsequent, now-superseded FreeRTOS NTZ release source-owned another 182
Apollo-main bytes in place without changing that release's main/boot overlay,
provider, or package hashes.
The main overlay/provider retained
`00318de9ff51e19f77d889fa691a3a2a54e035b1287843bda857f944af58e065`
and
`f0da043e234dc38481059459755e091622d689313cd12e5c8d5155c7b4ba3202`;
the boot overlay/provider retained
`b934dbea7624660c3c774eb0f4edd5e73a738fc59023fc69cfac96417dfe2fee`
and
`1aa7920a16ed2857a2743394c0f62395a2f2477f95c965da47d1e29c4d2d8247`.
The component report records 182 in-place source bytes, 114,506 total
source-owned bytes, and 3,443,066 opaque base bytes. The manifest contained
750 placed, two unresolved, and five container-only regions; flash-plan
SHA-256 is
`eda45c2cc276bd70bc123267d9fbdc09b0ae4aa030a7557f874c259ca7f5fee8`.
Package ownership was 114,820 source bytes (2.600188%), 81,477 generated
bytes (1.845110%), 4,219,537 opaque bytes (95.554702%), and 196,297
controlled bytes (4.445298%). The focused production gate passed 23/23 in
18.333 seconds and the linker plus inherited gate passed 21/21 in 0.705
seconds. Standard source and manifest verification passed. Three lanes under
`build/repro-freertos-ntz-output-{a,b,c}` reproduced both overlays, both
providers, the package, and the flash plan byte-for-byte; their temporary
manifests were moved to Trash. All 248 Apollo-main tests passed in 582.904
seconds. `./make.sh test` passed all 1,838 tests in 1,038.709 seconds,
including all six CMSIS constructor compile-closure tests.

### Prior disk-version-parts production

That disk-version-parts release advanced the main overlay to 114,346
bytes with SHA-256
`bdc1e353d1adcb0075231afb6c423616dcc0da8335b4b430afe51763a0b9df20`
and the 3,637,742-byte main provider to
`d69c4834f65b0661834f990da8167ca6989a1b1c97fda838edc488a4ed0b3e8e`.
Its installed bytes end at `0x007B01CE`, leaving 261,682 bytes below
`0x007F0000` and 319,026 bytes below `0x007FE000`.
The boot overlay is 302 bytes with SHA-256
`e94e33658aca89d3830182bc6c17c656256a194262835c041fecc93e1d72dc59`;
the 148,902-byte boot provider has SHA-256
`abc583d976a01e237ffa4ed29e4be1b6ff0e5ae2d9756bccec58d1779fe20239`,
ends at `0x004345A6`, and leaves 14,938 bytes before Apollo main.
The 4,415,876-byte package has SHA-256
`60cd913a716266b349ce18295064f2484749a7dbad2ab9244c923c927bd56c2f`.
Its 546,404-byte flash plan has SHA-256
`52124c17205ae10e47f0b02d0cd6bae7c2b30e10d65d787aa34201a53fe0dc68`
and records 757 placed, two unresolved, and five container-only regions.
Package ownership is 114,860 source bytes (2.601069%), 81,523 generated
bytes (1.846134%), 4,219,493 opaque bytes (95.552796%), and 196,383
controlled bytes (4.447204%).

### Prior allocator-lookahead production

That allocator-lookahead release advanced the main overlay to 114,398
bytes with SHA-256
`2189ec69f7076e216c2ba7388f4eb9d19647feb9f89c382864012902be4e0fdf`
and the 3,637,794-byte main provider to
`557fe93fdf79c5cb332c7db731db29ed7cfc42be3daa49fb0d022f81e7fe0ba8`.
Its installed bytes end at `0x007B0202`, leaving 261,630 bytes below
`0x007F0000` and 318,974 bytes below `0x007FE000`.
The boot overlay is 350 bytes with SHA-256
`1b8bb2893a33a18b8481b785a57d49c2849396cc05c5ef20d86f8cf5cef255a5`;
the 148,950-byte boot provider has SHA-256
`9af8b65041bbd576b49b4f88e2f7427daf7bb445981d608799d86e1987468736`,
ends at `0x004345D6`, and leaves 14,890 bytes before Apollo main.
The 4,415,976-byte package has SHA-256
`3d4b2f3e22a10d0755642c0544786c9a881b2ab7c2271d8a184a83f5d3d7d13f`.
Its 550,026-byte flash plan has SHA-256
`73978705e32bbb968a9741620a80e1a70f866b5e43db60f4a9f08b4404ce34d1`
and records 762 placed, two unresolved, and five container-only regions.
Package ownership is 114,958 source bytes (2.603230%), 81,637 generated
bytes (1.848674%), 4,219,381 opaque bytes (95.548096%), and 196,595
controlled bytes (4.451904%).

### Prior CMSIS `osMessageQueueNew` production

That release advanced the main overlay to 114,524 bytes with SHA-256
`de76f5db2f04f48c81ea480c348a3c9151d4441c522eba68621ad812290153e2`
and the 3,637,920-byte main provider to
`874bdc621a6cd91848dee66038c3ba97d7e4b7c7ab1fb5063739bf69fc3047e1`.
Its installed bytes end at `0x007B0280`; the boot artifacts remain unchanged.
The 4,416,102-byte package has SHA-256
`c7baf50cd5386a5e27b4c284cc0084e8cf5d0b83d74eb08b8d4a997bf66474f4`.
Its 552,937-byte flash plan has SHA-256
`79da631918503c668516e1af5d3844e3dab65c9e63d8add4834a43536ef69407`
and records 766 placed, two unresolved, and five container-only regions.
Package ownership is 115,082 source bytes (2.605963%), 81,779 generated
bytes (1.851837%), 4,219,241 opaque bytes (95.542200%), and 196,861
controlled bytes (4.457800%). The focused production gate passes 10/10
tests, offline.

## AmbiqSuite Apollo510 MSPI HAL reuse boundary

`am_hal_mspi_interrupt_clear` is unequivocally mapped to the authenticated
AmbiqSuite Apollo510 `am_hal_mspi.c` source at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, with source SHA-256
`5a91ab0c67bda4bd61c7d436b94b5a7c81693b948a331d282ae10e88cc5bf85f`.
Main
`[0x004C23DE,0x004C240E)` and boot
`[0x00426506,0x00426536)` contain the same complete 48-byte stock body:
handle validation, module extraction, `INTCLR` write, mandatory volatile
`INTSTAT` readback, and the upstream success/invalid-handle returns.

The authenticated, unmodified complete translation unit compiles for
Cortex-M55 with function/data sections. When only
`am_hal_mspi_interrupt_clear` is rooted and `--gc-sections` is applied, the
linked ARM ELF retains exactly the 48-byte leaf, no private
`g_MSPIState`, no other global code/data symbol, no unresolved symbol, and no
leaf text relocation. This proves that OpenCFW should reuse the complete
upstream translation unit with section GC instead of copying Ambiq's private
MSPI handle type into a local rewrite. The proof is reproducible with
`tools/prove_ambiq_mspi_interrupt_clear_gc.py`; stock identity and topology
are checked by `tools/analyze_g2_mspi_interrupt_clear.py` and documented in
`docs/research/ambiqsuite-mspi-interrupt-clear-source-boundary-audit.md`.

The dependency closure is now pinned, licensed, and self-contained in
`third_party/ambiqsuite-apollo510` and `third_party/cmsis-core`. The Ambiq
snapshot authenticates 71 upstream dependency files at tree
`02b79dbf428a8cded053c65c92cc58fa5fdb8e78`; the CMSIS snapshot
authenticates the seven reached Core headers plus its Apache-2.0 license at
tree `3474af187114165f3623732474e4e1bd4b3d01d8`. Their offline verifiers
pin every imported file by byte count, Git blob SHA-1, and SHA-256.

Both production overlays compile the complete authenticated
`am_hal_mspi.c` with the proven Cortex-M55 configuration, retain only
`am_hal_mspi_interrupt_clear`, and install hash-authenticated redirects at
the two stock bodies. The current boot image places the leaf at `0x00434544`;
Apollo main places it at `0x007B0128`. Each retained leaf is 48 bytes with SHA-256
`87505e035fa5fe7c0dfd7c4d85b66c6b8f3b57ced45dc7afd787db6c52b0fd7b`,
zero relocations, and no `g_MSPIState`.

Broader source-owned G2 callers use the same named 5.1.0 headers. The bootloader
`am_hal_mspi_control` ordinal mismatch is now closed by the narrow production
adapter in `runtime_mspi_control_4251c0.c`: stock-only requests 10 and 11 are
implemented directly and the remaining stock ordinals are translated before
entering the maintained AmbiqSuite body. The derived BSD-3-Clause translation
unit is separately pinned; the vendored upstream snapshot remains unchanged.
Physical MSPI register, XIP, timing, FIFO, interrupt, flash-bus, and cold-boot
qualification is blocked by unavailable physical evidence.

## LVGL v9.3 configuration

The defensible upstream baseline is LVGL v9.3.0 with possible Ambiq or local
patches. High-confidence compiled configuration includes:

- FreeRTOS OS integration with recursive mutexes and dynamically created
  tasks;
- warning-level logging, null/allocation assertions, and a custom fatal hook;
- custom malloc/realloc/free hooks and 32-bit millisecond ticks;
- little-endian operation;
- a 576-by-288 display with DPI 130;
- native format 6 at 8 bpp, strongly identified as `LV_COLOR_FORMAT_L8`;
- custom output format 13 at 4 bpp, consistent with
  `LV_COLOR_FORMAT_A4`, using an exact `0x14400`-byte output allocation;
- FreeType, littlefs, BMP, LVGL binary decoder, flex, and grid enabled; and
- span and built-in object-ID state enabled, complex software masks disabled,
  and custom rather than built-in TLSF allocation; and
- compressed fonts disabled.

Recovered ABI anchors are `sizeof(lv_global_t) == 0x1EC`,
`sizeof(lv_display_t) == 0x31C`, and `sizeof(lv_draw_buf_t) == 0x1C`.
The exact global layout is reproduced by the selected official core plus
Ambiq's `clear_cb`/`copy_cb` additions from commits `d4dcd26…` and
`925470dd…`. The backend source itself is exact tree `1e774257…`, canonical
commit `5be8e0ae…`, with byte-identical replay `67fd93e2…`. Upstream tick,
memory, FreeRTOS OSAL, misc/container, core, widget, layout, font, and standard
draw code can use the v9.3.0 baseline with ABI assertions. The Ambiq subtree
and public Nema dependency identities are closed but remain separately
production-excluded pending stock-IAR/GPU-patch/HAL candidate admission,
atomic integration, and hardware validation. The seven-function / 638-byte
`lv_ambiq_display.c` linked surface is already source-owned; only its original
private commit is unavailable. FreeType system glue, GPU/Nema hooks, the
L8-to-A4 pipeline, first-party input transport, and display-manager code remain
separate G2/vendor layers. No separate third-party input-port artifact is
linked.

## FlashDB 2.1.1 configuration

The application uses FlashDB's FAL-backed KVDB path, not file mode. Focused
call-site recovery pins two instances:

| Database | FAL partition |
|---|---|
| `sysenv` | `kvdb` |
| `factory` | `NVdb` |

KV and sector caches are enabled with 64 entries each. `FDB_WRITE_GRAN` is 1
bit, the KV header is 24 bytes, and `sec_size` is the `norflash` block size of
4 KiB because neither caller overrides it. `FDB_KV_AUTO_UPDATE`, file mode,
and FlashDB debug logging are off, and no live/retained TSDB subsystem is
present. The original `FDB_USING_TSDB` macro state is not statically proven;
the recovered minimal source configuration omits it. The two static `fdb_kvdb` objects
begin at `0x2005DFFC`, have stride `0x8AC`, and require the target's short-enum
ABI. The compiled FAL partitions are `kvdb` at `0x01FC0000` length `0x38000`
and `NVdb` at `0x01FF8000` length `0x8000`.

Keep FAL device/partition definitions, MRAM callbacks, mutex hooks, the two
database objects, default tables, magic/version migration, factory reset,
and service blob APIs in a separate G2 port/glue layer. The current
production-excluded read-only candidate accepts only the two authenticated
partition records, checks overflow-safe bounds, locks through the recovered
CMSIS mutex, converts every nonzero MX25 status to `-1`, and denies all
writes and erases. Before integration, retain those gates, close the
non-destructive mount policy and exact blob/delete/iterate API surface, and
validate the on-disk format against a non-mutating golden capture. The source closure is
the official `fdb.c`, `fdb_kvdb.c`, `fdb_utils.c`, public headers, and generic
FAL core/headers; omit TSDB source, file, RT-Thread, shell, demo, and
sample-port code. The offline snapshot verifier reconstructs seven Git tree
objects to prove commit-to-path-to-blob membership for every selected file.

## EasyLogger 2.2.99 configuration

Apollo main unequivocally identifies the EasyLogger `2.2.99` version label
and compiled paths for `elog.c`, `elog_utils.c`, and `elog_async_api.c`. The
bootloader identifies the same label but only `elog.c` and `elog_utils.c`;
its focused port audit proves a synchronous level-dropping channel-1 sink,
distinct absolute state, and a boot-specific assertion policy.

The primary upstream repository has no `2.2.99` tag or release; public tags
end at `2.2.0`. Commit
`a607e1715b83d42b2d431e4e415263b7044e0ecb` introduced the `2.2.99` version
string, which many later master revisions retain. The G2 core contains the
argument-aware directory/function/line helpers introduced by
`cd93d9c768415f4b7279f2d3ef2366ce15ea087c`. That commit and the only two
later official master commits, `34cc1717825c799979a1b4b3739be1e5668a7322`
and vendored
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, have byte-identical
`elog.c`, `elog_utils.c`, `elog.h`, and `elog_cfg.h` blobs. The snapshot is
therefore source-equivalent; no executable discriminator can select one of
the three repository commits. The full audit is in
`docs/research/easylogger-version-audit.md`.

Official upstream uses `elog_async.c`; the retained `elog_async_api.c` path
does not exist in inspected upstream history and is classified as G2
downstream glue.

The recovered main configuration has a 1,024-byte output buffer at
`0x2006BD30`, text colors enabled, an application filter level of
`ELOG_LVL_INFO`, five 33-byte tag-level slots, and six 32-bit format masks.
Assert-level output uses mask `0xFF`; error through verbose use `0x87`.
The global logger object begins at `0x20070BE8`; the integrated ABI pins a
`0xF6` field extent and a `0xF8` padded object size.

The upstream core can be kept unmodified behind a small Apollo-main port:

| Port service | Stock entry | Recovered G2 behavior |
|---|---:|---|
| Initialize | `0x0044AA68` | Lazily create `elogMutex`; return zero |
| Formatted output | `0x0044AA80` | Enqueue with G2 async metadata, then set event bit 1 |
| Raw/hexdump output | `0x0044AA76` | Enqueue through the raw G2 path |
| Lock / unlock | `0x0044AA98` / `0x0044AAA0` | CMSIS mutex, 1,000-tick acquire timeout |
| Time string | `0x0044AAA8` | Format date, time, and final integer field in a static buffer |
| Process / thread | `0x0044AB14` / `0x0044AB1C` | Current FreeRTOS task name or `unknown` |

The mutex uses static CMSIS storage: control block `0x20072AD8`, size 80,
and handle global `0x20074578`. The asynchronous event-flags handle is
`0x20074570`. That queue/worker is G2 application policy, including its
255-byte record cap, and belongs in `g2_elog_async_glue.c` rather than the
vendored library.

The formatted-output wrapper at `[0x0044AA80,0x0044AA98)` is now a production
30-byte source leaf with explicit record-builder, event-handle, and event-set
seams; nine focused tests pin its exact call ordering and ignored return
values. The production 132-byte redirect now targets the corrected single-
owner record builder. It performs one recycle after the enqueue path exhausts
10,000 compare-and-swap retries and admits the retained enqueue seam only as
a consuming operation. The downstream transport is not attributed to
upstream EasyLogger.

The production-excluded queue candidate now closes all seven bounded queue
lifecycle functions: 256-record pool initialization, dummy reset, allocate,
recycle, enqueue, dequeue, and one-shot state initialization. It preserves the
255-record capacity, retry counters, dummy rotation, and stock omission of the
level byte during dequeue. Apple and Linux target objects and complete
relocations are pinned. The separate four-function consumer candidate closes
both callback setters, the default-metadata setter, and the bounded record
drain, including ready/metadata/callback gates, payload delivery, unconditional
recycling, and the cumulative drain statistic. Its Apple/Linux target objects
and complete relocation sets are likewise pinned. The event-worker candidate
then closes the stock 1/2/8/4 dispatch order, per-bit clears, seven-handler
persistence fanout, failure path, and exact CMSIS thread attributes across all
16 low-nibble flag combinations. Its three Apple/Linux function bodies and
relocations are identical. Remaining downstream work begins at real target
concurrency/hardware stress and atomic production integration.

The authenticated source-equivalent snapshot and license are vendored under
`third_party/easylogger`, with its bounded commit set and file hashes recorded
in `PROVENANCE.json`. The integrated Apollo-main control boundary redirects eight
control entries plus the private five-slot tag-level default initializer and
public tag-level getter while preserving the existing `0x20070BE8` logger
object, assertion hook, and port lock/unlock as explicit seams. The output
core is now production source together with its G2 async chain. Source-owned
31-byte clearing and 30-byte equality helpers
remove the stock `memset` and `strncmp` dependencies from the new filter
boundary. Pristine-upstream oracles cover state transitions, format masks,
bounded tag copying, filter defaults and first-match lookup, lock transitions,
assertion behavior, and port call ordering. The G2 asynchronous transport
remains stock.

The current dual-image helper increment additionally source-owns
`get_fmt_enabled`, its unsigned-argument and pointer-argument predicates, and
`elog_strcpy` in both Apollo images. Each image retires 320 stock bytes. The
shared 4,975-byte MIT source and 6,505-byte header hash to
`8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5`
and
`f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393`.
The 7,068-byte image-seam source hashes to
`78dc5aa9a7eb4f072b3169ae1837855007f25e1adccec7deaefecc486c8f0823`.
It preserves the main `0x20070BE8`/`0x2007456C` and boot
`0x20026700`/`0x200270E4` logger/hook bindings and their distinct
diagnostic/wait policies. Official assertion strings and wait wrappers remain
binary seams. Both profiles use 32-bit `size_t`, six levels,
a 1,024-byte line buffer, and the corrected tag record layout `level +0`,
`tag +1`, `tag_use_flag +0x20`.

The output/async production tranche replaces 1,182 complete stock bytes.
Apple's 4,423,148-byte package hashes to
`2b1008c2fc533f1257ee58bd6d0c08b449d2e12bc57d918f101586ba1d3e3d29`;
exact-root Linux's 4,425,020-byte package hashes to
`12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d`.
Both reproduced twice byte-identically, offline and without hardware access.

`elog_hexdump` and its G2 level-less raw path are now production source-owned
for the authenticated 2.2.6.10 image. Complete `B.W`/NOP replacements cover
`[0x0043DACC,0x0043DC88)`, `[0x00448CCC,0x00448D4E)`, and
`[0x0044AA76,0x0044AA80)`. Ten strict leaves close the upstream-derived main
body over bounded arithmetic formatter helpers and a clean-room single-owner
transport adapter. The two-argument raw wrapper routes only to the level-less
builder; it does not reuse the incompatible three-argument formatted submit
path, set event flags, write the reserved level byte, or recycle after the
consuming enqueue. The original candidate and host fixtures remain excluded.
Complete stock topology, Apple/Linux closure, and production pins are in
`docs/research/easylogger-hexdump-source-candidate-audit.md`.

## Identified families needing focused configuration recovery

The Cordio WSF row now also has a module-specific OS/queue closure: 12 OS
functions / 532 bytes and six linked queue functions / 242 bytes are bounded,
behaviorally recreated, and production-excluded. AmbiqSuite 2.5.1 supplies
the dispatcher discriminator; later official Ambiq source changes only the
guarded handler default from 9 to the stock-effective 10, corroborating the
variant without proving the historical G2 definition site. The 64-byte task,
8-byte queue, callers/callees, globals, and 234-row Lorelei stock-ABI matrix
are closed. At this stage the tranche was 95–98% semantically/source-family
identified and the then-current aggregate estimate was 80–85%; that estimate
is superseded by the aggregate closure later in this document. See the
[WSF OS/queue recovery](research/cordio-wsf-os-queue-source-recovery.md).

The buffer/message tranche adds three allocator functions / 430 bytes and all
seven linked message functions / 126 bytes. AmbiqSuite R2.4.2 and R2.5.1
share the exact proprietary buffer blob, while initialized SRAM pins the G2
pool configuration and the retained `third_party\cordio` path supports the
R2.5.1-or-later packaging selected independently by timer/OS evidence. The
message definitions exactly match Apache-2.0 Packetcraft r19.02 commit
`86372d84…`; r20.05c adds an absent `WsfMsgNPeek`. Lorelei's 78-row matrix
has zero exact matches and a two-byte best gap for Free. See the
[buffer/message recovery](research/cordio-wsf-buffer-message-source-recovery.md).

The assert/trace tranche adds `WsfTrace` (54 bytes) and downstream-extended
`WsfAssert` (154 bytes). AmbiqSuite R2.4.2/R2.5.1 supplies the byte-identical
proprietary source family, retained paths, and trace behavior, while the
stock assert adds local EasyLogger diagnostics, hook, and reset handling.
Packetcraft's public bodies are not exact routes. Lorelei's 26-row matrix has
zero exact matches and shows a 118-byte best deficit for pristine `WsfAssert`,
which confirms material downstream augmentation. See the
[assert/trace recovery](research/cordio-wsf-assert-trace-source-recovery.md).

The remaining port census finds no linked EFS or math translation unit. EFS's
six-by-52-byte table, media callbacks, shared validator, WDXS topology, and
markers are all absent; math's xorshift constants and combined shift shape are
also absent. These are explicit dead-stripped/excluded modules, not opaque
coverage. Packetcraft r19.02 supplies exact Apache-2.0 definitions for all 20
EFS bodies should another image require them. See the
[EFS/math exclusion audit](research/cordio-wsf-efs-math-exclusion-audit.md).

The adjacent positive census closes two `wstr.c` reverse helpers / 118 bytes.
Their definitions are byte-identical under Apache-2.0 from Packetcraft r19.02
through r20.05c and in the Ambiq R2.4.2--R4.4.1 source family. The module is
not a point-release discriminator. WDXS-only `WstrnCpy` is absent, while the
security-stack reverse helpers have 41 stock call sites. See the
[string-helper recovery](research/cordio-wstr-source-recovery.md).

The ranked public-host follow-up closes ten linked `atts_csf.c` functions /
4,814 bytes. AmbiqSuite R2.4.2/R2.5.1 is byte-identical to Packetcraft r19.02,
but stock's `AttsCsfWriteFeatures` masks three bits, rejects only a nonzero to
zero transition, and ORs accepted bits, selecting Packetcraft
r20.05--r20.05c. Stock preserves older exported spellings and adds connId
validation plus extensive logger/assert expansion, so r20.05c is a high-
confidence public behavior/API oracle rather than an exact whole-file pin.
The global layout, all 20 callers, callback sites, literal/data gaps, and
dead-stripped `AttsCsfInit` are closed. Lorelei's compact readiness result is
repository-owned and both probe profiles link with zero undefined symbols.
See the [ATT CSF recovery](research/cordio-atts-csf-source-recovery.md).

The adjacent SMP database tranche closes eleven linked `smp_db.c` functions /
2,952 bytes. Its thirteen Apache definitions are byte-stable from Packetcraft
r19/AmbiqSuite 2.5.1 through r20.05c, but stock timer event `0x20` selects the
r20 header enum. Stock's ten-record database is a product override of the
upstream default three; two unused removal APIs are dead-stripped. The full
caller, ABI, configuration-lifecycle, and pointer-ingress closure is guarded
by a fail-closed analyzer, and Lorelei's two readiness links have zero
undefined symbols. See the
[SMP DB recovery](research/cordio-smp-db-source-recovery.md).

The adjacent CCC tranche closes all fourteen linked `atts_ccc.c` functions /
2,770 bytes. Its definitions are byte-identical from Packetcraft r19/Ambiq
2.5.1 through r20.05c, while stock event `ATTS_CCC_STATE_IND=0x14` selects the
r20 ATT header family. The three-connection control block, six runtime
settings, direct and registered callback ingress, and Lorelei readiness links
are closed. Product diagnostics keep this an exact public-definition/ABI
oracle rather than a pristine whole-object claim. See the
[ATT CCC recovery](research/cordio-atts-ccc-source-recovery.md).

The ATT client-discovery tranche closes fifteen linked `attc_disc.c`
functions / 2,908 code bytes. Stock's retained r20 line layout and the
r20-only characteristic-match `break` select Packetcraft r20.05--r20.05c;
three unused included-service routines are dead-stripped. The complete
20-byte state ABI, all 20 direct calls, literal gaps, and pointer/interior
ingress are closed, and Lorelei's two readiness links have zero unresolved
symbols. See the
[ATT discovery recovery](research/cordio-attc-disc-source-recovery.md).

The ATT client-core tranche closes twenty linked `attc_main.c` functions /
3,540 code bytes. Packetcraft r20.05--r20.05c provides the public EATT core;
official Ambiq R4.4.1 corroborates the stock zero-length receive guard. Local
validation and trace expansion prevent a pristine whole-file claim. The nine
44-byte client CCBs, 17-entry send table, four-entry interface, 32 direct
calls, and zero interior-pointer ingress are enforced. The unused
`AttcSetAutoConfirm` API is dead-stripped. See the
[ATT client-core recovery](research/cordio-attc-main-source-recovery.md).

The ATT client response/request closure adds nineteen functions from three
translation units. `attc_proc.c` contributes 1,884 code bytes and roots the
17-entry response table; `attc_read.c` contributes 414 bytes; `attc_write.c`
contributes 124 bytes. Packetcraft r20.05--r20.05c is the exact Apache source
route, with official Ambiq R4.4.1 later corroboration. Per-bearer response
state and the read-long MTU lookup exclude r19/AmbiqSuite 2.x; the two linked
write bodies alone are release-invariant. Nine unused APIs are dead-stripped,
and all direct, stored, and strict-interior ingress is closed. The inherited
R4 method/table bounds mismatch is preserved as an explicit audit finding.
See the [PDU processor](research/cordio-attc-proc-source-recovery.md),
[read unit](research/cordio-attc-read-source-recovery.md), and
[write unit](research/cordio-attc-write-source-recovery.md) recoveries.

Optional `attc_sign.c` is not a stock dependency. Its mandatory callback
interface remains null after `AttcInit`, and exhaustive provider/caller and
marker checks account for all seven definitions as dead-stripped. The exact
r20.05--r20.05c/R4 file is retained only as an Apache-2.0 compatibility
oracle; no stock bytes can independently select its version. See the
[ATT client-signing exclusion](research/cordio-attc-sign-exclusion.md).

The legacy-advertising tranche closes seventeen linked `dm_adv_leg.c`
functions / 4,396 code bytes. All eighteen public definitions are
byte-identical from Packetcraft r19.02/AmbiqSuite R2.4.2--R2.5.1 through
r20.05c; unused `DmAdvModeLeg` is dead-stripped. Stock nevertheless proves a
vendor ABI fork: the advertising payload begins inline at message offset
`+8`, matching Ambiq's flexible-array `dm_adv.h` rather than public
Packetcraft's pointer field. The two-set control block, eight-entry action
table, three-entry component interface, all direct/registered ingress, and an
IAR-interleaved trailing literal pool are closed. See the
[legacy-advertising recovery](research/cordio-dm-adv-leg-source-recovery.md).

The paired common-advertising tranche closes nine linked `dm_adv.c` functions
/ 562 bytes. Stock `DmAdvSetData` allocates `len+8` and copies payload inline,
selecting the Apache-licensed AmbiqSuite R2.4.2/R2.5.1 source/header ABI and
rejecting Packetcraft's pointer-bearing message layout. Six source APIs are
dead-stripped; caller/provider/pointer closure and two zero-unresolved Lorelei
links are guarded. See the
[common advertising recovery](research/cordio-dm-adv-source-recovery.md).

The connection-manager tranche closes 57 linked `dm_conn.c`-family functions
/ 6,216 bytes. Stock selects Packetcraft r20.05's separated update component,
36-byte connection messages, and peer-SCA action, while retaining AmbiqSuite
2.5.1's warning suppression and adding product validation/logger paths. Thus
the public r20.05--r20.05c file is an exact Apache per-function oracle for 56
bodies, not an exact whole vendor file; one adjacent helper is vendor-only and
five source APIs are dead-stripped. The 196-byte control block, three CCBs,
action/interface tables, 209 direct callers, thirteen registered pointers,
and corrected Lorelei v2 handoff are closed. See the
[DM connection-manager recovery](research/cordio-dm-conn-source-recovery.md).
All 57 linked entries are now production source-owned through 55 guarded
redirects and two exact no-op copies; the five dead-stripped APIs remain in the
target compile matrix. Live behavior remains a physical-evidence blocker, not
a software admission gap.

The adjacent connection state machine closes its sole linked function / 1,598
bytes plus the exact 80-byte r20 state table. Stock has five states, eight
events, mask 7, and only the `dm_conn.c` message/HCI callers; the older
r19/Ambiq table has thirteen events and additional role-specific update
callers. The public r20 table is exact and Apache-2.0, while stock's expanded
diagnostics and three-set validation are a clean-room vendor overlay. The
body, pool, table, callers, logger relocations, action tables, and Lorelei
closures are guarded by the
[DM connection state-machine recovery](research/cordio-dm-conn-sm-source-recovery.md).

The adjacent local-device module closes all twelve linked bodies / 626 code
bytes and the full 672-byte `dm_dev.c` object footprint. Stock uses the r20
three-bit component-message ABI with 21 component slots, while official
Ambiq R4.4.1 provides the closest exact Apache-2.0 source-family oracle for
the separate vendor-command translator and reset-state clear. Six
filter/whitelist APIs are dead-stripped. The bodies, data pool, 29 calls,
three registered pointers, provider relocations, retained path, source
lineage, and Lorelei closures are guarded by the
[DM local-device recovery](research/cordio-dm-dev-source-recovery.md).

Optional `dm_dev_priv.c` is explicitly excluded from the stock link. The
21-entry initialized component table leaves device privacy (ID 1) on
`dmFcnDefault`, and exhaustive table-reference/install, marker, action-table,
and allocation-wrapper checks find no linked privacy TU. Packetcraft r20.05c
is the Apache-2.0 build-ready compatibility oracle for all 18 source-only
functions, with product `DM_NUM_ADV_SETS=2`; no surviving stock body can
discriminate its exact source version. See the
[device-privacy exclusion audit](research/cordio-dm-dev-priv-exclusion.md).

The linked `dm_main.c` router is now completely bounded: 16 functions / 484
code bytes in a 508-byte physical span. Its 90-entry HCI route table,
92-entry callback-size table, and 21-slot interface table exactly match the
official AmbiqSuite R4.4.1 family, while the older r19, AmbiqSuite 2.5.1, and
public r20 table shapes are excluded. The official later AmbiqAI import is an
Apache-2.0 exact-content oracle, not the unresolved historical producing
commit. See the [DM router recovery](research/cordio-dm-main-source-recovery.md).

The linked `dm_priv.c` object is also closed: 21 functions / 980 code bytes
plus a 28-byte literal pool. Seven ordinary actions remain on component 6 and
two AES-completion actions occupy component 15, selecting the public
Packetcraft r20.05/Ambiq R4 split architecture over r19/AmbiqSuite 2.x. Four
unused public APIs are dead-stripped but maintained and target-compiled. All
21 linked entries are production-routed: 1,688 compiled bytes plus 20 alignment
bytes under 25 strict relocations replace all 980 stock body bytes. See the
[DM privacy recovery](research/cordio-dm-priv-source-recovery.md).

The linked `dm_sec.c` object contributes eight functions / 462 code bytes in
a 488-byte interval. Its LTK handler contains the exact Packetcraft r20/Ambiq
R4 LESC guard that is absent from r19/AmbiqSuite 2.x. Four source APIs are
dead-stripped. See the
[DM security recovery](research/cordio-dm-sec-source-recovery.md).

Component-8 `dm_sec_lesc.c` is bounded to seven linked functions / 222 code
bytes and four dead APIs. Its function text is release-invariant, but stock
events `0x40/0x41` select the r20/R4 shift-three ABI. See the
[DM LESC recovery](research/cordio-dm-sec-lesc-source-recovery.md).

Component-9 `dm_phy.c` is bounded to six linked functions / 308 code bytes
and two dead APIs. The stock initializer locks, installs slot 9, and invokes
the widened 64-bit HCI feature API with mask `0x900`, selecting the exact
Packetcraft r20/Ambiq R4 source family. See the
[DM PHY recovery](research/cordio-dm-phy-source-recovery.md).

The adjacent `dm_sec_slave.c` object is complete: all three public wrappers /
148 code bytes survive in a 152-byte interval. Six application calls and zero
stored or interior pointers close ingress; event `0x29` pins the r20/R4
three-bit ABI. See the
[DM slave-security recovery](research/cordio-dm-sec-slave-source-recovery.md).

The `dm_sec_master.c` object also retains all three functions / 144 code
bytes in 152 physical bytes. Its four callers include exact SMP initiator
actions and retained `app_master.c`; event `0x28` pins r20/R4. See the
[DM master-security recovery](research/cordio-dm-sec-master-source-recovery.md).

The linked `dm_conn_master.c` unit contributes five functions / 138 code
bytes and one dead API. Its exact two-entry update table, component-14 event
`0x72`, and `dmConnUpdExecute` route exclude r19's unified state machine. See
the [DM master-connection recovery](research/cordio-dm-conn-master-source-recovery.md).

The adjacent `dm_conn_master_leg.c` unit is also complete: three functions /
136 code bytes plus a 24-byte pool. Its r20-only locked installation of the
two-entry main and update tables exactly matches stock. See the
[legacy-master recovery](research/cordio-dm-conn-master-leg-source-recovery.md).

The adjacent `dm_conn_slave_leg.c` unit is complete as well: five functions /
104 code bytes plus a 16-byte pool. Its r20-only locked installation of the
four-entry main table and separate two-entry update table exactly matches
stock. See the
[legacy-slave recovery](research/cordio-dm-conn-slave-leg-source-recovery.md).

The core `dm_conn_slave.c` unit contributes five linked functions / 206 code
bytes and one dead API. Its exact two-entry update table, component-14 event
`0x73`, and `dmConnUpdExecute` route exclude r19's unified state machine. See
the [slave-connection recovery](research/cordio-dm-conn-slave-source-recovery.md).

The downstream `l2c_slave.c` object contributes six linked functions / 1,078
code bytes and one dead API. Its retained path and exact r20
`DmConnIdByHandle`/`connId-1` behavior exclude the older handle-indexed
implementation. See the
[L2CAP slave recovery](research/cordio-l2c-slave-source-recovery.md).

The adjacent `l2c_master.c` object retains all three functions / 658 code
bytes in 700 physical bytes. Its definitions are release-invariant and are
qualified by the already-proven r20/R4 DM consumer architecture. See the
[L2CAP master recovery](research/cordio-l2c-master-source-recovery.md).

The `l2c_main.c` core object retains all 11 definitions / 1,636 code bytes in
1,736 physical bytes. Its initializer pool supplies the six exact registered
callbacks, while 16 direct calls and zero interior pointers close ingress. The
implementation bodies are release-invariant and use the selected exact r20
Apache source consistently with neighboring discriminating objects. See the
[L2CAP core recovery](research/cordio-l2c-main-source-recovery.md).

The optional `l2c_coc.c` object is absent. All 67 r20 definitions are
source-only: neither the mandatory three-callback `l2cCb` replacement nor the
required `DmConnRegister` call exists, and the image has no CoC marker. See the
[L2CAP CoC exclusion](research/cordio-l2c-coc-exclusion.md).

The complete `smp_sc_main.c` object retains 18 of 22 public definitions / 2,626
code bytes in `[0x0056CDC0,0x0056D8C4)`. Packetcraft r20.05--r20.05c is
source-invariant at blob `00515542371b1403f2716a02676064bf4aac2dcb`;
the stock cleanup-event string at value `0x1F` excludes the r19/AmbiqSuite 2.x
message layout. See the
[SMP secure-connections main recovery](research/cordio-smp-sc-main-source-recovery.md).

The adjacent `smpi_sc_sm.c` and `smpr_sc_sm.c` units retain all four functions
and all rooted const dispatch data. Their 936 physical bytes plus 1,495
scattered table bytes are closed. The responder has the r20 55-action layout
and timeout/cleanup transitions, independently excluding r19. See the
[SMP SC state-machine recovery](research/cordio-smp-sc-state-machines-source-recovery.md).

| Family | Evidence gap to close |
|---|---|
| Packetcraft/Ambiq Cordio | Definitive Cordio/Packetcraft BLE host with Ambiq FreeRTOS/HCI ports. ATT/DM discriminators require **r20.05-or-later** semantics and the bounded public source-oracle interval is r20.05–r20.05c. Packetcraft r19.02 commit `86372d84…` remains a module-specific ancestry oracle; later official Ambiq R4.4.1 import `4264b930…` is a corroborating oracle; official AmbiqSuite 2.5.1 archive `87b03680…` pins selected proprietary WSF implementation families. The aggregate audit now reconciles all 22 retained public Packetcraft candidates and all five retained Ambiq ports with focused audits and matching tests. Across the broader linked module surface, 68 analyzers, 68 tests, 68 function maps, and 69 provenance manifests leave no reusable third-party module unclassified. Product paths separately admit Packetcraft `gatt_main.c`, AmbiqSuite ANCC, and the AMOTA skeleton; EUS/ESS/EFS/NUS and Ring are proven G2-local. Every retained `platform\ble\profiles` path is now classified. The exact historical producing commit remains `null`: r19/r20/R4 bodies, proprietary ports, and local diagnostic patches prove a mixed tree rather than one pristine checkout. Remaining work is production admission/placement and hardware/controller validation. Retained application/product paths are explicitly first-party boundary work. See the [aggregate closure](research/cordio-aggregate-closure-audit.md), [ANCC recovery](research/ambiqsuite-ancc-profile-source-recovery.md), [G2 profile recovery](research/g2-ble-transport-profiles-recovery.md), [OTA/Ring recovery](research/g2-ble-ota-ring-profiles-recovery.md), [snapshot README](../third_party/cordio/README.openCFW.md), and [version audit](research/cordio-version-recovery-audit.md) |
| LZ4 | Resolved API/family and production source selection: the stock image is unequivocally decompress-only LZ4-compatible code with `read_variable_length` at `0x0054EE90`, `LZ4_decompress_generic` at `0x0054EF08`, `LZ4_decompress_safe` at `0x0054F338`, and canonical `inc32table`/`dec64table`. The evidence does **not** unequivocally separate the compatible v1.9.4/v1.10.0 stock point releases. openCFW independently selects authenticated upstream **LZ4 v1.10.0** commit `ebb370ca83af193212df4dcbadcc5d87bc0de2f0` as its maintained decompress-only production replacement; no compressor is linked. Its two void-EABI memory-provider dependencies are now source-owned. See the [promotion result](research/lz4-upstream-production-promotion-plan.md) and [stock reachability/provider audit](research/lz4-stock-reachability-memory-provider-audit.md). Remaining: optionally compact the unreachable stock/legacy decoders |
| TinyFrame | Receive and send clusters establish the post-2.3.0 MIT lineage. Ten retained `TF_Error` line arguments select the exact `TinyFrame.c`/`.h` blobs introduced by `eb75483e` as the minimum-patch core baseline; repository head `a29167a` is core-identical and changes only demo content, so the historical checkout remains bounded to `eb75483e…a29167a`. Config: SOF `0x01`, 2-byte big-endian ID/LEN/TYPE and CRC-16/ARC, 1024-byte TX buffer, no mutex with per-instance soft lock, request IDs `(next++ & 0x7FFF) | peer_bit`, responses preserve full IDs. Header CRC covers `SOF || ID || LEN || TYPE`; zero-length frames omit DATA_CKSUM. All 31 linked functions / 2,994 code bytes plus the 124-byte non-executable pool are accounted for; thirteen unused upstream APIs are dead-stripped. One instance at `0x200749C4` is selected by role: master is peer bit 1, slave peer bit 0, and application code retains no field dereference. The G2 adapter implements `magic | pristine core | magic` and is host/target checked. Production now atomically redirects eight public entries over the exact dual-profile 14-function live graph, uses source-owned `heap_4`, retains the authenticated sync wrapper at `0x00541790`, and selects explicit no-op logging. Only the lower hardware provider remains opaque; placement/routing/ownership accounting is complete and hardware frames remain. A sweep of all 113 public upstream forks found no G2 magic/config match. See the [send/version audit](research/tinyframe-send-version-recovery-audit.md), [source-admission audit](research/tinyframe-source-admission-boundary-audit.md), and [receive audit](research/tinyframe-wire-format-recovery-audit.md) |
| FreeRTOS-Plus-CLI | The reusable MIT interpreter is the classic V1.0.4-compatible core. A production-excluded snapshot selects `43defa56`/tree `12448758`, verifies the exact CRLF C/H/history/license files through compatible ceiling `1309654d`, and carries a clean 1,077-byte patch containing only G2's blank-input suppression delta `[0x005848CA,0x005848F4)`. The independently named production parameter accessor source-integrates `[0x005848FC,0x00584960)`. Separately, seven MIT clean-room leaves replace the complete G2 console task `[0x00541600,0x0054171C)` while retaining the stock interpreter ABI, 22 setup groups, and 76 proprietary descriptors. The source task preserves the 127-byte safe payload and requires receive count exactly one; it supersedes the old two-byte capacity leaf. Snapshot and candidates remain excluded, and the selected commit is not an exact vendor-provenance claim. Recovered ABI: 16-byte descriptor, 8-byte list node, dynamic registration, 128-byte interpreter boundary, expected parameter counts -1..3, and highest parameter index 11. Vendor commands/handlers and unresolved static-allocation policy remain separate. See the [snapshot README](../third_party/freertos-plus-cli/README.openCFW.md), [source recovery audit](research/freertos-plus-cli-source-recovery-audit.md), [accessor promotion audit](research/freertos-cli-get-parameter-source-candidate-audit.md), and [console-task audit](research/freertos-cli-console-task-source-candidate-audit.md) |
| nanopb | Runtime at `0x0048F000`–`0x00491400` is compatible with pristine upstream **0.4.7–0.4.9.1**. The authenticated 0.4.9 snapshot verifies tag/commit/tree/blobs/Zlib offline. Thirty-five bounded altered production functions now include private `pb_decode_inner`, public `pb_decode_tag`, the nine-leaf `pb_common.c` iterator closure, and the paired private defaults routines; pristine translation units remain unregistered. The defaults pair fully redirects 438 stock bytes to 414 source bytes and retains only `decode_field` as a fixed executable seam. Apple object, placement, redirect, aggregate, and ownership pins are complete, while Linux/Clang 22 reproduction remains pending. Even schemas/generated messages remain separate first-party inputs. See the [iterator audit](research/nanopb-iterator-cluster-source-audit.md) and [defaults audits](research/nanopb-message-defaults-source-audit.md). Remaining: close extension and field-dispatch families; exact Linux reproduction; vendor point-release evidence; and first-party schema glue. |
| IAR DLIB/compiler runtime | The retained `s200_ap510b_iar_git` paths prove the IAR project family, but the image contains no IAR/ICCARM/EWARM/DLIB version string. Lorelei Ghidra plus local Rizin split 35 early-island targets into neighboring application/DSP code and six confirmed retained runtime units: `__aeabi_memmove`, VFP `sqrtf`, `__aeabi_memcpy`, EDOM/ERANGE setters, and an errno-address accessor. Signed/unsigned 64-bit division cores and wrappers plus `frexpf`, its binary32 helper, and `ldexpf` are source-recreated. Three authenticated application banners date the build to `Jul  6 2026`. Formal Cortex-M55 support gives a practical EWARM 9.20+ floor; Ambiq's later Apollo510 reference environment makes 9.60.2 the leading compatibility candidate, while official filename rules and retained literal pools narrow likely archive families to `m7M_tl{v|s}.a`, `rt7M_tl.a`, and `dl7M_tl{n|f}.a`. All thirteen bounded runtime code units have qualified clean-room source. The production-reachable formatted-input graph is source-owned through 11 strict Cortex-M55 leaves and a guarded 2,778-byte core redirect. The formatted-output graph is source-owned through four strict leaves and a guarded 3,256-byte core redirect, including `%a/%A`, IAR `q`/`L`, `%n`, and recursive descriptors. Every exact wrapper passes `secure=0`; both adapters reject nonzero mode, so unimplemented Annex-K semantics have no production ingress. Exact release and option variants remain unproven; no matching archives are installed locally or on Lorelei. See the [runtime census](research/iar-dlib-runtime-census.md), [formatted-input closure](research/g2-iar-format-input-source-closure.md), [formatted-output closure](research/g2-iar-format-output-source-closure.md), and [formatted-I/O audit](research/g2-iar-dlib-format-io-recovery.md). Remaining work is provenance-only archive comparison, Linux replay, and hardware execution evidence blocked by unavailable physical evidence; future qualification requires authorized responsive hardware. |
| EM9305 QP/C | EM Microelectronic documents the EM9305 RTEF as QP/C ported to ARC with minor customizations. QP/C is pinned to **v6.5.1**, official commit `416dcec8820b9cdb5827497e645d0d9375db53c6`: authenticated `qep.h` in a third-party EM9305 SDK v4.2 oracle records version 6.5.1 and release code `0x8E7055B4`. The oracle is commit `e4412bc98d4e76d441d1226ca3696e53cfae5f54`, tree `f5cb9ba00df71c2612d6d64cf39e05615a2feb64`; it is not an authoritative EM repository or proof of the exact private vendor checkout. Independently, stock bodies bound ancestry to v6.3.6 `5550cca87dedf72d45250ad01e9cdeee8c4140ba` through v6.6.0+ `a280d203c0f55753b18dd9fc76104936729e471a`, excluding v6.7.0. The authenticated SDK `lib_QPC.a` proves 36 exact stock functions, including all 22 portable bodies / 2,450 bytes, the 332-byte QK SWI/restore port, `BSP_Init`, and stock-default hooks; three internal hooks are explicitly vendor-modified. All 3,052 cluster bytes are source/archive identified, divided into 26 enforced non-portable/alignment segments plus the portable bodies; no anonymous executable byte remains. Recovered configuration includes `QF_MAX_TICK_RATE=0`, `QF_MAX_ACTIVE=16`, `QF_MAX_EPOOL=2`, event/queue/pool widths, disabled Q-SPY, and the ARC saved-status critical-section ABI. The exact official portable subset is vendored under its selected upstream license. Eight portable units plus two project port units now compile with reviewed GCC 16.1.1 for ARCv2 EM and deterministically link into a closed relocatable component, enforced by `make em9305-qpc-component`. All controller bytes remain stock-retained because install placement, redirect records, and the proprietary vendor/controller composition are unresolved. See the [snapshot README](../third_party/qpc/README.openCFW.md), [ARCompact audit](research/em9305-qpc-arcompact-audit.md), and [SDK archive match audit](research/em9305-sdk-archive-match-audit.md). Remaining: install/production routing, exact private vendor hooks, physical scheduling/radio validation blocked by unavailable physical evidence, and authoritative licensed Packetcraft/EM controller source provenance. |
| EM9305 vendor SDK libraries | Six authenticated relocation-bearing SDK v4.2 archives prove **98 exact stock functions / 7,172 bytes** across QP/C, PML, sleep manager, sleep timer, protocol timer, and unitimer; 92 globally unique normalized fingerprints cover 7,146 bytes. Archive `.comment` sections pin Synopsys MetaWare ARC Compiler **T-2022.09 build 004**, LLVM 14.0.6, EM-Micro ARCv2 EM, `-Os`. Exact archive identities are `lib_QPC.a` blob `26fc11bf…`, `lib_pml.a` `45c88f15…`, `lib_sleep_manager.a` `05af021a…`, `lib_sleep_timer.a` `3713f176…`, `lib_prot_timer.a` `cf8f1f22…`, and `lib_unitimer.a` `07ed4df5…`; full SHA-256 values are enforced by the analyzer. The former 280-byte anonymous pre-QP span is protocol-timer code, the 516-byte idle path is vendor-configured `SLEEP_MANAGER_GoToSleep`, and adjacent `SLEEP_MANAGER_RCCAL_Callback` is exact. These are binary-library provenance findings, not a claim that source or redistribution rights are available. All matched spans remain authenticated cut-forward stock pending source/license recovery. See the [SDK archive match audit](research/em9305-sdk-archive-match-audit.md). Remaining: locate corresponding licensed vendor source, recover build/link configuration, and compare modified bodies; the WSF/radio/application census continues in the following row. |
| EM9305 Packetcraft/EM Bleu and expanded SDK census | Two discovery rounds authenticate 48 archives. The first 2,180 records deduplicate to 1,146 functions / 132,610 bytes; the second 8,542 records collapse to 1,201 functions, of which only 67 / 13,078 bytes are globally new. An 8-byte replay adds 124 boundary/xref-qualified functions / 2,106 bytes. Strict and NOP-aware exact-neighbor link order identify 202 placements / 11,934 bytes: 50 exact, 59 low-compared, 42 relocation-only, 38 same-size modified, and 13 singleton size-delta functions. Vector ABI resolution adds four interrupt-handler placements / 760 bytes, including three exact bodies / 574 bytes and one modified radio-TX body. Authenticated EM-system archive order adds six exact four-byte prefix leaves / 24 bytes. Combined with six enforced archives, **1,494 functions / 157,122 bytes (74.504950% of the application)** are exact in 875 intervals; function provenance is identified for 167,684 bytes (79.513296%). The residual ledger classifies 9,546 vector/alignment/post-text-data bytes and leaves 33,658 bytes as unresolved code or mixed content. `lib_emb_controller.a` blob `6a1a8e3d…` supplies 1,055 address-body fingerprints, while `lib_emb_controller_iso.a` adds ISO/BIG and link-order evidence. The profile is Bluetooth 5.4 (`BT_VER=13`, Packetcraft `LL_VER_NUM=28992`), but the non-ISO header is not a complete final-link configuration claim. Packetcraft's official public `stacks` repository ends at older r20.05c `3656312d…` / `LL_VER_NUM=1366`; the exact 2024 snapshot is authenticated only through third-party SDK blobs with proprietary notices. All bytes remain cut-forward. See the [expanded census](research/em9305-expanded-sdk-archive-census.md), [link-order ledger](research/em9305-sdk-link-order-recovery.md), and [residual census](research/em9305-residual-segment-census.md). Remaining: authoritative licensed Packetcraft/EM source and classification/recreation of the 33,658-byte unresolved code-or-mixed queue. |

The nanopb configuration already proves 16-bit field descriptors,
error strings and callback streams enabled, 64-bit values supported, packed
repeated encoding and size checks enabled, and dynamic allocation disabled.
The old local nanopb 0.3.x trees are ABI-incompatible and must not be used.
openCFW now selects 0.4.9 and vendors `pb.h`, common, encode, and decode as one
authenticated production-excluded unit. Generated message sources, Even
schemas, and application transport glue remain separate. The selection is
recorded as an openCFW compatibility choice unless stronger vendor provenance
resolves the exact shipped point release.

## Uncertain or proprietary boundaries

Do not assign an upstream identity without stronger evidence:

- IAR DLIB runtime code;
- G2 application services and audio algorithms;
- codec, touch, and EM9305 controller images; and
- charging-case firmware HAL provenance.

These remain blob-backed or are re-created only from a reviewed behavioral
contract and host/target tests.

## Priority order

1. Obtain a full external-flash capture, validate pinned littlefs v2.10.1
   read-only against it, and only then install the bounded read-only port.
2. Extend the integrated EasyLogger boundary beyond the completed dual-image
   helper quartet while keeping both distinct G2 transports isolated.
3. Complete the FreeRTOS/CMSIS queue, task, list, and port closure from the
   authenticated V10.5.1 snapshot.
4. Validate the completed FlashDB 2.1.1 read-only source/oracle against a
   golden external-flash capture before any production mount; keep every
   write/erase path denied.
5. Capture hardware TinyFrame golden packets and validate the recovered wire format against them.
6. Integrate LVGL, Cordio, and FreeType when the link strategy can reclaim
   stock code rather than duplicating large libraries in the append-only
   overlay.

## Prior authenticated FreeRTOS getter

`runtime_freertos_pc_task_get_name.c` is a bounded production port of
`pcTaskGetName` from authenticated FreeRTOS-Kernel V10.5.1 `tasks.c` at
commit `def7d2df2b0506d3d249334974f51e427c17a41c`. The 3,489-byte MIT
source has SHA-256
`d46408b0bdce9622ac1fa8c694ccc790c76169b681d0c413a4ada35fbe29d21a`.
The G2 seams are `pxCurrentTCB=0x20074A20`,
`configMAX_TASK_NAME_LEN=32`, `pcTaskName=+0x34`, and the fail-stop
assertion's source-owned `ulSetInterruptMask` target.

Production pins are: 34-byte stock SHA-256
`a25ace28ece3ca37f11da7e73945acb28f1f99d906203613e9856d2070c07817`,
raw 38-byte leaf SHA-256
`b680e949844cca19a586fbe865837f8180e592434ac1517b29ceb1482c9dd3b6`,
and final leaf SHA-256
`88edbdea558812d213013a8d319a09c63dafa86ec91a7640f427c72c77552da1`.

## Prior CMSIS-FreeRTOS `osMutexNew` production

The 9,798-byte Apache-2.0
`runtime_cmsis_mutex_new.c`, SHA-256
`28081734a384c089635681014ed028414b75d375c22f0a52a64f53e22842cf2d`,
ports the exact authenticated CMSIS-FreeRTOS v10.5.1 algorithm from commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`. Focused G2 evidence pins
enabled static/dynamic allocation and recursive mutexes, disabled queue
registry, robust rejection, the recursive-handle low bit, the 80-byte
`StaticSemaphore_t`, the 16-byte 32-bit attribute ABI, and the inlined
`IPSR`/`PRIMASK`/`BASEPRI` rejection policy.

The complete stock span `[0x0044971C,0x004497B6)` is 154 bytes with SHA-256
`09f88d8a6a64730936a52aa0c2f90d9bcb0152f6e2439919f6409110148999ec`.
Its 30 direct callers have ordered digest
`14d18197e409351bfa6ded1310c61c1f27246ebd93ecf86452d19ac0bdadbfd0`;
no alternate, interior, or stored entry exists. Two generated alignment bytes
at `[0x007B02A6,0x007B02A8)` precede the 116-byte leaf at
`[0x007B02A8,0x007B031C)`. Its five relocations at
`+0x0E/+0x32/+0x56/+0x5C/+0x64` bind only to the source-owned scheduler-state
getter and static/dynamic mutex creators at
`0x007AECFC/0x007AEEBC/0x007AE100`.

That release's overlay was 114,680 bytes with SHA-256
`7603cf2a0de6e8b05d66dc356bf3e0701f6157536d29bdac8ad692dc56e0362c`;
the 3,638,076-byte Apollo-main component hashes to
`f696c6dfbd8ab1f7b5cc44fdc06fcdc5baf44f368ad55130e7571d82ee31ec82`.
The 4,416,258-byte package hashes to
`11d40cd1b3648f96b5ec98c9fa2dff6de121e878978206a0a9694ede38d3a0ff`.
The focused production gate passes 10/10 tests offline; no hardware was
accessed.

At that point `osSemaphoreNew` remained candidate-only pending production
closure of `heap_4`.

## Prior FreeRTOS heap and CMSIS semaphore production

The pristine authenticated V10.5.1 `heap_4.c` now supplies the algorithms for
the bounded 16,885-byte MIT `runtime_freertos_heap4.c` adapter, SHA-256
`d848b90a00da24db963c49dbff2472314b2a76c6cf269efef46e6cac56889986`.
Its four source leaves preserve the recovered G2 heap layout and accounting
globals. The 5,851-byte MIT `runtime_freertos_queue_delete.c`, SHA-256
`fa8033f61e418dbfb304dd7443dea340bfff88958df493e276ea92db4491da2b`,
closes `vQueueDelete` over source-owned heap free and interrupt masking.

The 11,566-byte Apache-2.0 `runtime_cmsis_semaphore_new.c`, SHA-256
`a947868d3fbcfc7f41d021210355e0ff777d49d3db84fa0da71a255d319c1527`,
ports exact authenticated CMSIS-FreeRTOS v10.5.1 `osSemaphoreNew`. Its
178-byte leaf closes over source scheduler, queue creation/send/delete, and
counting-semaphore dependencies. The overlay/component/package hashes at that
historical milestone were
`6359e4e8c824af3cea36280a1aabd6ad671027e38fb3263fe9ac0cbb292660b4`,
`00d112e265f40dd8bf98fc9021bba54b3bcc94f159111b2f4815d5484e91c67c`,
and
`064c9429352132cee2a5dfe45c2bf52349e10111b89db91f093b1ce16ed0c2b0`.

## Prior dual-image EasyLogger helper production

The shared EasyLogger helper quartet now runs from source in Apollo main and
the S200 bootloader. Main's 115,910-byte overlay and 3,639,306-byte component
hash to
`e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d`
and
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`.
Boot's 622-byte overlay and 149,222-byte provider hash to
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`
and
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.
The 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`;
its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`.

## Preceding FreeRTOS tick-getter production

The production source boundary reuses the MIT FreeRTOS-Kernel V10.5.1
algorithms at commit
`def7d2df2b0506d3d249334974f51e427c17a41c`. The pinned 223,695-byte
upstream `tasks.c` hashes to
`14020d617b96dd2814e1211f6e3b645bcf5e2bd3179c23fe7dd16bc666fe9463`.
The bounded 3,412-byte `runtime_freertos_tick_count.c` and 1,186-byte header
hash to
`948d1b2de6026adc7cf84a34a359c859c32126b3afcafe92c2347f5f7ab56363`
and
`adc4065b3504a7eacb2e29e2d357636917e2b690afc49b265689e36d66171dae`.
Focused disassembly supplies only the G2 boundary and state binding.

The exact official spans are `[0x00454EFE,0x00454F06)` for
`xTaskGetTickCount` and `[0x00454F06,0x00454F10)` for
`xTaskGetTickCountFromISR`; their aggregate 18-byte SHA-256 is
`d0b93ff29439d26b92dcd56fd012a9dab842364f7c5f4b4f7f39a27ed8cfe077`.
The earlier proposed ISR entry at `0x00454F08` is corrected to an interior
instruction. Nine normal callers and the sole ISR caller retain the official
entries.

Apollo main places two generated alignment bytes at
`[0x007B07EA,0x007B07EC)`, a relocation-free 12-byte source provider at
`[0x007B07EC,0x007B07F8)`, and the two four-byte source getters through
`0x007B0800`. The provider binds `xTickCount` at `0x20074A34`; each getter
has one jump relocation to it. Complete non-linking redirects and NOP fill
replace the 18 official bytes.

The 115,932-byte overlay and 3,639,328-byte main component hash to
`272ba0e0492b0c6b721adec53a007809158d6871ccdb7ec52d4b6ceadd4b4529`
and
`615304858150f5ee6b7b4c62a714629375010c6f4ab20bea1b6958daa6a5b4af`.
The raw main application partitions into 116,118 source, 81,622 generated,
and 3,441,556 opaque bytes. Builder accounting is 116,114 source-owned bytes
including 182 in place, 81,626 generated patch-site bytes, 81,808
replaced-stock bytes, 3,441,556 opaque base bytes, and the 32-byte wrapper.

The 4,417,782-byte package hashes to
`3bf635fb81439451e67642dc5ce11dde47a1773bda8ef11c12b35cd9bbbec01d`
and classifies 116,738 source bytes (2.642457%), 83,415 generated bytes
(1.888165%), and 4,217,629 opaque bytes (95.469378%); 200,153 bytes
(4.530622%) are controlled. Its 596,957-byte flash plan hashes to
`2b89447a0a867d1ec34f51e5798a4da7b28effe8bc5d7e27b1b7f24ce1c9cd3c`
and records 828 placed, two unresolved, five container-only, and six
protected regions. Of the placed regions, 53 are source-compiled, 574 are
generated source-entry replacements, and 18 are generated alignments. Boot
ownership remains 620 source, 817 generated, and 147,785 opaque bytes.

## Preceding FreeRTOS missed-yield production

The complete stock `vTaskMissedYield` function is the ten-byte span
`[0x004555E6,0x004555F0)`, SHA-256
`8cada1af8ad4973f2ad647d45c8a0ac9c56fdf2d8b270607844b7940eb7d5d2d`.
It has exactly two direct callers at `0x00441FA2` and `0x00441FD8`, and no
alternate entry or stored function pointer. FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` identifies its semantics
unequivocally as `xYieldPending = pdTRUE`; focused disassembly recovers the
G2 word at `0x20074A44`.

Apple clang 21 and Homebrew clang 22.1.8 emit the same relocation-free
14-byte source leaf. Canonical placement is
`[0x007B0800,0x007B080E)`; Linux placement is
`[0x007B0F38,0x007B0F46)` after two alignment bytes. The canonical overlay,
component, and package are 115,946, 3,639,342, and 4,417,796 bytes, with
SHA-256 values
`a24cd67ac1d308b8812c329a294f3f07cbe9db4bc815be3fe081ba0c2fd9008c`,
`f037745e9b85d16fc048ba2fedb282f7fc498a524a90b803b652556e286cf77d`,
and
`f06fdc7a1e9034e72321680b35fbd542b12dad06135e6f01f701d670dba676ae`.
The overlay contains 592 functions and 559 patch sites; builder accounting
is 116,128 source-owned, 81,636 generated patch, 81,818 replaced-stock, and
3,441,546 opaque bytes.

Linux independently pins a 117,794-byte overlay, 3,641,190-byte component,
and 4,419,644-byte package with SHA-256 values
`00cbcf99a63f69fa7fd2af607685179ac73edeafd0fc8c4e1ad49b6a13a02c0e`,
`f134beba731634fd81b42b143e3b1e414b4b8c07a9e3f009cc49e7c8258b1657`,
and
`13409c4d615651f1b8cb5618d6d1cb1a4d5095e8245c41b41c585a258c9114e1`.
Its aggregate is source-root-sensitive because TLSF embeds absolute
`__FILE__`; the recorded root spelling is
`/Users/kalani/Repo/SybilSightABCD`. See
[`research/freertos-missed-yield-source-boundary-audit.md`](research/freertos-missed-yield-source-boundary-audit.md).

## Preceding FreeRTOS event-item and mutex-held production

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` unequivocally supplies the
current `uxTaskResetEventItemValue` and
`pvTaskIncrementMutexHeldCount` source bodies. The recovered boundaries are:

| Function | Stock span | Bytes | Stock SHA-256 | Caller |
|---|---|---:|---|---|
| `uxTaskResetEventItemValue` | `[0x00455ACA,0x00455AE0)` | 22 | `76463ec53fbc06884c159bf5b7d01708c06e404e9b51bdcaab307b219179c049` | `0x0047ECCE` |
| `pvTaskIncrementMutexHeldCount` | `[0x00455AE0,0x00455AF6)` | 22 | `3cca7b821687976e59eccd737dc20b2064b86d66195c6f60f6a7cc2353f40d2f` | `0x00441D46` |

Both functions preserve volatile evaluations through `pxCurrentTCB` at
`0x20074A20`. Reset binds event-list value `+0x18`, priority `+0x2C`, and
56 priorities. Mutex-held binds field `+0x64` and
`configUSE_MUTEXES=1`.

Canonical placement is `[0x007B0810,0x007B082A)` for the 26-byte reset leaf
and `[0x007B082C,0x007B0844)` for the 24-byte mutex-held leaf, with two
alignment bytes before each. Their SHA-256 values are
`04fee613f7c2fb46a3e6f5832f7ea61875543a30160757ffd63579b58f0c45c6`
and
`494b41afb48389988e2678920ae7e1796b41a3d568e5c01c35c12c48bf7b57bf`.

The canonical overlay, component, and package are 116,000, 3,639,396, and
4,417,850 bytes, with SHA-256 values
`203b31ea09e03c919da51b4d194cab2c3325ad5d5eed3efc7464018af90e2059`,
`78375130a88e6ec0d14bc936b8f16f4535056344288419baba83d81fd4f3bdc3`,
and
`9ffe927fdb587db9fae07043d7dc0938d2519c95d29e71cd0dca021cadf31d85`.
The overlay records 594 functions and 561 patch sites; builder accounting is
116,182 source-owned, 81,680 generated patch, 81,862 replaced-stock, and
3,441,502 opaque bytes.

The package contains 116,802 source, 83,473 generated, and 4,217,575 opaque
bytes; 200,275 bytes are controlled. Its 604,237-byte flash plan hashes to
`c25b80e357274ee25903c74d6472cb0a3ab30d6f5d702a053b88c145e3ddd521`
and records 838 placed, two unresolved, and five container-only regions.

Linux places the leaves at `[0x007B0F48,0x007B0F62)` and
`[0x007B0F64,0x007B0F7C)`. Its overlay, component, and package are 117,848,
3,641,244, and 4,419,698 bytes with SHA-256 values
`12e592da338cbcf99ee81ec3551ff5ae22410f34387ba35dcbdfbf38294f8cc9`,
`a81f7ca5c4219f9f31820a9f3e18aa6f5bb85004b7bedc9f25f9083dbdfd14e6`,
and
`e86eb0003e5b9f7f15c416ab9485e3457ce2082b17720d85ef59b6f198efe4b2`.
The reviewed Linux source root remains
`/Users/kalani/Repo/SybilSightABCD`. See the
[reset audit](research/freertos-reset-event-item-value-source-boundary-audit.md)
and [mutex-held audit](research/freertos-mutex-held-source-boundary-audit.md).

## Prior FreeRTOS scheduler-suspend and timeout-state production

That release added two more unequivocal FreeRTOS-Kernel V10.5.1 task leaves
from authenticated commit
`def7d2df2b0506d3d249334974f51e427c17a41c`:

| Function | Stock span | Bytes | Stock SHA-256 | Recovered G2 binding |
|---|---|---:|---|---|
| `vTaskSuspendAll` | `[0x00454D7C,0x00454D88)` | 12 | `3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2` | volatile `uxSchedulerSuspended` word `0x20074A58`, 32-bit increment and barrier ordering |
| `vTaskInternalSetTimeOutState` | `[0x00455556,0x00455566)` | 16 | `6ff12b123d1647953300d002a439daf4df52f96e369eebbb0b183a1a4fb3e862` | `xNumOfOverflows=0x20074A48`, `xTickCount=0x20074A34`, `TimeOut_t` size/alignment 8/4 and offsets `+0`/`+4` |

The timeout leaf has four direct callers at `0x00441886`, `0x00441B90`,
`0x00441CBC`, and `0x004555D0`. Whole-image scans close alternate branches,
interior transfers, and stored pointers. Apple clang 21 and Homebrew clang
22.1.8 emit the same relocation-free 18-byte source body, SHA-256
`8319202babe42ee571774682793c4c4c1a54c3a72826a92ba5c60273ba451c6a`,
while preserving overflow-read/store before tick-read/store.

Canonical placement is `[0x007B0844,0x007B0854)` for suspend and
`[0x007B0854,0x007B0866)` for timeout. Linux placement is
`[0x007B0F7C,0x007B0F8C)` and `[0x007B0F8C,0x007B0F9E)`. Neither profile
requires alignment padding between the two leaves.

That release's production pins were:

| Profile / artifact | Bytes | SHA-256 |
|---|---:|---|
| canonical overlay | 116,034 | `d0b36ab3661f3b3487e3962bfe58d9f588f6a6f1ea14e1d9389f7e45d98094bd` |
| canonical Apollo-main component | 3,639,430 | `8a747653cc4d938e447197f2bec199933b68072318f0743e3cd85dcf656db8bc` |
| canonical core-source package | 4,417,884 | `e3b7f29a19a4b3c19a14377a8ea8a77d14458a48678955d406ef7eea274dd6e7` |
| Linux overlay | 117,882 | `5c3c381342bb57ec4f33192ea89c2d40e8f0018c39c7092551243be7159dc326` |
| Linux Apollo-main component | 3,641,278 | `6bead197d657c26fa6ba84210949c8e28b266fbf63a8f908edda1d64516a3163` |
| Linux core-source package | 4,419,732 | `a801d1ecbf83780701cbb7fdc1ae14401a656ba79102877458a3a88c73bc3fc4` |

The overlay records 596 functions and 563 patch sites. Builder accounting is
116,216 source-owned, 81,708 generated patch, 81,890 replaced-stock, and
3,441,474 opaque bytes. The package records 116,836 source, 83,501
generated, and 4,217,547 opaque bytes; 200,337 bytes are controlled. Its
608,608-byte flash plan hashes to
`c6cde87716d8ff407e06998aadaaa0da6e78e5689ea1ac2963f104178447cae2`
and records 844 placed, two unresolved, and five container-only regions.

The reviewed Linux root remains `/Users/kalani/Repo/SybilSightABCD` because
unrelated TLSF data embeds absolute `__FILE__`. See the
[timeout-state audit](research/freertos-timeout-state-source-boundary-audit.md)
for the complete source, topology, ABI, and redirect evidence.

## Prior authenticated scheduler-cluster reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies the production
implementations of `vPortYield`, `vPortEnterCritical`, `vPortExitCritical`,
`prvResetNextTaskUnblockTime`, `xTaskIncrementTick`, and `xTaskResumeAll`.
Focused disassembly supplies only the G2 configuration and ABI bindings:
fixed scheduler globals, list/TCB layout, `configMAX_PRIORITIES=56`, tick and
time-slicing policy, interrupt-mask providers, and port MMIO addresses.

The tranche replaces 770 stock bytes and adds 776 compiled bytes plus six
Apple alignment bytes. Its canonical overlay/component/package pins are
116,816 / 3,640,212 / 4,418,666 bytes with SHA-256 values
`b9cb2b00d4859650d120ff713a8af9a1ca626876b46bac751098abdbca575153`,
`fcb218fd5d9a33b2398cd046550b26258ca9da90d423c50ae635203535614a58`,
and
`5a31772a8a4fb746fa9eff53d618541fd38cf44a93c9d602eb88e15d142cef01`.
This is source reuse under the vendored MIT notice, not a decompiled
reimplementation. G2-specific seams remain explicitly pinned and tested.

## Prior authenticated LZ4 v1.10.0 source reuse

The maintained production decompressor is now built from authenticated
upstream LZ4 v1.10.0 commit
`ebb370ca83af193212df4dcbadcc5d87bc0de2f0` under BSD-2-Clause. This is an
openCFW selection: it does not assign that point release to the stripped stock
image. The selected closure is intentionally narrow—`LZ4_decompress_safe`,
64 bytes of read-only `inc32table`/`dec64table`, a four-byte G2 ABI adapter,
and a 30-byte EvenHub mode-2 adapter. No compressor, frame API, writable LZ4
state, or unrelated upstream function is retained.

Apple clang emits 1,660 bytes of relocated decoder text at
`[0x007B0B74,0x007B11F0)`, followed by the tables at
`[0x007B11F0,0x007B1230)`, safe adapter at
`[0x007B1230,0x007B1234)`, and mode-2 adapter at
`[0x007B1234,0x007B1252)`. Linux clang emits 1,690 text bytes at
`[0x007B12A8,0x007B1942)`, two alignment bytes, the same 64-byte tables at
`[0x007B1944,0x007B1984)`, then the adapters at
`[0x007B1984,0x007B1988)` and `[0x007B1988,0x007B19A6)`.

| Artifact | Apple clang 21 | Linux clang 22.1.8 |
|---|---|---|
| Overlay | 118,574 / `1a0b92e12203b78f48191969744128bfbcc2559c811ae40a1f393370eceacea9` | 120,450 / `2901320d6169c2b9ad49d501cb25e7f50ceaa90b94e7d0640f80d318932d8fc7` |
| Apollo-main component | 3,641,970 / `6621c7d0403e37d0598c5f2f521633afb13b98034542c8010cf9d210f576e91d` | 3,643,846 / `140cac71e8ec612f2129800ee9a205c30f743dfd51664207c1661fdb337d8f8d` |
| Core-source package | 4,420,424 / `d576be2c4626006a830593a5ad1aae21da8ee3e16d67d80c62eb8f3994bfc294` | 4,422,300 / `cb1516c2c61402626a723f05f4fb315e8af91adae599818830b2f8e1ffee0bf8` |

The original primary mode-2 and hand-decoder sections are retained under
`_legacy` names and are unreachable, preventing address churn in later
functions. The stock generic decoder and reader likewise remain unreachable
opaque compatibility bytes. The active object still binds authenticated stock
void-EABI `__aeabi_memcpy` at `0x00439BE4` and `__aeabi_memmove` at
`0x00439710`; full provider spans, overlap paths, and the memmove-to-memcpy
tail are audited.

Canonical component accounting is 118,756 source-owned, 82,478 generated
patch, 82,660 replaced-stock, 3,440,704 opaque-base, and 32 wrapper bytes.
Canonical package accounting is 119,370 source, 84,277 generated, and
4,216,777 opaque bytes. This integration was validated offline; no hardware
was flashed or executed.

## Prior authenticated FreeRTOS queue/task closure reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies production
`xTaskRemoveFromEventList`, `xQueueGiveFromISR`, and
`prvTaskCheckFreeStackSpace`. These are source reuse under the retained MIT
license. Disassembly contributes only the G2-specific queue/list/TCB/global
bindings, caller topology, and stack configuration.

The three complete stock spans total 468 bytes; the selected source leaves
total 490 bytes and need one two-byte alignment region per profile. Apple
places them at `0x007B1254..0x007B143E`; Linux places them at
`0x007B19A8..0x007B1B92`. The package pins are 4,420,916 bytes /
`1b3ea44cc1cbd8004585e0208e33605c4e5f59229fdc5cb23395d19e0ba120f2`
for Apple and 4,422,792 bytes /
`b93b39eb8e6f70e144b517dd7d770adcea67f62aa1100d722d4d1d0e6f8907ea`
for Linux. The reviewed exact-root Linux recording and two normal rebuilds
were byte-identical. No physical device was used.

## Preceding authenticated FreeRTOS timeout-check reuse

Authenticated FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now also supplies production
`xTaskCheckForTimeOut`. This is source reuse under the retained upstream MIT
license, not a decompilation. Focused disassembly supplies only the G2
configuration and ABI facts needed to instantiate that released algorithm:

- official span `[0x00455566,0x004555E6)`, 128 bytes, SHA-256
  `83a983995a285b3257a1213bdbe3fa0542bae0c9296a88fd8b22c1388abdf72c`;
- `INCLUDE_vTaskSuspend=1`, `INCLUDE_xTaskAbortDelay=0`, 32-bit ticks, and
  `portMAX_DELAY=UINT32_MAX`;
- `xTickCount=0x20074A34`, `xNumOfOverflows=0x20074A48`, and the eight-byte
  `TimeOut_t` layout; and
- the three callers plus the already source-owned assertion, critical, and
  internal timeout-snapshot providers.

Apple and Linux append a 136-byte relocation-free source leaf after two
alignment bytes. Their leaf hashes are
`33f0782fa8af468bccf78b558cc010a9f7a89f30c7c76abced9a799feb6a93f5`
and
`486515dfdbdb1e175321445df167dca27357f270421b2d00492268e8da7c815c`.
The canonical and Linux packages are respectively 4,421,054 bytes /
`4fb13f64e81b8a6ef9bdf784ac38d5fc08ed03e4d310601a48bf4b395c20ab37`
and 4,422,930 bytes /
`22c0e367882b005c1b85ee40d138e596c423d5a6335b8d93bc5a68873323c3ab`.
All provenance checks, compilation, assembly, and package inspection were
offline; no hardware was connected or operated.

## Preceding authenticated FreeRTOS semaphore-take reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies production
`xQueueSemaphoreTake` and its private
`prvGetDisinheritPriorityAfterTimeout` dependency. This is authenticated MIT
source reuse; disassembly supplies only the recovered G2 configuration and
ABI. The Apple leaves are 602 and 18 bytes at overlay offsets 120,728 and
120,708; Linux emits 600 and 18 bytes at offsets 122,584 and 122,564. The
candidate's sole relocation binds to the source helper. The stock helper stays
byte-identical but has no remaining assembled branch or stored-pointer
reference, so no unnecessary redirect was emitted. Final Apple/Linux package
pins are 4,423,180 /
`74278f0c7ae44e5364a6bca3abc762fcb48a0b2dcb06d816412566c5e974541d`
and 4,425,034 /
`b07ee2e813356553bd5c8f0a7c2f951376f8b338be6e53b6aff75824062f47f1`.
No hardware was operated.

## Preceding authenticated littlefs private rewind reuse

The littlefs v2.10.1 snapshot at commit
`0494ce7169f06a734a7bd7585f49a9fa91fa7318` now also supplies the bounded
production adaptation `runtime_littlefs_file_rewind_private.c`. Its exact
192-byte upstream definition begins at `lfs.c` offset 118,157 and hashes to
`74638292061613417c2ce7c6bbed200d2bee046c35a7a835fb4d9bb183ab755a`.
The 1,239-byte source and 1,743-byte header hash to
`e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8`
and
`7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56`.

The selected source reuse is BSD-3-Clause. Focused disassembly supplies only
the G2-specific private seek binding at `0x004CE3BC`, the sole public-wrapper
caller, stock boundary, and placement. It does not authenticate the vendor's
filesystem port or authorize format/erase/hardware behavior.

## Preceding bounded CmBacktrace production reuse

The authenticated CmBacktrace compatibility baseline at commit
`73714489f9d8af130aacb515586b397b604a5768` is now represented in production
by the bounded MIT-licensed
`components/shared/cmbacktrace/runtime_cmbacktrace_get_cur_thread_name.c`.
This production source reuses the upstream FreeRTOS behavior only; commit
selection remains an openCFW compatibility choice, not proof of Even's exact
vendor checkout. The vendored pristine snapshot remains production-excluded.

Device-specific behavior lives in the separately recovered openCFW adapter:
current TCB at `0x20074A20`, task-name offset `0x34`, including null-to-`0x34`.
The adapter is not attributed to upstream CmBacktrace. Both Apple and Linux
target objects and placements, the single stock entry replacement, and the
complete ingress closure are fail-closed. No hardware was operated.

## Preceding bounded nanopb production reuse

The authenticated nanopb 0.4.9 snapshot is now used as the explicit
compatibility baseline for three altered production leaves:
`components/shared/nanopb/runtime_nanopb_decode_varint.c` and
`components/shared/nanopb/runtime_nanopb_skip_varint.c`, plus
`components/shared/nanopb/runtime_nanopb_close_string_substream.c`. Version
0.4.9 is an
openCFW compatibility selection within the authenticated 0.4.7–0.4.9 range,
not proof of the vendor's nanopb revision or checkout; all three pristine
releases remain indistinguishable under recovered G2 evidence.

For `pb_decode_varint`, focused disassembly supplies the exact stock range,
16-byte callback stream ABI, three-caller topology, overflow literal, and the
reviewed `pb_readbyte` seam at `0x0048F454`. For `pb_skip_varint`, the verifier
pins the altered source and header, authenticated upstream function bytes,
36-byte stock range `[0x0048F628,0x0048F64C)`, and sole `pb_read` seam at
`0x0048F3BE`. For `pb_close_string_substream`, it pins the 42-byte stock range
`[0x0048F7CA,0x0048F7F4)`, all three callers, zero-remainder and failed-read
semantics, the exact 16-byte stream layout, and the same sole stock `pb_read`
seam. The 2,061-byte source and 2,537-byte header hash to
`736e7ec228f9282ba5b093fd482441e6e2017fff860d989dc3aadb2bdeff0fcb`
and
`851af370162d79f4bd0be8b8bb9a5731d47cf02527078b9e278019340f2d65d4`.
The broader pristine `pb_common.c`, `pb_decode.c`, and
`pb_encode.c` files remain production-unregistered. The offline snapshot
verifier permits only these three bounded registrations and rejects direct
broad-runtime linkage. All three production sources retain Zlib terms;
host-only candidate and oracle fixtures remain excluded.

Both compiler profiles pin the relevant raw objects, extracted text and
relocation closures, full-span redirects, aggregate component, and package.
Behavioral qualification pins authenticated upstream semantics and exercises
the bounded production behavior with host oracles. All work was offline; no
firmware was signed or flashed and no G2 hardware was operated.

## Preceding authenticated FreeRTOS queue-reset/unordered-removal reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now supplies production
`xQueueGenericReset` and `vTaskRemoveFromUnorderedEventList`. Focused
disassembly supplies only G2 queue/list/TCB ABI, fixed-address scheduler
state, feature gates, assertion providers, and entry topology. Full-span
redirects replace the 180-byte and 218-byte stock bodies; all Apple and Linux
source leaves are relocation-free.

Apple's overlay/component/package pins are 121,718 /
`76e21a06d75ed5c3beb5343014621e432726ea285e46d54978a4de43d9b6b666`,
3,645,114 /
`c32ff5c5daf946812df503cfaa328c1cc22dc4206201da0b752a365f235e0108`,
and 4,423,568 /
`0e18c7c435edaff3fa5b692e8c17251f075c472933c93b05153ac0307e6f4ca8`.
The exact-root Linux pins are 123,570 /
`6885adb2da4019a5595fd14fefe7e6682e6d32e63b45c47b3436828a1238d288`,
3,646,966 /
`657140490b0bd0b1f5aeb44505cc24b01377d16254f91c30e31893d1890731ca`,
and 4,425,420 /
`d7870c13b9417f8a9866ad6b87858e712c1c6c005b0b534bdd1d4ba540b64d60`.
This is authenticated MIT source reuse qualified offline; no hardware was
operated.

## Bounded dual-image littlefs tag-ID production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now also
supplies `components/shared/littlefs/runtime_littlefs_tag_id.c` and its
header. The exact upstream authority is `lfs.c[10702:10793]`, 91 bytes,
SHA-256
`50140c563689852013dfad180ec3b6464c6b6c5b22854f5492d63cf5de57fbe2`,
at commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. This establishes
source-equivalent behavior, not Even Realities' exact historical checkout.

Focused disassembly contributes only the 32-bit scalar ABI, identical stock
spans `[0x004CAEB0,0x004CAEB8)` and `[0x00410BB8,0x00410BC0)`, complete
50/41 direct-caller topology, and entry-replacement addresses. The common
six-byte source leaf is provider- and relocation-free and implements only
`(tag & 0x000ffc00) >> 10`.

Final profile placements and aggregate artifact identities are pinned in the
memory-map and reproducible-build ledgers. The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. This bounded scalar reuse imports neither
the broad library nor a block-device, mount, format, program, or erase path,
and it authorizes no signing, flashing, reset, boot, or hardware operation.

## Current bounded dual-image littlefs tag-validity/type1 production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now also
supplies altered BSD-3-Clause adaptations of `lfs_tag_isvalid` and
`lfs_tag_type1`. Their exact upstream authorities are `lfs.c[10042:10129]`
and `lfs.c[10232:10326]`, with SHA-256
`bb8e571d6dbddd1fe446ec7b4838979a4ab9bd6d6184e2f8d9b6c00cc0835b13`
and `ebf0229d6e0f78175c43641b09906fea19575fc3f34ac8862ae60159df1ec743`.
This proves compatible source behavior, not Even Realities' exact checkout.

Focused disassembly contributes only the 32-bit scalar ABI, identical
main/boot stock bodies, three/eight caller sets, entry topology, and patch
addresses. Both production leaves are provider- and relocation-free and are
registered atomically in the two overlays. The final Apple package is
4,426,458 bytes, SHA-256
`f0e7e4c5e090ea558968b6293f3eec0a7f88a6126ea164547c25c8462b60be23`;
exact-root Linux is 4,428,278 bytes, SHA-256
`07cee183416db26bbe13673c1123e4ef19593d6343caa63c6c94791a210dc0dc`.
Complete component hashes remain fail-closed in the overlay registries and
canonical manifest.

The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. The two scalar helpers do not import the
broad library, a block-device port, or a format/erase path. Offline assembly
is GO; signing, flashing, reset, boot, filesystem mutation, and hardware
operation remain NO-GO.

## Preceding authenticated FreeRTOS task-list initializer reuse

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` now also supplies the bounded
production adaptation
`components/shared/freertos/runtime_freertos_task_lists_initialize.c`. The
exact upstream boundary is `tasks.c[150869:151768]`, 899 bytes with SHA-256
`0908b0fb7a1b43d6d4fa2bd8212ba069ac6a8d4d036b4f973ae7f3baa6dd6e63`.
The 3,529-byte source and 5,886-byte header retain MIT terms and hash to
`58773452256b0f44647040085bbcc7a896a1cbd3efd0c5c4b4de3ddfe1a9e857`
and
`6fe827f6d2659a784e8b3e22fa096162dfd4003146c0425222efc92c63baef9e`.

The recovered G2 list ABI, 56-priority selection, fixed Apollo-main SRAM map,
sole caller, overlay placement, and generated `replace_freertos_task_lists_initialize`
entry replacement are compatibility evidence, not upstream provenance. The
production symbol `open_cfw_freertos_task_lists_initialize` closes its only
callable dependency over source-owned `open_cfw_freertos_list_initialise`.
The separately compiled bootloader homolog remains excluded. Qualification
was offline; no firmware was signed or flashed and no hardware was operated.

## Preceding EasyLogger G2 single-owner glue selection

The downstream/private G2 record builder at the official entry
`[0x00448D4E,0x00448DD2)` now selects the corrected single-owner openCFW
implementation. This does not change the upstream attribution boundary:
`elog_output` remains the authenticated EasyLogger-derived portion, while the
record builder, enqueue ownership contract, and submit wrapper remain G2
application glue. The stock-compatible double-recycle builder is retained as
an audit oracle and is not linked into production.

Apple overlay/component/package pins are 121,706 / 3,645,102 / 4,423,556
bytes and exact-root Linux pins are 123,558 / 3,646,954 / 4,425,408 bytes.
Their respective SHA-256 triples are
`03dd692b55204fc36f67469ece0175e981b6281123a1b20b3db592ee2dd0b44c`,
`ae123c6a119bfebd0420898aef590a9ba1fd7f7dc7da00b3d347f6573bba43ec`,
`7cf86c7311b4684eb6d2fdd4f832989317c858733f8438dc01ee649fcd1cf250`
and
`f2c33def6131981c1a283968bc02bd55cde32536f4f33a7fa3cbf905d42693fc`,
`5ff7dd5894b74573971912371f22d0b463c32552ea1037441e1de992a6a8d3b9`,
`fe49c0d9830327a0fdd0e7815a147bb6b810e27b9a9277b3bbfe9021de247a75`.
No hardware was operated.

## Preceding bounded nanopb fixed32 production reuse

The authenticated nanopb compatibility snapshot now supplies a fourth
bounded production adaptation,
`components/shared/nanopb/runtime_nanopb_decode_fixed32.c` and its header.
The selected baseline is official nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, but the exact upstream
definition is identical across authenticated pristine 0.4.7, 0.4.8, and
0.4.9. This establishes compatibility, not Even Realities' historical point
release or checkout.

The 1,975-byte altered Zlib source and 1,750-byte header hash to
`fefd8a899174fb9332c366df691dc2c8ec6f4792f3fd464b65dbb573ace8ee19`
and
`738e4c7d4ea983b0ba967fa42cdcc61cb2e20837531bc6176b7f95a5fe8e2460`.
Focused disassembly supplies only the G2 stock span
`[0x00490190,0x004901AC)`, sole caller, recovered stream boundary, little-
endian behavior, and provider address. The leaf retains one call to stock
`pb_read` at `0x0048F3BE`; neither that provider nor the broader pristine
`pb_common.c`, `pb_decode.c`, or `pb_encode.c` translation units become
source-owned.

Both reviewed profiles pin the same 960-byte object and 50-byte unrelocated
text, with exactly one call relocation at offset 10. Full-span redirects and
that phase's aggregate component/package artifacts are qualified offline.
The 648/597/79 config census belongs to this preceding tranche. No signing,
flashing, or hardware behavior is claimed.

## Preceding bounded littlefs tag-type production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now supplies
the bounded BSD-3-Clause production adaptation
`components/shared/littlefs/runtime_littlefs_tag_type2.c` and its header. The
selected commit is `0494ce7169f06a734a7bd7585f49a9fa91fa7318`; the exact
92-byte upstream definition hashes to
`65f614cf5ed7152f7ad2176547453c329b1f15442e550ef6632b0f7773970f78`.
This establishes source compatibility, not the vendor's exact historical
checkout.

Focused disassembly supplies only the scalar `uint32_t` ABI, official stock
span `[0x004CAE90,0x004CAE98)`, two direct callers, and closed entry topology.
The ten-byte source text is relocation- and provider-free and hashes to
`88be40d05d37142bf0bae8306026d8c405a4f8f441aabd87ee6731557d4149fd`.
Apple places it at `[0x007B29A8,0x007B29B2)` and exact-root Linux at
`[0x007B30C4,0x007B30CE)`.

The current config census is 649 functions, 598 patches, and 80 relocated
leaves; the Apple build report records 645 overlay functions and 594 generated
patch records. Apple overlay/component/package/plan sizes are 124,558 /
3,647,954 / 4,426,408 / 698,204; exact-root Linux uses 126,378 / 3,649,774 /
4,428,228 / 586,282. The canonical manifest has 915 regions, and canonical package
ownership is 125,327 source, 88,020 generated, and 4,213,061 opaque bytes.

The complete unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. The source leaf contains no filesystem
object or G2 block-device path. The broader library and hardware ports remain
outside this reuse, and qualification authorizes no signing, flashing,
filesystem format or erase, or hardware operation.

## Preceding bounded dual-image littlefs tag-chunk production reuse

The authenticated littlefs v2.10.1 source-equivalent snapshot now also
supplies the shared altered BSD-3-Clause
`components/shared/littlefs/runtime_littlefs_tag_chunk.c` adaptation. Its
exact upstream source authority is `lfs.c[10514:10607]`, 93 bytes, SHA-256
`406b74c2d10482c959cf1048d9589d00d8b416ee4661203bd339144baa74cd09`;
the independently pinned 32-bit tag typedef is `lfs.c[9602:9629]`, SHA-256
`cb4dcd6212b1a269371d86dddf98ed74853e2eb43753c5d8f8659abbca167ce2`.
This proves source-equivalent behavior, not Even Realities' exact historical
checkout.

Focused disassembly contributes only the identical six-byte stock spans,
four-caller topology in each image, scalar ABI, and entry-replacement
addresses. The six-byte source leaf is provider- and relocation-free. It is
registered atomically in Apollo main and the bootloader, where complete
`B.W`-plus-NOP patches replace `[0x004CAEA0,0x004CAEA6)` and
`[0x00410BA8,0x00410BAE)`.

Apple main/boot overlay/component pins are 124,566/3,647,962 and
628/149,228 bytes; the 4,426,422-byte package hashes to
`441bc7dd753518464afa0ac8ab84c26aedcd18228dbab3427d8c20ff66a8d914`.
Exact-root Linux uses 126,386/3,649,782 and 628/149,228 bytes; its
4,428,242-byte package hashes to
`8f62cf0ffb7d861ca1e6f9881e3221557f0da4640491489c7468129c5d57f1ba`.
Complete hashes are pinned in the overlay registries and canonical manifest.

The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. This bounded scalar reuse does not import
the broad library, a block-device port, or any format/erase path. All
qualification was offline; no image was signed or flashed and no hardware was
operated.

## Preceding bounded dual-image littlefs tag-size production reuse

At that milestone the atomic reuse boundary selected the bounded adaptation
`components/shared/littlefs/runtime_littlefs_tag_size.c` and its header for
both Apollo images. Its source authority is the exact 87-byte private
definition at authenticated littlefs v2.10.1 `lfs.c[10793:10880]`, SHA-256
`9df85bc43ca9f90ef58c425c5fd9bbbbf53585093be5fad0cc580fc88814ea5c`,
commit `0494ce7169f06a734a7bd7585f49a9fa91fa7318`. The exact behavior is the
pure unsigned mask `tag & 0x000003ff`; the source-equivalent selection is not
proof of Even Realities' historical checkout.

Focused disassembly contributes only the byte-identical stock spans
`[0x004CAEB8,0x004CAEBE)` and `[0x00410BC0,0x00410BC6)`, their complete
15/14 direct-caller topology, and the recovered 32-bit scalar ABI. Apple
production text is provider- and relocation-free. Final placements, redirects,
artifact identities, manifest ownership, and exact-root Linux parity are
closed in the explicit build-evidence ledgers; the settled tag-ID reuse is the
preceding production boundary.

The unchanged BSD-3-Clause terms remain at
`third_party/littlefs/LICENSE.md`. This promotion imports neither the broad
library nor a block-device, mount, format, program, or erase path, and it
authorizes no signing, flashing, reset, boot, or hardware operation.

## Preceding bounded nanopb `pb_read` production reuse

At this preceding milestone the authenticated nanopb compatibility snapshot
supplied a sixth bounded altered production adaptation,
`components/shared/nanopb/runtime_nanopb_read.c` and `.h`. Their 2,874/2,059
bytes hash to
`65f8f3cb92729e98f82f1254b18ba969cdd8a57c7ac74e8713137b5585102453`
and `aaa9847151722953498958687e91d55dc0b18cc9a60318b4f754110c66a443d6`.
The exact upstream 814-byte `pb_read` definition is byte-identical in
authenticated nanopb 0.4.7, 0.4.8, and selected compatibility baseline 0.4.9
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`; this does not establish
Even Realities' historical point release.

Focused disassembly supplies the complete stock span
`[0x0048F3BE,0x0048F454)`, its two internal recursive calls and 13 external
callers, the recovered 16-byte stream ABI, and complete ingress topology. The
stock entry redirected to the source-owned 158-byte leaf without changing
any caller address. No external branch or stored pointer enters the interior.
At that milestone three binary-owned dependencies remained explicit: the
private `buf_read` odd Thumb identity at `0x0048F3A5`, end-of-stream string at
`0x00787C70`, and I/O error string at `0x0078B690`. The subsequent private
read-pair and constructor promotions source-own the private helper bodies and
constructor while preserving that callback identity; only the two error
strings and copy helper remain explicit binary seams.

Apple places the leaf at `0x007B2A04`; exact-root Linux uses `0x007B3124`
after two alignment bytes. At that milestone the canonical manifest had 941
main and 67 boot regions, and packages hashed to
`f861d049873d497b44f25b265bad4a6ba9409aef3ff3abb4ed6abc1a031a4804`
at 4,426,688 bytes and
`0269400751d0ffa0f58c5cf8658b4dbc6e8af90a875d13bc2e5f684a436d26a9`
at 4,428,512 bytes. No bootloader homolog was authenticated. Qualification was
offline; no image was signed or flashed and no hardware was operated. The
preceding nine-function boundary follows immediately below.

## Preceding bounded nanopb stream-constructor reuse milestone

At that preceding milestone, the nanopb snapshot authorized nine bounded
production functions. The then-new
`pb_istream_from_buffer` adaptation used tag `nanopb-0.4.9`, commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, and the exact upstream
definition `pb_decode.c[5114:5692]` under Zlib. The source-equivalent
0.4.7--0.4.9 range did not identify the vendor checkout. Focused disassembly
supplied the complete 28-byte stock span, its 30 callers, the 16-byte stream
ABI, and callback identity `0x0048F3A5`. No bootloader homolog or broad nanopb
translation unit was included. Apple/Linux packages at that milestone were
4,426,806 / `062eaf5a7f301022f97162f4517d15248276e80c11a27b7c9f9b0e4cda4fbef2`
and
4,428,632 / `c9f09923a8c97706f32aed0c0c7db455a9aed01eff06d968cf8be81ee552793f`.
The constructor qualification is recorded in
`docs/research/nanopb-istream-from-buffer-source-audit.md`; no hardware
operation is authorized.

## Preceding bounded nanopb signed-varint reuse

At that preceding signed-varint milestone, nanopb's production allowlist
contained ten bounded altered functions.
The new `open_cfw_nanopb_decode_svarint` leaf selects the authenticated
nanopb 0.4.9 `pb_decode.c[42912:43210]` definition (298 bytes,
`df1caa71053163bdefaea7d6b19bdc72f10c63f09430003b88f10fb7dac3ff6e`)
as a compatibility baseline. Its only executable relocation targets the
already source-owned `open_cfw_nanopb_decode_varint`, so no opaque nanopb
provider remains in this leaf's dependency closure. The full 64-byte stock
span is generated ownership and the Apple manifest contains 951 regions.
This does not prove the vendor checkout; pristine nanopb translation units
remain unregistered. Exact-root Linux Clang 22.1.8 emits a 50-byte leaf at
`0x007B323C`, linked directly to the source-owned unsigned decoder, and pins
the overlay/component/package at 126,794 / 3,650,190 / 4,428,684 bytes.

## Preceding bounded nanopb varint32 reuse

At the preceding varint32 milestone the production allowlist contained twelve
independently audited altered functions; the current skip-string section below
brings it to thirteen. Private `pb_decode_varint32_eof` selects upstream bytes
`[5762,7483)` and public `pb_decode_varint32` selects `[7485,7617)` from the
authenticated 0.4.9 snapshot. One altered C/H pair supplies two separately
owned Apple text leaves and a private literal closure; no broad pristine
translation unit is registered. Version 0.4.9 is a compatibility baseline,
not proof of the vendor point release. No bootloader homolog was found.
Exact-root Linux independently pins the leaves at offsets 126,796 and 127,036
and the final overlay/component/package at 127,046 / 3,650,442 / 4,428,936.

## Preceding bounded nanopb skip-string reuse

The production allowlist at that milestone contained thirteen independently audited altered
functions. `pb_skip_string` selects the byte-identical authenticated
0.4.7--0.4.9 definition, replaces `[0x0048F64C,0x0048F66C)`, and calls only
source-owned varint32/read providers. Apple/Linux place identical 34-byte text
at `0x007B2C4C`/`0x007B336C` and close at
`125258/3648654/4427148` / `127082/3650478/4428972`. This is compatibility
reuse, not proof of the vendor checkout, bootloader reuse, or hardware
execution.

## Current bounded nanopb skip-field reuse

The production allowlist at this milestone contained fourteen independently audited altered
functions. `pb_skip_field` selects the authenticated 0.4.9 compatibility
definition at `pb_decode.c[9043:9458]`, replaces the complete
`[0x0048F6A0,0x0048F6EA)` stock dispatcher, and calls only source-owned
`pb_read`, `pb_skip_varint`, and `pb_skip_string`. Apple places 66 text bytes at
`0x007B2C70` and 18 diagnostic bytes at `0x007B2CB2`; the resulting
overlay/component/package close at `125344/3648740/4427234`. The Linux/Clang
22 profile is deliberately pending and fail-closed, not extrapolated from the
Apple build. This is compatibility reuse, not vendor-checkout or hardware proof.

## Current bounded nanopb raw-value reuse

The production allowlist at this milestone contained fifteen independently audited altered
functions. Private `read_raw_value` selects the authenticated 0.4.9
compatibility definition at `pb_decode.c[9612:10656]`, replaces the complete
`[0x0048F6EA,0x0048F77E)` stock function, and calls only source-owned
`pb_read`. Apple places 134 text bytes at `0x007B2CC4` and 34 diagnostic bytes
at `0x007B2D4A`; overlay/component/package close at
`125512/3648908/4427402`. The Linux/Clang 22 profile is deliberately pending
and fail-closed. The following `pb_make_string_substream` at
`[0x0048F77E,0x0048F7CA)` is now source-recreated with a four-field copy and no
compiler-runtime relocation. The current allowlist contains sixteen functions;
Apple closes at `125608/3649004/4427498`. See
`research/nanopb-raw-substream-boundary-audit.md`.

## Current bounded nanopb Boolean-pair reuse

The production allowlist now contains eighteen independently bounded altered
nanopb functions. Public `pb_decode_bool` selects authenticated
`pb_decode.c[42715:42911]` and private `pb_dec_bool` selects
`pb_decode.c[44696:44844]`, both at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The stock spans are
`[0x0049012C,0x00490150)` and `[0x004901CC,0x004901D6)`. Their executable
closure terminates entirely in source-owned `pb_decode_varint32` and
`pb_decode_bool`; retained upstream-source identity stays within the already
qualified 0.4.7--0.4.9 range and does not prove the vendor checkout.

Apple closes at overlay/component/package sizes
`125642/3649038/4427532`. Exact-root Linux Clang 22.1.8 remains pending and
fail-closed. See `research/nanopb-bool-cluster-source-audit.md`.

## Current bounded nanopb private field-varint reuse

The production allowlist now contains nineteen independently bounded altered
nanopb functions. Private `pb_dec_varint` selects authenticated
`pb_decode.c[44845:47571]` at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The complete 380-byte stock
span `[0x004901D6,0x00490352)` is replaced; its executable closure terminates
in source-owned `pb_decode_varint` and `pb_decode_svarint`, while both error
strings are source-owned. This remains compatible with pristine 0.4.7--0.4.9
and does not prove the vendor checkout.

Apple closes at overlay/component/package sizes
`125984/3649380/4427874`. Exact-root Linux Clang 22.1.8 remains pending and
fail-closed. See `research/nanopb-dec-varint-source-audit.md`.

## Current bounded nanopb private bytes-field reuse

The production allowlist now contains twenty independently bounded altered
nanopb functions. Private `pb_dec_bytes` selects authenticated
`pb_decode.c[47571:48677]` at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The complete 146-byte stock
span `[0x00490358,0x004903EA)` is replaced; its executable closure terminates
in source-owned `pb_decode_varint32` and `pb_read`, while all three diagnostic
strings are source-owned. This remains compatible with pristine 0.4.7--0.4.9
and does not prove the vendor checkout.

Apple closes at overlay/component/package sizes `126130/3649526/4428020`.
Exact-root Linux Clang 22.1.8 remains pending and fail-closed. See
`research/nanopb-dec-bytes-source-audit.md`.

## Current bounded nanopb private string-field reuse

The production allowlist now contains twenty-one independently bounded altered
nanopb functions. Private `pb_dec_string` selects authenticated
`pb_decode.c[48677:49908]` at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The complete 158-byte stock
span `[0x004903EA,0x00490488)` is replaced; its executable closure terminates
in source-owned `pb_decode_varint32` and `pb_read`, while all three diagnostic
strings are source-owned. This remains compatible with pristine 0.4.7--0.4.9
and does not prove the vendor checkout.

Apple closes at overlay/component/package sizes `126295/3649691/4428185`.
Exact-root Linux Clang 22.1.8 remains pending and fail-closed. See
`research/nanopb-dec-string-source-audit.md`.

## Current bounded nanopb private submessage reuse

The production allowlist now contains twenty-two independently bounded altered
nanopb functions. Private `pb_dec_submessage` selects authenticated
`pb_decode.c[49908:51557]` at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Its complete 172-byte stock
span `[0x0049048C,0x00490538)` is replaced. Source-owned substream helpers and
local diagnostic data close most of the leaf, while `pb_decode_inner` at
`0x0048FE98` remains a named stock executable seam and the indirect message
callback remains schema/application ABI.

Apple closes at overlay/component/package sizes `126459/3649855/4428349`.
Exact-root Linux Clang 22.1.8 remains pending. See
`research/nanopb-dec-submessage-source-audit.md`.

## Current bounded nanopb private decoder-loop reuse

The production allowlist now contains twenty-three independently bounded
altered nanopb functions. Private `pb_decode_inner` selects authenticated
`pb_decode.c[32121:37346]` at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Its complete 634-byte stock span
`[0x0048FE98,0x00490112)` is replaced by a 530-byte source leaf and 88-byte
diagnostic closure. The stock memory-fill call is eliminated and
`pb_skip_field` and `pb_decode_tag` are source-owned. Six fixed addresses
across five remaining helper families stay explicitly pinned; this is partial dependency closure,
not a pristine translation-unit claim.

Apple closes at overlay/component/package sizes `127122/3650518/4429012`.
Exact-root Linux Clang 22.1.8 and hardware execution remain pending. See
`research/nanopb-decode-inner-source-audit.md`.

## Current bounded nanopb tag-decoder reuse

The production allowlist now contains twenty-four independently bounded
altered nanopb functions. Public `pb_decode_tag` selects authenticated
`pb_decode.c[8663:9043]` at compatibility commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. Its complete 52-byte stock span
is replaced by a 42-byte source leaf closed over source-owned
`pb_decode_varint32_eof`. Stock byte stores prove the one-byte wire-type ABI;
there are no retained code or data seams.

Apple closes at overlay/component/package sizes `127122/3650518/4429012`.
Exact-root Linux Clang 22.1.8 and hardware execution remain pending. See
`research/nanopb-decode-tag-source-audit.md`.

## Current production nanopb defaults pair

Private `pb_message_set_to_defaults` is now authenticated at
`[0x0048FDF2,0x0048FE98)` against nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, source span
`pb_decode.c[31080:32048]`. Source/version identification, stock boundary,
caller topology, outgoing call mapping, recreation, Apple target compilation,
placement, and production integration are each 100% complete.

All stream, tag, iterator, and recursive-default edges are source-owned. The
sole remaining fixed helper is `decode_field @ 0x0048FBE4`. Overall nanopb
production is now thirty-five functions. See
`research/nanopb-message-defaults-source-audit.md` and
`research/reverse-engineering-acceleration-strategy.md`.

### Field-default member

Private `pb_field_set_to_default` is authenticated at
`[0x0048FCE2,0x0048FDF2)` against selected nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, source span
`pb_decode.c[28476:31080]` and SHA-256
`dced6e406d8c2c657a90cd599a60457a83bbc123b6ddfbfb9bff71778a773265`.
Its exact source bytes also occur at peeled release commits
`b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` (0.4.7),
`6cfe48d6f1593f8fa5c0f90437f5e6522587745e` (0.4.8), and
`cad3c18ef15a663e30e3e43e3a752b66378adec1` (0.4.9.1). This establishes
compatibility, not unique vendor provenance.

Boundary, callers, outgoing calls, release-range identity, semantics,
recreation, compilation, placement, and integration are 100% complete. Pairing
it with `pb_message_set_to_defaults` removes their three mutual call seams and
the released memory fill. Iterator helpers now bind to source and only
`decode_field` remains fixed. The pair moves package ownership to 129,428
source, 91,417 generated, and 4,209,725 opaque bytes. See
`research/nanopb-field-default-source-audit.md`.

## Current production nanopb iterator cluster

The complete retained `pb_common.c` iterator/default-callback cluster is
authenticated at `[0x004D916E,0x004D9522)`, 948 bytes across eleven functions.
Its selected definition is `pb_common.c[145:10196]` at nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`. The whole `pb_common.c` file is
byte-identical from official 0.4.4 through 0.4.9.1, so this component does not
narrow the vendor release.

The source is complete and target-compilable with no undefined symbol. Nine
isolated production leaves route all eight live iterator/callback entries; a
local loop removes the stock memory-fill call, while two callback dispatches
remain correctly classified as application/schema ABI. The integration closes
decoder/defaults iterator begin, begin-extension, next, find, and find-extension
seams. The three private stock bodies remain 536 opaque, unreachable bytes.
See `research/nanopb-iterator-cluster-source-audit.md`.

The global pristine nanopb candidate interval is corrected to
0.4.7--0.4.9.1. The 0.4.9.1 `pb_decode_ex` change is absent from retained G2
code, and the firmware build timestamp postdates that release. openCFW still
selects authenticated 0.4.9 deliberately; the exact vendor point release is
unresolved.

## Current production nanopb dispatch and extension trio

Private `decode_field`, `default_extension_decoder`, and `decode_extension`
bring the bounded altered nanopb allowlist to 38 functions. The selected
definitions at commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824` are:

| Function | `pb_decode.c` span | Definition SHA-256 | Identification |
|---|---:|---|---:|
| `decode_field` | `[26221,27053)` | `1c6111be8313e278c2b1753401a701245c1baa7c90acd085f18c1eb277d7e42d` | 100% |
| `default_extension_decoder` | `[27227,27659)` | `175e06435cc0c7e7f0bf3d44aa6b2d3e0f5f9bc8384ce52d28c80bf21777a691` | 100% |
| `decode_extension` | `[27810,28413)` | `3229a97ca148e192ca3b1d0fd33df3a1654b6405bd247e0b6f6320041460f7da` | 100% |

Direct official-source comparison found every definition byte-identical at
0.4.4, 0.4.5, 0.4.6, 0.4.7, 0.4.8, 0.4.9, and 0.4.9.1. These functions thus
do not narrow the global vendor point release. Their boundaries, callers,
diagnostic literals, upstream spans, host behavior, Apple objects,
relocations, placements, and stock redirects are each 100% complete. The
adjacent field-decoder implementations are production-integrated below;
dynamic application/schema callbacks are ABI, not missing firmware source.

## Current nanopb field-decoder production integration

The four functions at `[0x0048F7F4,0x0048FBE4)` are now 100% bounded and
upstream-identified, recreated, and Apple-production-integrated. Exact official-tag
definition comparison places the current `decode_static_field` source at
0.4.5 or newer and the current pointer/callback source at 0.4.6 or newer;
`decode_basic_field` is unchanged across 0.4.4--0.4.9.1. This does not improve
the stronger existing global nanopb interval, but it supplies compile-matrix
discriminators and guards against selecting older per-function source.

The production unit includes adjacent private
`pb_dec_fixed_length_bytes [0x0049053C,0x004905A8)`. All five definitions are
pinned to selected commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`;
the fixed-length definition is compatible from 0.4.6 through 0.4.9.1. The
production nanopb allowlist is now 43 functions. Boundary/call identity,
semantic recovery, dependency closure, source recreation, Apple placement,
and stock routing are each 100%. Linux/Clang 22 and hardware execution remain
deferred. See
`research/nanopb-field-decoder-cluster-boundary-audit.md`.

## Current IAR runtime memory-provider integration

The IAR family remains identified only probabilistically to EWARM 9.20+ with
9.60.2 the leading comparison candidate; no exact compiler or archive release
is claimed. Independently of that unresolved provenance, stock semantics and
caller ABI are fully recovered for memmove and both memcpy entries. The
clean-room relocation-free implementation passed 6,000 Lorelei Unicorn vectors
and matched stock's instruction-count shape within 5.2% across the qualified
1,024-byte cases.

Production now redirects all 316 callable stock bytes to 626 source bytes in
both reviewed toolchain profiles. The follow-on math/errno integration raises
confirmed IAR-runtime source recreation and production integration to ten of
ten code units (100%), including six of six for the new census tranche. The
remaining efficient upstream task is release-specific
comparison of `sqrtf`, errno helpers, and candidate `m7M_tl{v|s}.a`,
`rt7M_tl.a`, and `dl7M_tl{n|f}.a` archives.

## Current IAR runtime math/errno integration

Hard-float `sqrtf`, the EDOM/ERANGE setters, and the errno-address accessor
are now 100% bounded, ABI-recovered, source-recreated, and target-emulated.
Apple Clang 21 and Linux Clang 22.1.8 agree on the 28/20/20/10-byte section
pins. Lorelei matched 5,500 executions against stock, including NaNs,
infinities, signed zero, and randomized float/register states. Four guarded
stock redirects and independently replayed Apple/Linux placements now make all
ten bounded IAR code units source-recreated and production-integrated. No
bounded executable unit remains opaque; exact EWARM/archive provenance stays
at 20%.

## Cordio SMP-main hybrid source oracle

The G2 SMP-main module cannot be pinned to one pristine published file. Its
public base is Packetcraft r20.05--r20.05c `smp_main.c`, invariant at blob
`ba4889305cc903c7283972a12532a83c2a5b9cfe` and SHA-256
`c0d63cc679b63a0ad188a3a5b9ce36a5457812b077cc6a87d40bb189873d3810`.
Stock retains the r20 `keyReady`, `SmpDmLescEnabled`, and STK gate behavior.
It also retains AmbiqSuite 2.5.1's stale-AES queue drain, absent from public
r20. The repository therefore pins r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` plus the independently tracked
Apache-compatible cleanup patch.

The resulting 24,979-byte semantic candidate hashes to
`dd813e9b3bdf5d4ea6c879a78b7c7e542518a573ea70d18d9e144eb8909b6d74`.
Retained line constants prove small additional downstream textual drift, so
the classification is exact public/version behavior plus a proved vendor
patch, not byte-identical original source. Lorelei closes the hybrid's 32
providers under two compiler profiles; exact IAR flags and the G2 FreeRTOS
port remain unresolved.

## Cordio SMP Secure Connections main source oracle

Packetcraft r20.05 through r20.05c carries invariant `smp_sc_main.c` bytes:
Git blob `00515542371b1403f2716a02676064bf4aac2dcb`, 22,613 bytes, SHA-256
`cc2e97537c11f7eb0df9b713100ad0165c34e1e39d6c5b6846d9772f14b01c33`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. AmbiqSuite 2.x/r19 differs
semantically only in the event-string switch: it lacks the cleanup event that
stock retains at value `0x1F`.

Eighteen definitions link in stock and four are dead-stripped. All 2,626 code
bytes, three owned data gaps, 111 direct calls, and the absence of real stored
interior ingress are enforced by the module analyzer. This is exact public
definition/source-family evidence, not a whole-object compiler identity or a
production replacement claim.

## Cordio SMP Secure Connections state-machine source oracle

The selected initiator and responder files are Packetcraft r20.05c blobs
`68d20bee606c584a0ecd66a5dd1dbd41faf73a85` and
`09a208b4735cab37af65689bdf68288913f5e495`, at commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. Their SHA-256 identities are
`f9d52f683da225c0c37d1b454bc7ebff151e1b929e5b24887ee5a69e2b4af295`
and `ff8ef9e5ee14824558c0df42801ffccc31178080040e3f9dc79f2f3f83f85917`.
Both blobs are invariant through r20.05--r20.05c and explicitly Apache-2.0.

The initiator implementation is release-invariant apart from license
formatting. The responder is not: r20 adds `SMPR_SC_ACT_SEC_REQ_TO` and two
API-pair-request transitions. Stock matches that exact 55-action/table shape.
All four linked bodies and 1,495 scattered dispatch-data bytes are enforced;
this remains source-family evidence rather than exact IAR object equivalence.

## Cordio SMP common-action source oracle

Packetcraft r20.05 through r20.05c shares `smp_act.c` Git blob
`3c1ac36652243add46ba812e45e62555a5668ba3`, 27,952 bytes, SHA-256
`5149ca2e6feb98157b3a5fe7d2061c5eba1e09d3bc8f7d9ee666ec4478849f4f`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0.

All 25 definitions link in stock. The r20-only security-request-timeout action
and guarded `pScCcb->lescEnabled` trace condition exclude the r19/AmbiqSuite
2.x blob. The complete physical object, 25 body hashes, 78 calls, four role
action tables, two callback pairs, and 62 stored entry pointers are enforced
by the module analyzer. This is source-family evidence, not compiler-object or
production-replacement identity.

## Product BLE WSF-thread provider boundary

The G2-specific `platform\threads\thread_ble_wsf.c` TU is not upstream
Cordio or CMSIS source. Its complete 728-byte physical object is now bounded,
including twelve functions, the retained source path, and its literal pool.
Exact product source and historical provenance remain unresolved.

Its provider ABI is consistent with the already pinned CMSIS-FreeRTOS
v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`: `osThreadNew`,
`osThreadTerminate`, `osKernelGetTickCount`, `osDelay`, and the semaphore
create/acquire/release/get-count quartet. The task's forever loop enters the
separately authenticated Cordio `WsfOsDispatcher`. These pins qualify provider
interfaces only; they do not transfer upstream provenance or licensing to the
G2 task implementation.

## Product BLE message-thread provider boundary

The retained product files `thread_ble_msgtx.c` and `thread_ble_msgrx.c` are
not upstream Cordio or CMSIS source. Their exact physical objects are bounded
at `[0x00475290,0x00475FC0)` and `[0x0048EDB0,0x0048F3A4)`, respectively.
The original product source and historical generating commit remain
unresolved. TX already has a clean-room OpenCFW implementation; RX does not.

CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` is the selected provider oracle
for `osThreadNew`, termination, message queues, thread flags, and delay. It
authenticates only those ABIs. The product record formats, dispatch tables,
retained diagnostics, and lifecycle behavior come exclusively from the
official image. See `research/g2-thread-ble-message-recovery.md`.

## Cordio SMP responder-action source oracle

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share `smpr_act.c` Git blob
`086a013a445e9222a367fb3eb5383beead662af2`, 12,676 bytes, SHA-256
`9dde00f83bdadb7445935522fad83a86a48b75be220f877ab94a9a483736ba05`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0.

The r19/AmbiqSuite 2.x blob is
`54c5dbec582ea011a798f5b083f0a123afbffe21`, SHA-256
`da8f66711e27e5aa6b7438467ff8d368101429ffb2577eb3191bc37dcde0511a`.
Its only implementation delta is the missing `keyReady=TRUE` assignment.
Stock retains the corresponding `smpCcb_t+0x44` byte store, independently
selecting the r20/R4 family. All ten definitions link through both responder
action tables; this remains source-family evidence rather than compiler-object
or production-replacement identity.

## Cordio SMP initiator-action source oracle

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share `smpi_act.c` Git blob
`404a9e20dac01b1aa466b8758c6e46cb59d4af40`, 11,910 bytes, SHA-256
`c61194f9d62c5dd974056cd0d6d6e025243b3d10b75c6c08ac7f97ed749e5ac2`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0.

The r19/AmbiqSuite 2.x blob
`2db63fd5204268a8fccab6a733184f8b44e28146`, SHA-256
`71bf7da78f4d6768b9bc8434c197cea4251be16238a6890471c6ae8804ea7f91`,
lacks the sole implementation addition: `keyReady=TRUE` after adjusting the
initiator STK. Stock retains that `smpCcb_t+0x44` store. All ten definitions
link through both initiator tables; this is source-family evidence, not an
exact compiler-object or production-replacement claim.

## Cordio SMP Secure Connections role-action source oracles

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share `smpi_sc_act.c` Git blob
`38ed4197099e84e5dd17dac4a05385e42fe556fb`, 16,295 bytes, SHA-256
`195b7619013e746462ee1cb2cb4db7ccce3f68a1fe7dd15d0d05e1ca2567c952`,
and `smpr_sc_act.c` Git blob
`062799ba7c52aff19cb29d07eb0fbfc38ae1d1e4`, 18,585 bytes, SHA-256
`6c98c9eb132b19a6b7870ae35d7e31f0480d2566a83590f09984e205b10567d5`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; both files are Apache-2.0.

The r19/AmbiqSuite 2.x blobs are respectively
`ed53928ee9d86e94ef7985abb2c783aa3ee16069` and
`b8261ddbf130e4f5640e32e46688d0389460d6f7`. Each omits one later
`keyReady=TRUE` assignment in its terminal DH-key-check action. Stock retains
both `smpCcb_t+0x44` stores. All 36 definitions link, providing exact
source-family evidence without claiming compiler-object or production identity.

## Cordio SMP shared Secure Connections source oracle

The exact later definition-family oracle is the official AmbiqSuite R4.4.1
import of `smp_sc_act.c`: Git blob
`65d79f72b9e7536e554bb183c56f14bccc00b5af`, 33,145 bytes, SHA-256
`6e77a1429fe3bee3c0638c39d3784cfe7a9a789f3cf55be4b3e48a10ef360e34`.
It is explicitly Apache-2.0. Packetcraft r19/AmbiqSuite 2.x has identical
implementation definitions under the older license-header formatting.

Packetcraft r20.05 through r20.05c instead use blob
`f722964bb6beeaf91af2eee7897d0aa5578957b2`, 32,792 bytes, SHA-256
`ff78a86e44ac26b5a356153cdca9316c9228007d3400a42a5a78f40eff9ec270`.
Only `smpScProcPairing` differs: r20 removed the no-input/no-output MITM branch
that stock retains. The later R4 import is exact corroboration, not a resolved
historical producing commit; production ownership remains unchanged.

## Cordio SMP legacy state-machine source oracles

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share `smpi_sm.c` blob
`b5bc5ba1a6a91d49d6523f6fbbfd3c07d2070670`, 11,739 bytes, SHA-256
`70cc74bfbbe000ceedff41645b5d01208f9b0a083c22adb913b215065f3c61fa`,
and `smpr_sm.c` blob `a922f753e64b82bc92278671ded9f736b5a092e0`, 13,292
bytes, SHA-256
`a60f0611344bf550b6bc6152139a660b3c0177835e537d20da6d131567e6a771`.
Both are Apache-2.0; r20.05c commit `3656312d...` is the selected public pin.

The initiator implementation is invariant from r19. The responder r20 file
adds `smpActSecReqTimeout` plus timeout and cleanup rows in the API-pair-request
state; stock retains all three additions. The later R4 import corroborates the
exact source bytes but does not resolve G2's historical generating commit.

## Cordio non-SMP optional source oracle

Packetcraft r20.05 through r20.05c and the official later AmbiqSuite R4.4.1
import share optional `smp_non.c` blob
`b024dc746c712284f2cb0b54669358b3f3cbd0fd`, 3,325 bytes, SHA-256
`792892f2ca830fce8f1f0b280d098a9b188621fd5feb94a877a48b54779407b2`.
Packetcraft r19/AmbiqSuite 2.x uses blob
`46a0bc5820d9b6ee139ef905b4de510cf274b448`, 3,298 bytes, SHA-256
`2cad9c7bfefaf92a82e6e398e0aa2399c059ae72c1a04e89434c0eef0fa2b58c`.
The definitions are identical; only Apache-header formatting differs.

No stock body survives to discriminate those optional versions. The complete
r20/R4-compatible SMP implementation exclusively owns CID 6, so the
Packetcraft r20.05c file is retained only as the compatible Apache-2.0 source
oracle for the positively excluded alternative.

## Ambiq Cordio HCI event-port oracle

Stock's proprietary `sources/hci/ambiq/hci_evt.c` port contains 85 parser and
85 callback-size entries and 79 linked definitions. AmbiqSuite R2.5.1 file
blob `6b3416cd50862b8c11b898de321b69a08b27b85c`, 80,420 bytes, SHA-256
`3671305d64a49ffdef69de3e280a38a2ea0d12a17cd22eda4dfa76f1aff274eb`,
has only 67 table entries and is excluded.

The closest exact source-layout oracle is the later official AmbiqSuite
R4.4.1 import at neuralSPOT commit `4264b930...`: blob
`d2b2648587b2c8e89852f9d99555b35148e4d6ca`, 105,064 bytes, SHA-256
`5bee4484a94968be22cf59b60aa1d40441a824f26fe657edc58ca3e190037f24`.
Its 85-entry tables and diagnostic lines match stock. The file is proprietary
under the Arm Cordio SLA, so it is an analysis oracle only; no source bytes or
patch are imported. The later import does not resolve G2's historical
producing commit.

A separately authored GPL-3.0-only event decoder implements all 80 APIs from
public Bluetooth HCI wire semantics and the public callback ABI. It
production-routes all 79 linked bodies under exact route, relocation,
component, package, and flash-plan contracts; the proprietary oracle remains
metadata/behavior evidence only.

## Ambiq Cordio HCI core oracle

Stock links 22 of 24 definitions from the proprietary Ambiq HCI core family.
The R2.5.1 oracle (blob `8d8202f644ebfdfd9fa4d604d0196c1f97d7d9fc`,
28,330 bytes, SHA-256
`b3f5fb83b9fc7a50a305442bcf94715f674fbda3e94c722458f21ea2f5bd01bb`)
has only 19 definitions, a 32-bit LE-feature word, and no CIS surface, so it
is excluded.

The later official R4.4.1 import is blob
`1f81040608ca6f977d37a58aad5ab0b63229d607`, 35,068 bytes, SHA-256
`03ab8c9d340dd8cc9958779f6e336188cca2bbbc92ef39759dc165e84835e549`.
Its 24-definition 64-bit/CIS architecture is the selected reconstruction
oracle, but its neuralSPOT ACL-send delay is absent from stock. Later nsx
priority/trace behavior is absent too. This is a proprietary source-family
pin, not an exact-file, historical-commit, or reusable-source claim.

## Ambiq Cordio HCI platform-shim oracle

Packetcraft r20.05c public `ble-host/sources/hci/dual_chip/hci_core_ps.c`
is blob `0730013ce6d4bb992b6a48695e30bddae757c8ae`, 12,231 bytes,
SHA-256 `730395b8be404d357cf498fa1caee5630dcf95d66b2ea1c817e35932d5be0dd8`,
under Apache-2.0. It is the reusable behavior source for the production G2
adaptation; authenticated G2 offsets and local hardening are maintained
separately.

AmbiqSuite R2.5.1 `hci_core_ps.c` is blob
`6c289296e001369d09febef042d041cc298e2315`, 11,618 bytes, SHA-256
`c852f27f4cfc66cc01e9bb4676cb282e528778d658b4d88e9cff21e7fd247acb`.
Its 18-definition, 32-bit, non-ISO family is excluded by stock.

The later official R4.4.1 import is blob
`863085f75f368ac8ad2a8b741dd51231bffcabcf`, 12,960 bytes, SHA-256
`dca9e769828eedab03b15d99ffd0e1e726d8935af2e22eaa901bb897e05853cd`.
Stock's 64-bit feature getter and separate ISO callback/free branch select its
20-definition family. Nine definitions link and eleven getters are
source-only. The proprietary file remains an analysis oracle only.

## Ambiq Cordio HCI transport oracle

AmbiqSuite R2.5.1 `hci_tr.c` is blob
`acf4b4fdd1d30bdfbce53e142196c713fba5d0eb`, 8,452 bytes, SHA-256
`38c0851a30bfeb2ddb1f04ddf1d004c76eda013395c6ee36524ba52d99b288cb`.
Its `void` send routines complete or free successful buffers inside the
transport and are excluded by stock.

The later official R4.4.1 import is blob
`2fab7d10b369ff14d90339f75eda614a66239735`, 8,821 bytes, SHA-256
`81461dd10e01fac253df692f163f62e2174899e2e51f68c48f15b0cd07c9a6fd`.
Stock matches its return-valued send ownership and receive validation. Three
of four definitions link; `hciTrReceivingPacket` is source-only. The
proprietary file is an analysis oracle only, and its later import does not
resolve G2's historical producing commit. A separately authored clean-room
translation unit now implements all four definitions and production-routes the
three linked entries; it preserves the authenticated ABI while hardening
rejected receive state and copies no proprietary source or object bytes.

## Ambiq Cordio HCI command oracle

AmbiqSuite R2.5.1 `hci_cmd.c` is blob
`a71031443d0cf506c587f1d8340f3d7c52a91b1d`, 48,634 bytes, SHA-256
`ff9ddaab51fe02a20634eb3337a7360e0edadfdbe7bfdf04f112f593ee68ff3c`.
The Packetcraft r20.05c dual-chip ancestry is blob
`ac0ead555f1e5c158d5328aef4c61d569f6ce567`, 44,116 bytes, SHA-256
`9197085b206abcb0479fa6bf932c3ab314ecaf1777035550a06cb36e7b74896f`.
Neither has stock's exact complete command inventory.

The selected later official R4.4.1 import is blob
`106e76123c0f03f05f7ce3e4238d02b1ac98fd8f`, 51,777 bytes, SHA-256
`3a2d4609d803524f4765dbdfc65ec043035f2aa75526b0aa39f04873e62d5468`.
Its 72-definition ordering, queue-clear helper, radio-test surface, and
peer-SCA wrapper account for all 50 linked and 22 source-only definitions.
The file remains under the proprietary Arm Cordio SLA and is used only as a
clean-room metadata/behavior oracle; the later import does not resolve G2's
historical generating commit.

The production command layer is separately authored GPL-3.0-only C. All 50
linked functions are admitted under exact route, relocation, package, and
flash-plan contracts, and all 22 source-only APIs target-compile; the
proprietary oracle contributes behavior and ABI facts only.

## Ambiq Apollo3 HCI-driver oracles

AmbiqSuite R2.5.1 `hci_drv_apollo3.c` is blob
`02efb8c27f1138af998a53824c230d82bc611239`, 45,357 bytes, SHA-256
`55bf59929abdcb3c1c39903a6f5e3c4806443b245e404e1616475388244664b4`.
It is the historical blocking Apollo3 transport and radio-lifecycle baseline.
The later official R3.1.1 import is blob
`89cfb37c843f49d015adeada3619bc47aeed2a39`, 45,623 bytes, SHA-256
`246aaa2365ca175712209ddbb6b3544377934b41d347f878367a2363f8a4d0d2`;
its null-safe blocking handler matches stock more closely.

The vendor-command tail is newer still. The official R4.4.1 Cooper driver is
blob `e767f925b6cf3de4d250d6965b3fe1931a3c1025`, 36,534 bytes, SHA-256
`1f1461f0eeedc21277e9e9afb7dbdab2d7d89dbf101d1cc588e1ea220e06b7b0`.
It corroborates the stock RF-power, custom-BD-address, and NVDS-update command
semantics but is not an Apollo3 transport oracle. No source is a whole-file
match, so the selected classification is a mixed-version Ambiq driver with an
unresolved historical generating commit. All three carry Ambiq's
BSD-3-Clause-style notice.

The maintained clean-room driver implements all 16 APIs. Nine
hardware-independent entries are production-routed; six radio boot/shutdown,
handler, RF-test, and sleep operations stay stock-routed pending authorized
responsive G2/EM9305 validation. This is an explicit unavailable-physical-
evidence block, not a remaining C implementation gap.

## G2 BLE-startup oracles

The exact product authority is the official G2 OTA itself. It retains
`platform\ble\app_ble.c`, `_bleExactleStackInit`, and the complete product
initialization topology, but no matching product source file or generating
commit has been recovered.

AmbiqSuite R2.5.1 `ble_freertos_fit/src/radio_task.c` is 9,001 bytes, Git blob
`97aedb41ef5dd00e867a2409ced37dc6c38dc961`, SHA-256
`f5bf90bb48d888cb147efc3143675f565ebcb0c8fb469b0da9f49dddfa2f5d8d`.
It is a BSD-notice topology oracle for WSF, security, handler, radio, and
application startup—not a whole-file match. The vendored Apollo510 CMSIS
header, SHA-256
`b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797`,
identifies external IRQ 59 as `GPIO0_607F_IRQn`; it is used only for vector
identity.

## Ambiq HCI vendor reset-sequence oracles

AmbiqSuite R2.5.1 `hci_vs_apollo3.c` is blob
`d87b3476c0b0e3179476ea68e2b7fe6d1d2568d4`, 10,864 bytes, SHA-256
`241e49dcd92b7d68300388df290144a6cf6dcd70419354ee1ad8316054cfbd2a`,
under the proprietary Arm Cordio SLA. The later official R3.1.1 Apollo3
import is blob `b994f4e4c625835877d37efeaa1bdc49b770d29c`, 12,016 bytes,
SHA-256 `6559513745a91da000187be7cef780ebe99543de0a983849e9c6c69559ad56e4`;
it carries Ambiq's BSD-style notice and is the closest reset-start oracle.

The later official R4.4.1 Cooper file is blob
`3dcbbb4e64011229d13e7865978a8e79816f8603`, 12,493 bytes, SHA-256
`71b4914c5344bd6197c73ab3b124bfe25ef380d8afa15e9aa07bee79bae2ec78`.
It introduces an NVDS-first startup idea, but stock uniquely sends reset and
address update first, then chains NVDS, RF power, and event masks. It is a
semantic oracle for that later stage, not an exact file or historical pin.

## Cordio HCI PHY-command source oracle

AmbiqSuite R2.5.1 and Packetcraft r20.05c have identical bodies for all three
`hci_cmd_phy.c` definitions. The selected public file is Packetcraft blob
`e7bb445bb080a09bf3041f98dde3d355864eaf48`, 2,924 bytes, SHA-256
`e9ddb84511f1163614fd3e912f903160d7fa913158690e2aff13729c522c75c6`,
at commit `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. The file is Apache-2.0.

Stock links `HciLeSetPhyCmd`; the read and set-default wrappers are
source-only. This TU is source-exact but not independently release-
discriminating.

## Optional Ambiq Cordio HCI command oracles

The later official AmbiqSuite R4.4.1 import inventories six optional command
files: `hci_cmd_ae.c` (25 definitions), `hci_cmd_bis.c` (4),
`hci_cmd_cis.c` (5), `hci_cmd_cte.c` (8), `hci_cmd_iso.c` (10), and
`hci_cmd_past.c` (5). Their exact blob and SHA-256 identities are pinned in
`tools/manifests/ambiq-cordio-hci-optional-command-exclusion.tsv`.

All 57 definitions are source-only in stock. These proprietary files remain
metadata/behavior oracles only and provide no reusable or production source.

## Cordio ATT server-write source oracle

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import share `atts_write.c` Git blob
`1b41582c58124a49014317b987f304dd216ce100`, 14,245 bytes, SHA-256
`8c205dcd4162d5b3e30322bb13dbd552568a5aa62ecddabf7f0a69edad17d7b1`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0.

Four of five definitions link. Stock's EATT bearer slots, per-connection
prepared-write queues, and live method 9--12 roots exclude the smaller
r19/AmbiqSuite 2.x source. The physical object, 28 decoded outbound calls,
initialized method cells, and absence of accepted interior ingress are
enforced without claiming compiler-object or production-replacement identity.

## Cordio ATT core source oracle

Packetcraft r20.05 through r20.05c provides `att_main.c` Git blob
`e21a30766686e1657906412187b223d2c7a92f9d`, 19,467 bytes, SHA-256
`2706979a8ec7c310bcc41ce057e16aaa0ae7381086e0c0cb82fb60a423d74058`.
The later official AmbiqSuite R4.4.1 import is blob
`decbdafce60ebc2fe2b9e986ffd97207fceebcb2`, 19,463 bytes, SHA-256
`38c4287295d85efd7c153495a51248397496e71f60b26cf5f1364e9317797359`.
Their implementation text is identical; the only file delta is four license
header spaces. Both are Apache-2.0.

Stock links 21 of 23 definitions and exactly implements the r20
three-bearer/EATT architecture. The physical object, 65 direct callers, 14
stored entries, default interfaces, retained path, and initialized base UUID
are enforced without claiming compiler-object or historical-commit identity.
The r19/AmbiqSuite 2.x single-bearer source is excluded.

## Cordio ATT UUID constant-object source oracle

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import share `att_uuid.c` Git blob
`52cda51039c7665b66711cb45093395b0d55da34`, 15,852 bytes, SHA-256
`084b088781df6ef09647f6a4251406d92ec1b1aab6c6a61ef93a4982f5b756b7`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0.

Stock retains 11 of the 152 exported two-byte objects in one 22-byte
source-ordered block and strips the other 141. The whole-image scan closes 54
aligned stored references. Packetcraft r19/AmbiqSuite 2.x blob
`079c768f29f4cbe53951a3262e0d06200ce33134` already contains all 11 retained
objects, so the exact block identifies object semantics but does not by itself
resolve the release family or historical generating commit.

## Cordio optional enhanced ATT server source

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import share `atts_eatt.c` blob
`f1ca4879c8c32ef42127971399592329ca084680`, 16,713 bytes, SHA-256
`99d169c7e0066186fb6d1ebfe718f36c84a45eddf54b4a99091747deedc51355`.
The file is Apache-2.0. All twelve definitions are absent in stock, so this is
a compatible optional source rather than a stock body/version identity.

## Cordio optional enhanced ATT core/client sources

Packetcraft r20.05 through r20.05c provides Apache-2.0 `att_eatt.c` blob
`330d9efe93ef9c994dc996b54efcd3c3d6a2b135`, 26,769 bytes, SHA-256
`16cee15a33f157fc560a8983c057fd5e5186f686ee0d1a8424b0a364d36861d1`,
and `attc_eatt.c` blob `45305ddb59ed34713f02f9a2783b62eca25cfc04`,
26,255 bytes, SHA-256
`8f5e062300131697f705461eecdf57b1639e4b2168520dea5b8395e40e62f713`.
All 46 definitions are absent in stock.

The later official R4.4.1 import differs in one function per file: an
`AM_BLE_EATT` guard moves automatic channel establishment in the core, while
the client rewrites an equivalent null check. Their SHAs are respectively
`f0ba94715e834d7d7761091c495e24104a43aca6dbdd63775716d56d9a215e67`
and `c09d391bca06db1ba4129ee778848927576b4bb7adf33a118db4d80eafa53345`.
No linked body remains to distinguish these optional variants.

## Cordio optional dynamic ATT service source

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import share `atts_dyn.c` blob
`a125a644317eb973674637ea6fa0391c13999bf2`, 11,119 bytes, SHA-256
`fb310af2be69489884b104a35288f3539c2bb47dbc6ebe48d4070e3133cea9d3`.
All seven definitions are absent in stock. The r19/AmbiqSuite 2.x
implementation bodies are identical, so no release discriminator survives.

## Cordio optional ATT server-read source oracle

Packetcraft r20.05 through r20.05c provides the public lower-bound
`atts_read.c` blob `4e168d052592520878118944adc230e87393ad94`, 26,413
bytes, SHA-256
`371ad472a1b2b2a6d9be876107c590e74f97a113b1d9d40138d24cc2f2a8ca55`.
The linked CSF database-hash branch and r20 ATT server ABI exclude the legacy
r19/AmbiqSuite 2.x file.

The closest behavioral oracle is the official later AmbiqSuite R4.4.1 import,
blob `52a7f290710c12ecba0850175c9bc1fe21f8e0aa`, 26,859 bytes,
SHA-256
`b07b3b63a4c6f6bc0c7f1efa11c30f17cef39360c0619db7830f86647a74a425`.
It differs from r20 only by three subtraction-safe response-fit checks added
for IAR high optimization; stock pins their machine-code topology. All seven
definitions link. The later import is an Apache-2.0 reconstruction oracle,
not a resolved historical G2 generating commit.

## Cordio ATT server-signing source oracle

The stock-linked ABI is not the Packetcraft r20.05c public API. Packetcraft
r20.05--r20.05c `atts_sign.c` is invariant at Git blob
`5cadd92e4651311d5d4e12968adebd39d88773c0`, 12,536 bytes, SHA-256
`f85cbb896fc0e70f7de285e9eff3976d79f09156ea8ee5a28699fe1f59844762`,
but retains a two-argument `AttsSetCsrk` and 12-byte connection record.

The official later AmbiqSuite R4.4.1 import adds the authentication flag and
matches stock's three-argument API, `+0x0C` flag store, and 16-byte stride:
blob `c2f34343cd43e4633ec50f4899ab3e7af9bee820`, 13,134 bytes, SHA-256
`9a4b42b2e6cb0549eabfa4479a3a7516b8030c63f4497fcac227cb6a1bd7a81d`.
The file is Apache-2.0. This later import is the selected semantic/ABI oracle,
not a historical G2 commit pin or exact whole-file-text claim.

Four of eight source definitions link. The processing half is dead-stripped,
so source-family comparison applies to the state helper and three public APIs;
it does not imply that signed-write verification is enabled in stock.

## Cordio ATT server indication source oracle

Packetcraft r20.05 through r20.05c carries invariant `atts_ind.c` bytes: Git
blob `803f1fefb245314a8332d6fbc210306afd2ff3ec`, 21,163 bytes, SHA-256
`d79922dbfcc00e4b8b68c13c7bfc604f88b173fc431daba89c70c24331495567`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0. The
official later AmbiqSuite R4.4.1 import is byte-identical and is corroboration,
not the resolved historical G2 commit.

Thirteen of fifteen definitions link. Stock's EATT-aware per-bearer CCBs,
slot-aware callbacks, three-by-three timer initialization, and CSF
change-awareness flow exclude the legacy r19/AmbiqSuite 2.x file. The exact
public definition family, physical object, interface, PDU pointer, calls, and
absence of interior ingress are enforced without claiming compiler-object or
production-replacement identity.

## Cordio ATT server-owner source oracle

Packetcraft r20.05 through r20.05c provides the public EATT-aware
`atts_main.c` base at Git blob `998e6300d08ddcb18b2c91c17ca4b90da2b6e04b`,
28,310 bytes, SHA-256
`07f4aaad4f2ef9df3f0e6c9da6bc056e480ce4b60f0f0c787b3acf9791764698`.
Stock has the later `ATT_CHECK_DATA_LENGTH` hardening absent from that file.
The selected exact behavioral oracle is the official AmbiqSuite R4.4.1 import,
blob `bb99817115ce4da49ce26b5c52c4dd3418baaf88`, 28,588 bytes, SHA-256
`f28ba51cfb47d360508d5d8eac5187da34f84ac29180e712bcd1591f861eeff1`.
Both files are Apache-2.0; the later import is corroboration, not a historical
G2 generating-commit claim.

Seventeen of 21 source definitions link. The physical object, 45 callers,
four server callbacks, 18-method initialized-SRAM processor table, minimum-PDU
array, retained path, EATT control-block layout, and absence of accepted
interior ingress are enforced. This is exact source-family evidence rather
than compiler-object or production-replacement identity.

## Cordio common ATT server-processor source oracle

Packetcraft r20.05 through r20.05c and the later official AmbiqSuite R4.4.1
import share `atts_proc.c` Git blob
`455950e73bd19d0a6ee02e5bdfcd86149d0cb1cb`, 18,001 bytes, SHA-256
`b06af2dc72c57bb8742b5fbbf083dfdd2e5187768cb16db693e00463b8fcc502`.
The selected public pin is r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the file is Apache-2.0.

All nine definitions link. Stock's EATT MTU feature gate and live method-16
read-multiple-variable processor exclude r19/AmbiqSuite 2.x. The full physical
object, 26 callers, four decoded processor roots, retained path, and absence
of interior ingress are enforced without claiming compiler-object or
production-replacement identity.
## Current FreeRTOS/CMSIS message-queue closure

FreeRTOS-Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` is now the production source for
the remaining task/ISR message-queue dependencies: generic ISR send, queue
copy-to, priority disinherit, task receive, queue unlock, event-list placement,
and delayed-list placement. CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` supplies both public message-queue
operation wrappers. Together with the subsequent source-owned
`vTaskDelay`/`osDelay` pair and the subsequent
`vTaskPrioritySet`/`osThreadSetPriority` pair and the subsequent complete
thread-termination chain and the subsequent three-provider notification plus
two-wrapper thread-flags closure, followed by the source-owned `osThreadNew`
wrapper over authenticated retained creators, this raises linked CMSIS
ownership to 36/38 public APIs and 5/5 private helpers. The current
Apple/Linux packages are `4439150`/`4441028` bytes with SHA-256
`fcfed4ff1e555702d16ddef40bd155f6c11b8284c54f11ff352ebf25d98d2e8e` and
`3a621893611484516cf0a2bc35e117fc44064ace1d84747005dd5658ec5e44cd`.

## Current complete CMSIS-FreeRTOS production closure

The writer-coupled `osKernelInitialize` and `osKernelStart` pair completes the
linked wrapper object. All 38 public APIs and all five private helpers are now
source-owned from CMSIS-FreeRTOS v10.5.1 tag commit `d213f261`; the exact
`cmsis_os2.c` blob was first introduced by `13acfbef`. The lifecycle pair
shares `KernelState @ 0x20074384` with source-owned get-state, calls
source-owned IRQ/scheduler-state providers, and retains the independently
authenticated FreeRTOS V10.5.1 scheduler-start boundary. That retained core is
now also represented by a production-excluded dual-profile source candidate
with its idle hook, task creators, assertion, globals, and Apollo port explicit.
Current Apple/Linux
packages are `4439258`/`4441138` bytes with SHA-256
`16c879e54526237f7e2cad3200cc1f99cc535510b7d4ea7e67128a1af2b491d0` and
`a38542adb130ad8a9bbb2b4d1d693ff61d3b2a859ce009d135caadbbf8a906ef`.

The scheduler candidate proves static idle allocation at TCB `0x20071E30`,
stack `0x2005F154`, depth `0x400`, timer-task creation, the exact state-write
order, and the sole CMSIS caller. It does not change production ownership:
atomic scheduler-global binding and `xPortStartScheduler`/STIMER validation are
still required for production. Separate dual-profile candidates now close the
exact V10.5.1 `xPortStartScheduler` algorithm and the G2 STIMER setup. The
timer candidate authenticates IRQ 32, compare A, 32 counts/tick, 1,024 Hz, and
configuration `0x103` against AmbiqSuite 5.1.0 commit `5efc0228`. Separate
dual-profile candidates now also close the elapsed-tick/IRQ and tickless-idle
algorithms, including the stock missing-`+1` wrap behavior, PendSV aggregation,
abort/clamp/WFI policy, and capped tick stepping. No bounded STIMER algorithm
remains opaque; first-party power/overflow hooks, device validation, and
atomic production admission remain.

The subsequent production-excluded
`runtime_freertos_task_switch_context.c/.h` candidate closes the retained
generic scheduler-selection path from the same authenticated V10.5.1 commit.
Its stock `[0x004551B4,0x00455282)` body is 206 bytes with SHA-256
`fe979ce2eed1eeac9ca5c54192d428ef98825775f1665113ccbe0caf302c7343`.
The candidate preserves method-2 four-word stack checking, 56-list downward
selection, sentinel-skipping round robin, and the G2 64-entry external
switched-out/in trace ring. Apple/Linux target bodies are each 266 bytes and
have only the expected first-party overflow-hook and assertion-mask calls.
Production ownership is unchanged pending atomic scheduler admission and
device validation.

## Cordio copied GATT-profile source oracle

The retained product path `platform\ble\profiles\gatt\profile_gatt.c` is now
identified as Packetcraft Cordio's standard six-function
`ble-profiles/sources/profiles/gatt/gatt_main.c` object rather than opaque Even
logic. The exact source blob `bba9a3041ce14284a0bf527934eabd01c01694d8`
and header blob `6b71dd3178cbf89bbe3751d0ba33fb4a1603d97b` are identical across
official releases r20.05 through r20.05c. The selected source commit is the
existing newest-compatible Cordio baseline,
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; the private historical G2
generating commit remains unrecoverable.

All six stock functions / 322 body bytes / 356 physical bytes are
source-owned. Five are direct semantic matches. `GattDiscover` carries an
inserted EasyLogger expansion before its unchanged `AppDiscFindService` call.
The Apache-2.0 oracle, header, license, and offline verifier live under
`third_party/packetcraft-gatt-profile`; see
`docs/research/cordio-gatt-profile-source-recovery.md`.

## EvenHub common-text provider closure

The complete retained `app\gui\EvenHub\common_text_container.c` object is
now authenticated as thirteen functions / 6,966 body bytes / 7,740 physical
bytes. Three Ghidra-missed functions recover the constructor and index helper;
all four indirect calls resolve to one 192-byte first-party `evenhub_ui.c`
callback. Its reusable providers are the already selected EasyLogger commit
`a596b264…`, LVGL hybrid commit `344c7c318…`, bounded IAR DLIB, and the
production-routed TLSF-backed heap wrappers. It embeds no additional
third-party definition and exposes no new historical-commit discriminator.

The adjacent complete `app\gui\EvenHub\evenhub_ui.c` object is 26 functions /
14,296 body bytes / 15,568 physical bytes. Its dependencies terminate at the
same selected EasyLogger and LVGL commits, nanopb compatibility commit
`98bf4db6…`, LZ4 v1.10.0 commit `ebb370ca…`, bounded IAR DLIB, and the routed
TLSF-backed heap wrappers. Sixteen restored functions and three exact internal
callback targets reveal no additional third-party definition or historical-
commit discriminator.

The adjacent `evenhub_main.c` controller is now closed as five functions /
3,130 executable bytes / 3,450 physical bytes. Its generic utility edges reuse
EasyLogger `a596b264…`, LVGL `344c7c318…`, CMSIS-FreeRTOS `d213f261…`, nanopb
`98bf4db6…`, and TLSF `deff9ab5…`, plus bounded IAR/EABI and first-party
providers. It embeds no dependency implementation and yields no additional
version or private generating-commit discriminator.

The adjacent `translate.c` controller is closed as eleven functions / 2,504
body bytes / 2,862 physical bytes. Its utility graph reuses EasyLogger
`a596b264…`, LVGL `344c7c318…`, CMSIS-FreeRTOS `d213f261…`, and nanopb
`98bf4db6…`; no new family, version discriminator, or embedded implementation
appears.

The neighboring `teleprompt.c` controller is closed as ten functions / 2,408
body bytes / 3,900 physical bytes. Its utility graph reuses the same selected
EasyLogger, LVGL, CMSIS-FreeRTOS, and nanopb commits; no text-engine library,
new version discriminator, or embedded dependency appears.

`conversate_comm_data.c` is closed as twelve functions / 2,208 body bytes /
2,560 physical bytes. Its only reusable edges are EasyLogger `a596b264…`, LVGL
`344c7c318…` text-line measurement, and bounded IAR memory primitives; it
contains no serializer or new dependency/version evidence.

## G2 MX25U25643G driver provider closure

The complete `driver\flash\drv_mx25u25643g.c` object is forty functions /
6,726 executable bytes / 7,360 physical bytes. Its 31 MSPI/GPIO HAL calls reuse
the authenticated AmbiqSuite Apollo510 5.1.0-lineage commit `5efc0228…`; five
locking/completion calls reuse CMSIS-FreeRTOS v10.5.1 commit `d213f261…` over
FreeRTOS-Kernel `def7d2df…`. Three calls to the shared address `0x0048949C`
initialize transfer descriptors and do not establish nanopb behavior in the
driver. EasyLogger, IAR DLIB, and source-owned runtime/delay seams account for
every other direct edge. The object adds no new utility definition or exact
historical-commit discriminator; clean-room command-policy recreation and
device validation remain first-party/hardware work.

## G2 notification-list provider closure

The complete `app\gui\MessageNotify\ui_msg_notif_list.c` object is fifty
functions / 10,808 executable bytes / 11,686 physical bytes. Thirteen bodies
missed at the Ghidra shard boundary complete its UI construction, stored
callbacks, and string helpers. Its reusable edges terminate at LVGL
`344c7c318…`, CMSIS-FreeRTOS `d213f261…` over FreeRTOS-Kernel `def7d2df…`,
EasyLogger `a596b264…`, and production-owned TLSF wrappers over `deff9ab5…`.
Bounded IAR and first-party notification/time/resource helpers account for all
remaining calls. No third-party implementation or new version discriminator
is embedded.

## G2 dashboard main-screen provider closure

The complete misspelled stock `ui_DashBaord_Main_Screen.c` object is 31
functions / 9,040 executable bytes / 9,896 physical bytes. Its reusable edges
terminate at EasyLogger `a596b264…`, LVGL `344c7c318…`, and CMSIS-FreeRTOS
`d213f261…` over FreeRTOS-Kernel `def7d2df…`; IAR and 77 first-party
dashboard/widget targets account for the rest. Seven stored words are genuine
interior callback labels; six apparent odd pointers are unaligned words whose
targets are second halfwords of pinned 32-bit instructions. No reusable
implementation or new version discriminator remains hidden in the object.

## G2 teleprompt UI provider closure

The complete `teleprompt_ui.c` object is 55 functions / 12,228 executable
bytes / 13,120 physical bytes. Its reusable edges terminate at EasyLogger
`a596b264…` and LVGL `344c7c318…`; bounded IAR and first-party teleprompt,
file, presentation, resource, and display providers account for every other
direct call. One indirect call is bounded to the object's 4-by-19 mode/event
callback table. The 38 restored bodies reveal no third-party implementation or
new historical-commit discriminator.

## G2 EM9305 DFU-service vendor-negative closure

The complete `service_em9305_dfu.c` object is seven functions / 2,802
executable bytes / 2,826 physical bytes, but it has zero direct calls into the
Packetcraft/EM9305 vendor image. Its edges terminate at EasyLogger
`a596b264…`, source-owned littlefs/TLSF file and heap wrappers, bounded IAR,
the shared initializer admitted at nanopb compatibility commit `98bf4db6…`,
and two first-party DFU helpers. Consequently this object cannot identify an
EM9305 source version or producing commit; those claims remain confined to the
separate authenticated controller artifacts.

## G2 conversate tag-data serialization-negative closure

The complete `conversate_tag_data.c` object is twelve functions / 2,726
executable bytes / 2,876 physical bytes. It has zero nanopb and zero JSON calls:
the tag list is first-party allocation, insertion, deletion, lookup, and text
lifecycle code. Its only reusable edges terminate at EasyLogger `a596b264…`,
production TLSF wrappers over `deff9ab5…`, and bounded IAR DLIB. No serializer
version or producing commit can or needs to be inferred from this object.

The adjacent `framework\sync\sync_framework.c` object is now closed as 43
functions / 16,816 executable bytes / 18,180 physical bytes. Its provider
graph reuses CMSIS-FreeRTOS commit `d213f261…`, FreeRTOS-Kernel commit
`def7d2df…`, TinyFrame commit `eb75483e…`, AmbiqSuite commit `5efc0228…`,
nanopb commit `98bf4db6…`, and EasyLogger commit `a596b264…`. Twenty restored
listener/callback bodies contain no embedded third-party implementation and
add no historical-commit discriminator.

`framework\sync\sync_interface_api.c` is likewise closed as thirteen
functions / 6,136 body bytes / 6,432 physical bytes. Its third-party edges are
the same admitted EasyLogger and CMSIS-FreeRTOS v10.5.1 sources, the bounded
FreeRTOS assert port, IAR DLIB, and routed TLSF-backed heap wrappers. It embeds
no utility implementation and adds no version discriminator.

The remaining large sync object, `framework\sync\display_thread.c`, is closed
as 27 functions / 9,100 body bytes / 9,834 physical bytes. Its providers reuse
CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, LVGL `344c7c318…`,
and EasyLogger `a596b264…`; no third-party implementation is embedded. The
main display command loop and stored callback are already source-routed.

The remaining retained EvenHub parser, `evenhub_data_parser.c`, is now closed
as nineteen functions / 10,336 executable bytes / 10,874 physical bytes. Its
generic parsing edges terminate at nanopb compatibility commit `98bf4db6…`,
CMSIS-FreeRTOS v10.5.1 commit `d213f261…`, LVGL hybrid commit `344c7c318…`,
and the existing EasyLogger, IAR, and TLSF-backed provider seams. It has no
indirect call and embeds no third-party implementation or new historical-
commit discriminator.

## G2 dashboard watchface layout-3 provider closure

The complete `dashboard_watchface_layout3.c` object is nineteen functions /
3,254 executable bytes / 3,648 physical bytes. Its 173 external calls reuse
LVGL commit `344c7c318…`, EasyLogger commit `a596b264…`, and mpaland printf
commit `d3b98468…`; bounded IAR and first-party dashboard providers account for
the remainder. Five raw halfword patterns that resemble `BL` instructions are
the trailing halfwords of authenticated four-byte `sdiv` instructions. The
object embeds no additional utility implementation and supplies no new version
or private application-commit discriminator.

## G2 Ring-thread provider closure

The complete `thread_ring.c` object is seventeen functions / 2,374 executable
bytes / 2,632 physical bytes. Twelve recovered functions include the actual
CMSIS thread entry at `0x004C4CEC`, correcting the adjacent BLE Ring-profile
physical boundary from `0x004C4D64` to `0x004C4CEC`. Its reusable edges
terminate at EasyLogger `a596b264…`, CMSIS-FreeRTOS v10.5.1 `d213f261…` over
FreeRTOS-Kernel `def7d2df…`, production TLSF wrappers over `deff9ab5…`, and
bounded IAR/assert seams. Ring and delayed-event policy remains first-party;
no utility implementation or new historical-commit discriminator is embedded.

## G2 firmware event-loop provider closure

The complete `fw_event_loop.c` object is six functions / 1,806 executable
bytes / 2,012 physical bytes. Its reusable edges terminate at EasyLogger
`a596b264…`, CMSIS-FreeRTOS v10.5.1 `d213f261…`, and exact FreeRTOS critical
port entries from `def7d2df…`. One bounded callback is dequeued together with
its argument. All six stock functions are already routed to the clean-room
`event_loop.c` production source; no opaque utility or commit discriminator
remains in this provider.

## G2 Ring-connect-policy provider closure

The complete `ring_connect_policy.c` object is fifteen functions / 1,828
executable bytes / 2,056 physical bytes. Its 108 external calls terminate at
EasyLogger `a596b264…`, exact CMSIS-FreeRTOS v10.5.1 tick access from
`d213f261…`, or independently closed first-party event-loop, protobuf, and BLE
central facades. It reaches Cordio and nanopb only through those closed
facades, embeds no reusable implementation, and adds no version or private
application-commit discriminator.

## G2 SystemClose provider closure

The complete `systemClose.c` object is twenty functions / 4,960 executable
bytes / 5,368 physical bytes. Its reusable edges terminate at EasyLogger
`a596b264…`, LVGL-compatible commit `344c7c318…`, and a bounded IAR memory
runtime entry. It has no direct CMSIS-FreeRTOS or other opaque utility seam and
adds no version or private application-commit discriminator.

All twenty callable entries are now production-routed to independently
authored `system_close.c`: 4,960 replaced stock function bytes become 2,804
compiled Thumb text bytes plus 22 alignment bytes with 118 strict relocations.
The 408-byte official alignment/literal remainder stays stock-carried. The
software boundary is closed; live display, transition, IMU-reflash, and peer
behavior remains blocked by unavailable physical evidence; future qualification requires authorized physical evidence.

## G2 SystemAlert source ownership

The complete callable portion of `app/gui/SystemAlert/systemAlert.c` is now
production-routed to independently authored `system_alert.c`: seven functions,
2,174 replaced stock bytes, and 1,138 compiled Thumb text bytes plus 51 bytes
of read-only data and nine alignment bytes. Its reusable seams terminate at
the already bounded LVGL, event, timer, display, notification, and IMU
providers. The retained 172 official bytes are alignment and object-local
pool/data, not an opaque executable implementation.

## G2 FreeRTOS+CLI filesystem source ownership

The complete callable portion of
`app/freertos_cli/freertos_cli_filesystem.c` is now production-routed to
independently authored `freertos_cli_filesystem.c`: twelve functions, 3,200
replaced stock bytes, and 9,866 compiled Thumb text bytes plus 704 bytes of
read-only data and 20 alignment bytes. Its reusable storage edges terminate at
the already bounded littlefs provider; no matching upstream source-generating
commit was recovered. The retained 56 official bytes are object-local gaps and
alignment, not an opaque executable implementation. Live writable-media
validation remains blocked by unavailable physical evidence; future qualification requires authorized physical evidence.

## G2 factory NVDB lifecycle source ownership

The complete callable portion of `platform/service/flashDB/NV/service_nvdb.c`
is production-routed to independently authored C: five functions, 930 replaced
stock bytes, and 514 compiled Thumb bytes plus four alignment bytes. Its
reusable seams terminate at authenticated FlashDB 2.1.1 and the already
bounded database/serial providers. The 122 retained official bytes are an
object-local pool. Destructive reset is disabled pending golden-media and
authorized physical validation.

## G2 touch sensing and gesture source closure

The PSoC-specific MSC scan, gesture classifier, calibration threshold, and
ACT/ALR/WOT policy are independently authored from authenticated machine
behavior and retained strings. No upstream implementation identity is claimed.
All MSCLP operations are port callbacks; production admission remains blocked
on unavailable raw sensing, noise, timing, sleep, and wake evidence.

## G2 touch-controller I2C source closure

The proprietary shipped-prefix protocol is now independently reimplemented as
freestanding Cortex-M0+ C from authenticated machine behavior. It owns the
command, reply, report, persistence, attention, FIFO, power-policy, and DFU-
handoff boundaries. No upstream identity is claimed. Factory resident flash
at `>=0x8680` remains unavailable, so resident tables/HAL/boot/DFU code and
physical I2C behavior stay explicit blocks rather than inferred source.

## G2 charging-case UART/update source closure

The case-side proprietary protocol surface is now independently reimplemented
as freestanding Cortex-M0+ C from authenticated machine behavior. It does not
claim an upstream source identity. The source owns the frame and image sums,
bounded parser, update-offer/chunk decoding, retry loop, and callback-only
dual-bank state machine. Destructive production admission remains blocked by unavailable physical evidence; future qualification requires authorized case hardware and serial-window backup evidence.

## CmBacktrace fault-path source closure

The authenticated armink/CmBacktrace compatibility snapshot at commit
`73714489f9d8af130aacb515586b397b604a5768` now supplies all six target-
compiled APIs under the recovered G2 configuration. The project-owned
`runtime_cmbacktrace_fault_entry.c` replaces the snapshot's IAR-only entry
syntax with Cortex-M55-compatible naked C while preserving its `lr`/`sp`
calling contract. This is a compatibility-source selection, not proof of the
private vendor checkout. Physical fault injection remains unavailable, so the
source entry is not registered as the production HardFault vector.

## Packetcraft Cordio common HCI core

Packetcraft Cordio r20.05c commit
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` provides the Apache-2.0 behavior
source `ble-host/sources/hci/common/hci_core.c` (blob
`fe9a1f0cba1749c166e434d7cef90a167d1ed9c1`, 30,369 bytes, SHA-256
`6bfe1f1f37bf97bc86fa8f83345192bdbc813eff9ddac66108f91c2cf04c4b5e`).
The maintained G2 port adapts that behavior to the authenticated three-
connection, six-CIS, 64-bit-feature ABI. Ambiq proprietary copies are retained
only as version/ABI lineage metadata and contributed no copied source.

## G2 Cordio vendor reset-sequence ownership

The product-specific Apollo3/Cooper hybrid reset chain is now clean-room
source-owned. AmbiqSuite R3.1.1 Apollo3 and R4.4.1 Cooper BSD-notice files are
behavioral/version oracles only; the older R2.5.1 proprietary file is retained
solely as historical lineage evidence. No vendor implementation text is copied.
Four linked entries contribute 862 compiled bytes plus six alignment bytes;
all four unlinked hooks remain target-compilable.

## G2 bootloader MSPI device reconfiguration

`runtime_mspi_device_reconfigure_420e08.c` is first-party clean-room source
for `[0x00420E08,0x00420E8C)`. AmbiqSuite 5.1.0 supplies the BSD-3-Clause HAL
API identities for MSPI disable, device configuration, and enable; it does not
supply the product wrapper. The wrapper's status collapse, diagnostics,
published-state dereference, device-selector offset, and pin-group call are
authenticated G2 behavior. Physical qualification remains blocked.

## G2 bootloader MX25U25643G quad-mode selector

`runtime_mspi_set_quad_mode_420e8c.c` is first-party clean-room source for
`[0x00420E8C,0x00420F0C)`. AmbiqSuite 5.1.0 supplies the BSD-3-Clause API
identities for the retained MSPI control boundary; it does not supply this
product wrapper. The initialized-SRAM template clone, field overrides,
reconfiguration/XIP ordering, request `0x18`, mode byte, failure diagnostics,
and void completion are authenticated G2 behavior. Physical qualification
remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader row-six services and mode-family dispatcher

`runtime_row6_services_4220b2.c` is first-party clean-room source for the exact
row-six enable/disable and mode-family dispatcher bodies in
`[0x004220B2,0x004222D2)`. No external upstream implementation is incorporated;
the two 18-byte literal seams remain separately authenticated official data.
Low-byte bitmap indexing, selector client `0x35`, first-client handle creation,
configuration/start/finalize, ordered rollback, last-client stop/destroy and
kind-`4..6` dispatch are authenticated G2 product behavior. Physical
interrupt, retained-provider, timing, bitmap/state ownership and mode
qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader MX25U25643G serial-mode selector

`runtime_mspi_set_serial_mode_420f10.c` is first-party clean-room source for
`[0x00420F10,0x00420F6A)`. AmbiqSuite 5.1.0 supplies the BSD-3-Clause API
identity for the retained MSPI control boundary; it does not supply this
product wrapper. The initialized-SRAM serial configuration, reconfiguration
and XIP ordering, request `0x18`, zero mode byte, failure diagnostics, and void
completion are authenticated G2 behavior. Physical qualification remains
blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## AmbiqSuite Apollo510 command-queue public services

`components/bootloader/core_overlay/runtime_cmdq_services_427794.c` is a
reviewable BSD-3-Clause adaptation of the authenticated AmbiqSuite 5.1.0
Apollo510 command-queue implementation at upstream commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. It production-routes eleven
stock-compatible public entries at `[0x00427794,0x00427C80)` while preserving
the G2 state/register layout, caller ABI, updater boundary, SSRAM address
classification, and memory barrier. The exact imported license remains in
`third_party/ambiqsuite/LICENSE.txt`; physical command-queue and MSPI behavior
is blocked by unavailable physical evidence.

## AmbiqSuite Apollo510 queue family

`components/bootloader/core_overlay/runtime_queue_4275ea.c` is a bounded
BSD-3-Clause adaptation of `am_hal_queue.c` from AmbiqSuite commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. The authenticated upstream
source SHA-256 is
`2ca55e34d5b9d4843e32ce0ab24e312bde580716c708c7f017adcd0a12dbd1e4`;
the vendored 10,115-byte `am_hal_queue.h` SHA-256 is
`eabc8d95b06f06c24cc160ca85e20bd2fca32d1e7b0d9c8d815b7b3f9dffd2db`.
The complete initializer/add/get family is production-routed through
`0x004276BA`. Live interrupt and concurrency qualification remains blocked by
unavailable physical evidence.

`runtime_platform_bringup_430000.c` is first-party MIT clean-room source for the
exact 470-byte platform bring-up, measurement, and teardown orchestrator. No
external upstream implementation is incorporated. Both compilers, the sole
caller, 23 provider edges, sixteen literals, and portable lifecycle model are
pinned. Physical callbacks, calibration, registers, clocks, channels,
measurements, interrupts, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_dfu_payload_program_42dae8.c` is first-party MIT clean-room source for
the exact 424-byte chunked DFU payload programmer/verifier. No external upstream
implementation is incorporated. Both compilers, the sole caller, fourteen
provider edges, thirteen literals, and portable chunk/program/compare model are
pinned. Physical storage, destination programming, callbacks, coherency,
power-loss behavior, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_state_register_initialize_42d3bc.c` is first-party MIT clean-room
source for the exact 422-byte state-transition register initializer/restorer.
No external upstream implementation is incorporated. Both compilers, the sole
caller, delay edges, sixteen literals, Apollo-main analogue, and portable
register model are pinned. Physical MMIO, clock, power, trim, timing,
concurrency, reset, and cold-boot qualification is blocked by unavailable
physical evidence.

`runtime_spotmgr_state_transition_42b294.c` is first-party MIT clean-room
source for the exact 1,032-byte SPOT-manager state-transition, trim,
register-publication, wake, and finalization orchestrator at
`[0x0042B294,0x0042B69C)`. No external upstream implementation is incorporated.
Its compiler profiles, 12 provider edges, sole caller, 15 literals,
996/1,032-byte Apollo-main analogue, portable forward/reverse model, and
complete-image ownership are pinned. Physical SRAM, MMIO, trim, power, timing,
interrupt, concurrency, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_hw_state_decode_42b6b8.c` is first-party MIT clean-room source for
the exact relocation-free 770-byte hardware-state nibble composer and
dual-output classifier at `[0x0042B6B8,0x0042B9BA)`. No external upstream
implementation is incorporated. Its compiler profiles, sole caller, eight
literals, 738/770-byte Apollo-main analogue, 16,384-case portable differential,
and complete-image ownership are pinned. Physical flash, SRAM, MMIO,
peripheral, concurrency, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_hw_context_initialize_42e8d0.c` is first-party MIT clean-room source
for the exact 354-byte hardware-context and calibration-profile initializer. No
external upstream implementation is incorporated. Both compilers, the sole
caller, five provider edges, eleven literal cells, Apollo-main analogue, and
portable profile/default model are pinned. Physical SRAM, configuration, MMIO,
calibration, concurrency, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_dfu_image_crc_check_42d890.c` is first-party MIT clean-room source for
the exact 352-byte DFU image open/read/CRC/close verifier. No external upstream
implementation is incorporated. Both compilers, the sole caller, twelve
provider edges, eleven literal cells, and portable chunk/remainder behavior are
pinned. Physical filesystem/storage, buffer/configuration state, timing, reset,
and cold-boot qualification is blocked by unavailable physical evidence.

## G2 bootloader runtime control services

`runtime_control_services_42bf54.c` is first-party MIT clean-room source for
four exact fixed-address bodies totaling 296 bytes: readiness gating, event
wait-mask handling, aligned guarded dispatch, and register power control. No
external upstream implementation is incorporated. Both reviewed Clang
profiles, strict retained-provider edges, callers, the readiness stored
pointer, portable behavior, and complete-image ownership are pinned. Physical
MMIO, event/scheduler, interrupt-mask, timing, power, peripheral, reset, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

`runtime_control_orchestration_42dd14.c` is first-party MIT clean-room source
for 158 exact bytes covering event/control orchestration and a critical
four-word dispatch transaction. No external upstream implementation is
incorporated. Both compiler profiles, provider edges, stored/direct ingress,
portable behavior, and complete-image ownership are pinned. Physical
scheduler, event, retained-RAM, interrupt-mask, terminal-mode, logging, timing,
reset, and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

`runtime_context_publish_42dca2.c` is first-party MIT clean-room source for the
exact 114-byte queued runtime-context publisher. No external upstream
implementation is incorporated. Both compilers, provider edges, callers,
portable failure/success behavior, and complete-image ownership are pinned.
Physical retained-RAM, RTOS queue/event, scheduler, logging, timing, interrupt,
reset, and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

`runtime_hw_descriptor_publish_42c45a.c` is first-party MIT clean-room source
for the exact 108-byte ring-descriptor selector and register publisher at
`0x0042C45A`. No external upstream implementation is incorporated. Both
compilers, relocation-free body, caller topology, portable ring wrap and field
mapping, and complete-image ownership are pinned. Physical SRAM, MMIO,
peripheral, DMA, timing, interrupt, reset, and cold-boot qualification is
blocked by unavailable physical evidence; future qualification requires
authorized hardware evidence.

`runtime_hw_context_claim_42c4c6.c` is first-party MIT clean-room source for
the exact 114-byte hardware-context validation and ownership-claim service at
`0x0042C4C6`. No external upstream implementation is incorporated. Both
compilers, relocation-free body, call topology, 110-byte Apollo-main identity,
status codes, ownership flags, magic, stride, and complete-image ownership are
pinned. Physical retained-SRAM ownership, concurrency, peripheral lifecycle,
reset, and cold-boot qualification is blocked by unavailable physical
evidence; future qualification requires authorized hardware evidence.

`runtime_hw_context_enable_42c538.c` is first-party MIT clean-room source for
the exact 258-byte context activation and failure-rollback service. No external
upstream implementation is incorporated. Both compilers, three provider
edges, call topology, 246-byte Apollo-main identity, validation/idempotence,
command-queue setup, status wait, active flag, rollback mask, and complete-image
ownership are pinned. Physical retained-SRAM, MMIO, command-queue, timing,
concurrency, interrupt, reset, and cold-boot qualification is blocked by
unavailable physical evidence; future qualification requires authorized
hardware evidence.

`runtime_hw_event_service_42c6f8.c` is first-party MIT clean-room source for
the exact 648-byte hardware event, descriptor, callback, and command-queue
service. No external upstream implementation is incorporated. Both compilers,
nine provider edges, call topology, 621-byte Apollo-main identity, event/ring
state transitions, callback clearing, command-queue failure paths, terminal
register cleanup, and complete-image ownership are pinned. Physical
retained-SRAM, MMIO, DMA, callback, command-queue, interrupt, timing,
concurrency, reset, and cold-boot qualification is blocked by unavailable
physical evidence; future qualification requires authorized hardware evidence.

`runtime_hw_config_transaction_42c988.c` is first-party MIT clean-room source
for the exact 684-byte three-mode register snapshot/restore and resource
transaction. No external upstream implementation is incorporated. Both
compilers, seven provider edges, two callers, 657-byte Apollo-main identity,
thirteen-register mapping, validation/guard/status paths, queue state, resource
routes, and complete-image ownership are pinned. Physical MMIO, saved-state
validity, power/clock, command-queue, timing, concurrency, interrupt, reset,
and cold-boot qualification is blocked by unavailable physical evidence;
future qualification requires authorized hardware evidence.

`runtime_hw_instance_configure_42cc34.c` is first-party MIT clean-room source
for the exact 380-byte hardware-instance validation and mode-specific
configuration service. No external upstream implementation is incorporated.
Both compilers, the source-owned clock-encoder edge, sole caller, 352-byte
Apollo-main identity, handle/instance/active guards, dynamic and fixed-rate
paths, buffer/window calculations, slot clearing, and complete-image ownership
are pinned. Physical SRAM, MMIO, clock, DMA/buffer coherency, peripheral
timing, concurrency, interrupt, reset, and cold-boot qualification is blocked
by unavailable physical evidence; future qualification requires authorized
hardware evidence.

`runtime_hw_clock_encode_42c26a.c` is first-party MIT clean-room source for the
exact 376-byte clock-divider search, rounding, and register-field encoder. No
external upstream implementation is incorporated. Both compilers, three
source-owned arithmetic-helper edges, the sole caller, 370-byte Apollo-main
identity, shared constants, deterministic differential semantics, and
complete-image ownership are pinned. Physical clock, MMIO, peripheral
tolerance, signal integrity, timing, interrupt, reset, and cold-boot
qualification is blocked by unavailable physical evidence; future
qualification requires authorized hardware evidence.

`runtime_event_service_loop_42e2f8.c` is first-party MIT clean-room source for
the exact 162-byte retained-event initialization and wait loop at
`0x0042E2F8`. No external upstream implementation is incorporated. Both
reviewed compiler profiles, fourteen retained-provider edges, the sole stored
entry pointer, portable bounded-step behavior, and complete-image ownership are
pinned. Physical retained-RAM, scheduler/event, logging, timing, interrupt,
reset, and cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

`runtime_event_runtime_services_42e53c.c` is first-party MIT clean-room source
for 436 exact event-runtime bytes covering object/task initialization,
queue-driven callback dispatch, and callback enqueueing. No external upstream
implementation is incorporated. Both compilers, provider edges, callers,
portable lifecycle behavior, and complete-image ownership are pinned. Physical
RTOS-object, scheduler, queue, callback, logging, timing, interrupt, reset, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader Apollo510 SPOT-manager state-sequence selector

`runtime_spotmgr_state_transition_sequence_42a2b4.c` is BSD-3-Clause source
grounded in `mcu/apollo510/hal/am_hal_spotmgr_pcm2_2.c` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. It replaces the complete
390-byte selector at `[0x0042A2B4,0x0042A43A)` and retains the authenticated
28-byte transition table as typed vendor data. Physical power/temperature and
boot qualification is **blocked by unavailable physical evidence**.

## G2 bootloader overlap-safe byte move

`components/bootloader/core_overlay/runtime_memmove_4276bc.c` is first-party
clean-room MIT source for `[0x004276BC,0x00427752)`. No external upstream
source is incorporated. The unsigned overlap classification, backward and
forward byte loops, destination return ABI, production rotation caller, and
retained source-owned copy-provider edge are authenticated G2 behavior. The
Apple/Linux 50-byte leaves are relocation-free and byte-identical. Physical
memory-system, timing, caller-integration, and cold-boot qualification remains
blocked by unavailable physical evidence.

## AmbiqSuite Apollo510 command-queue index updater

`components/bootloader/core_overlay/runtime_cmdq_update_indices_427754.c` is
a bounded BSD-3-Clause adaptation of private `update_indices()` from
AmbiqSuite Apollo510 `mcu/apollo510/hal/mcu/am_hal_cmdq.c` at immutable commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. The authenticated 35,930-byte
source has SHA-256
`60aa2126ca01cd72f746a92d6f34a13e909fdab24ebfab6d6b0a70b026d8fa83`
and Git blob `0a286e565cad27cef801c389b5dedae826a2669a`; the vendored
10,496-byte header has SHA-256
`0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f`.
The complete private body `[0x00427754,0x00427794)` is production-routed.
Hardware index masking, monotonic epoch reconstruction, negative-wrap
correction, CQ-address snapshotting, and exact saved-PRIMASK restoration are
authenticated. Live register, interrupt/concurrency, wrap-timing, downstream
command-queue, and cold-boot qualification remains blocked by unavailable
physical evidence.

## G2 bootloader primary and secondary progress services

`runtime_hw_progress_423524.c` is first-party clean-room MIT
source for both authenticated transfer-progress bodies totaling 426 bytes at
`[0x00423524,0x004236CE)`. No external upstream source is incorporated.
Descriptor/FIFO selection, bounded progress, completion/exhaustion callbacks,
pump/snapshot behavior and interrupt-token restoration are authenticated G2
behavior. Physical FIFO/descriptor/interrupt/DMA/callback/concurrency/MMIO and
cold-boot qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive
hardware evidence.

## G2 bootloader per-instance register services

`runtime_hw_register_services_4236ce.c` is first-party clean-room
GPL-3.0-or-later source for three exact register-service bodies totaling 144
bytes around `[0x004236CE,0x00423764)`. No external upstream source is
incorporated. Type validation, bank selection, bitwise update, direct write,
and dual-register query behavior are authenticated G2 behavior. Physical
register/MMIO/concurrency/peripheral and cold-boot qualification remains
blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader per-instance service dispatcher

`runtime_hw_service_dispatch_42377c.c` is first-party clean-room
GPL-3.0-or-later source for the exact 176-byte dispatcher at
`[0x0042377C,0x0042382C)`. No external upstream source is incorporated. Active
and inactive flag routing, progress publication, callback dispatch and cleanup
are authenticated G2 behavior. Physical interrupt/register/callback/
concurrency/MMIO and cold-boot qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader hardware-control state mapper

`runtime_hw_control_state_423e14.c` is first-party clean-room
GPL-3.0-or-later source for the exact 44-byte body at
`[0x00423E14,0x00423E40)`. No external upstream source is incorporated.
State-one advancement, state-two override, default flag mapping, and context
mutation are closed offline; physical qualification is explicitly blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader MSPI FIFO, command-queue, and DMA-programming services

`runtime_mspi_fifo_write_423e40.c`, `runtime_mspi_fifo_read_423e8a.c`,
`runtime_mspi_cq_init_423f28.c`, `runtime_mspi_cq_term_423f54.c`, and
`runtime_mspi_cq_control_423f8e.c` are first-party clean-room
GPL-3.0-or-later source for six exact bodies totaling 376 bytes at
`[0x00423E40,0x00423FB8)`. Their software identity and ABI are independently
closed against the BSD-3-Clause AmbiqSuite 5.1.0 MSPI/CMDQ sources at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`; no upstream implementation text
is incorporated into the clean-room files. Retained status-check and CMDQ
providers remain explicit compatibility boundaries. Physical qualification is
blocked by unavailable physical evidence; future qualification requires authorized responsive G2 evidence.

`runtime_mspi_cq_pause_423fb8.c` and
`runtime_mspi_program_dma_42403e.c` are BSD-3-Clause source-equivalent adapters
for the corresponding AmbiqSuite 5.1.0 private helpers at the same pinned
commit. Their two exact bodies add 242 source-owned bytes at
`[0x00423FB8,0x004240AA)`. Dual-toolchain linked-byte checks, callers,
relocations, queue-index semantics, timeout behavior, and DMA-register order
are closed offline; physical clock, DMA/MMIO, concurrency, interrupt, and
cold-boot qualification is blocked by unavailable physical evidence; future qualification requires authorized evidence.

## G2 bootloader bounded memory-exchange helpers

`runtime_memory_exchange_423864.c` is first-party clean-room
GPL-3.0-or-later source for the exact two-buffer exchange and three-buffer
rotation bodies at `[0x00423864,0x00423928)`. No external upstream source is
incorporated. Direct-byte behavior, bounded 128-byte scratch chunking, and the
seven authenticated copy calls are closed offline; these helpers require no
physical-device qualification.

## G2 bootloader rotate-to-front helper

`runtime_memory_rotate_front_423928.c` is first-party clean-room
GPL-3.0-or-later source for the exact 74-byte helper at
`[0x00423928,0x00423972)`. No external upstream source is incorporated.
Bounded scratch chunking and the authenticated copy/overlap-safe-move bindings
are closed offline; this helper requires no physical-device qualification.

## G2 bootloader three-element comparator/exchange helper

`runtime_memory_sort3_423972.c` is first-party clean-room MIT
source for the exact 80-byte sorting network at `[0x00423972,0x004239C2)`.
No external upstream source is incorporated; all behavior is closed offline.

## G2 bootloader Floyd max-heap sift helper

`runtime_memory_heap_sift_4239c2.c` is first-party clean-room
GPL-3.0-or-later source for the exact 134-byte helper at
`[0x004239C2,0x00423A48)`. No external upstream source is incorporated;
exclusive-bound max-child descent and upward repair are closed offline.

## G2 bootloader introspective qsort runtime

`runtime_memory_qsort_423a48.c` is first-party clean-room MIT
source for the exact 704-byte core and 24-byte public wrapper at
`[0x00423A48,0x00423D20)`. No external upstream source is incorporated;
partition, recursion-budget, heap fallback, insertion, and public guard
behavior are closed offline.

## G2 bootloader global hardware-control services

`runtime_hw_control_services_423d20.c` is first-party clean-room
GPL-3.0-or-later source for six exact bodies totaling 228 bytes in
`[0x00423D20,0x00423E0C)`. No external upstream source is incorporated.
Register, timer, interrupt, debug, SRAM, and MMIO behavior is authenticated at
the software seam; physical qualification is explicitly blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader secondary configuration release

`runtime_hw_config_release_secondary_422fa2.c` is first-party clean-room source
for the exact 60-byte body at `[0x00422FA2,0x00422FDE)`. No external upstream
source is incorporated. Critical-section entry/restoration, state gating,
retained memset binding and exact secondary runtime reset span are
authenticated G2 behavior. Physical interrupt/concurrency/SRAM/MMIO/provider
and cold-boot qualification remains blocked by unavailable physical evidence; future qualification requires authorized
responsive hardware evidence.

## G2 bootloader per-instance hardware shutdown

`runtime_hw_shutdown_422fde.c` is first-party clean-room source for the exact
176-byte body at `[0x00422FDE,0x0042308E)`. No external upstream source is
incorporated. Four-bank register quiescence, delay policy, conditional
secondary clear, shutdown/release ordering and enable-mask restoration are
authenticated G2 behavior. Physical MMIO/clock/delay/concurrency/provider and
cold-boot qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive
hardware evidence.

## G2 bootloader per-instance FIFO services

`runtime_hw_fifo_4232c8.c` and `runtime_hw_fifo_drain_423342.c` are first-party
clean-room source for three exact bodies totaling 136 bytes at
`[0x004232C8,0x00423350)`. No external upstream source is incorporated.
`runtime_hw_fifo_adapters_423350.c` is first-party clean-room MIT
source for the two authenticated FIFO-adapter bodies at
`[0x00423350,0x004233E0)`. No external upstream source is incorporated.
`runtime_hw_mode_dispatch_4233e8.c` and `runtime_hw_mode_wait_423444.c` are
first-party clean-room MIT source for all five authenticated
executable bodies in `[0x004233E8,0x00423524)`. No external upstream source is
incorporated.
Four-bank polling, low-byte data movement, `0xF00` read-error mapping, count
publication and drain arguments are authenticated G2 behavior. Physical
FIFO/MMIO/concurrency/peripheral qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader secondary per-instance configuration latch

`runtime_hw_config_latch_secondary_422f4c.c` is first-party clean-room source
for the exact 86-byte body at `[0x00422F4C,0x00422FA2)`. No external upstream
source is incorporated. Critical-section entry/restoration, duplicate status,
secondary payload layout, latch publication and runtime-state clearing are
authenticated G2 behavior. Physical interrupt/concurrency/SRAM/MMIO and
cold-boot qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive
hardware evidence.

## G2 bootloader per-instance configuration-latch service

`runtime_hw_config_latch_422ee2.c` is first-party clean-room source for the
exact 106-byte body at `[0x00422EE2,0x00422F4C)`. No external upstream source
is incorporated. Critical-section entry/restoration, duplicate status,
configuration payload layout, latch publication and runtime-state clearing are
authenticated G2 behavior. Physical interrupt/concurrency/SRAM/MMIO and
cold-boot qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive
hardware evidence.

## G2 bootloader per-instance status mapper

`runtime_hw_status_map_422d7e.c` is first-party clean-room source for the exact
72-byte body at `[0x00422D7E,0x00422DC6)`. No external upstream source is
incorporated. Four-bank register-offset `0x3C` selection, argument/MMIO flag
combination, ordered bit mapping, retained status literals and fallback return
are authenticated G2 behavior. Physical MMIO/status/bank/timing qualification
remains blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader per-instance dual-descriptor initializer

`runtime_hw_descriptor_init_422dc6.c` is first-party clean-room source for the
exact 98-byte body at `[0x00422DC6,0x00422E28)`. No external upstream source
is incorporated. Header validation, two optional pair gates, publication flags,
two 24-byte descriptor layouts, retained-constructor calls and return statuses
are authenticated G2 behavior. Physical descriptor ownership, DMA/controller
timing, buffer lifetime and interrupt qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader per-instance clock-divider service

`runtime_hw_clock_divider_422e28.c` is first-party clean-room source for the
exact 186-byte body at `[0x00422E28,0x00422EE2)`. No external upstream source
is incorporated. Six reference-clock mappings, invalid/range statuses,
fixed-point divider derivation, per-instance register writes, achieved-rate
calculation and the source-owned divmod binding are authenticated G2 behavior.
Physical clock/MMIO/rate qualification remains blocked by unavailable physical evidence; future qualification requires authorized responsive hardware evidence.

## G2 bootloader instance register-transfer and lifecycle service

`runtime_hw_instance_service_422ba8.c` is first-party clean-room source for
the exact 376-byte body at `[0x00422BA8,0x00422D20)`. No external upstream
source is incorporated. Header/action validation, low-byte transfer policy,
four register banks, revision-gated clock bit, mode routing, teardown/resource
order and statuses are authenticated G2 behavior. Physical MMIO, clock, mode,
resource and lifecycle qualification remains blocked by unavailable physical evidence; future qualification requires authorized
hardware evidence.

## G2 bootloader per-instance register-clear leaves

`runtime_hw_register_clear_422d20.c` is first-party clean-room source for two
exact leaves totaling 90 bytes at `[0x00422D20,0x00422D7A)`. No external
upstream source is incorporated. The four-bank `0x1000` stride and exact masks
at register offsets `0x04`, `0x48`, and `0x50` are authenticated G2 behavior.
Physical MMIO/bank/peripheral qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader MX25U25643G guarded blocking read

`runtime_mspi_read_420f70.c` is first-party clean-room source for
`[0x00420F70,0x00420FF2)`. AmbiqSuite 5.1.0 supplies the BSD-3-Clause API and
descriptor identities for the retained blocking-transfer boundary; it does
not supply this product wrapper. The validation/status mapping, source-owned
guard/quad/wait ordering, ignored wait result, descriptor fields, timeout, and
raw HAL return are authenticated G2 behavior. Physical qualification remains
blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader LittleFS directory bootstrap

`runtime_fs_directories_4210c8.c` is first-party clean-room source for
`[0x004210C8,0x004211B0)`. It routes through the retained LittleFS directory
open, mkdir, and close wrappers at `0x00415288`, `0x0041527E`, and
`0x0041531C`, using the authenticated filesystem object and `/firmware`,
`/ota`, `/user`, and `/log` paths. The open/create/close status policy and
diagnostics are authenticated G2 behavior rather than upstream littlefs
implementation text. Physical mount, mutation, persistence, power-loss, and
cold-boot qualification remain blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

## G2 bootloader row-five client services

`runtime_row5_services_421eba.c` is first-party clean-room source for the exact
row-five client enable/disable pair at `[0x00421EBA,0x004220B2)`. No external
upstream implementation is incorporated. Low-byte bitmap indexing, timeout
refresh/publication, readiness, selector client `0x36`, first-client dual
switch/commit, rollback, last-client null-commit/release, critical ordering
and status mapping are authenticated G2 product behavior. Physical interrupt,
retained-provider, timing, bitmap/state ownership and mode qualification
remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

`runtime_memory_select_copy_4213e6.c` is first-party clean-room source for the
mapped-memory selector/copy service and odd-selector wrapper at
`[0x004213E6,0x0042156E)`. It incorporates no external upstream source. The
mapped-memory windows, control/security register gates, capacity matrix,
status mapping, and retained byte-copy provider are authenticated G2 product
behavior. Physical register/memory qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader mode routes, all-row cleanup, and configuration copy

`runtime_mode_routes_4222f0.c` is first-party clean-room source for the four
exact bodies in `[0x004222F0,0x00422430)`. No external upstream implementation
is incorporated. Seven-kind dispatch, client-bit validation, selective bitmap
cleanup, fixed destination `0x20007C00`, 20-byte copy length, and status mapping
are authenticated G2 product behavior. Both reviewed Cortex-M55 compilers
reproduce all 320 installed bytes. Physical bitmap ownership, routed service
effects, concurrent cleanup, configuration persistence, and cold-boot
qualification remain blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader Ambiq debug-domain services

`runtime_debug_services_422468.c` implements the three authenticated bodies in
`[0x00422468,0x00422574)` using the behavior of public AmbiqSuite SDK 5.1.0
`mcu/apollo510/hal/mcu/am_hal_debug.c` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` (11,141 bytes, SHA-256
`08e762d766432a883e1cdc2f1de2851614864f1a02d64cff45ae046538a2f61d`,
BSD-3-Clause). Debug-count shutdown, prior power-domain ownership,
`MCUCTRL->DBGCTRL` clearing, `DCB->DEMCR.TRCENA` release and the 10-microsecond
poll match the source and authenticated stock. Both reviewed compilers
reproduce all 268 installed bytes. Physical power/register/trace and timing
qualification remain blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader bitmap-client services

`runtime_bitmap_clients_421978.c` is first-party clean-room source for the
exact configuration/query publisher and four row-zero/row-one bitmap mutation
helpers at `[0x00421978,0x00421B08)`. No external upstream implementation is
incorporated. Controller selection and validation, row-six busy policy,
publication cells, low-byte selection, interrupt ordering, guarded row-one
activation, cleanup and status mapping are authenticated G2 product behavior.
Physical interrupt, controller/register, bitmap ownership and client behavior
qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader mode-one services

`runtime_mode1_services_421b08.c` is first-party clean-room source for the
exact mode-one enable, last-client disable and poll/state cleanup cluster at
`[0x00421B08,0x00421BD2)`. No external upstream implementation is
incorporated. Controller availability, control-word transformation, bitmap
row policy, critical ordering, active/state clearing and status mapping are
authenticated G2 product behavior. Physical interrupt, control/register,
bitmap ownership, polling and mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader mode-zero enable transaction

`runtime_mode0_enable_421bd2.c` is first-party clean-room source for the exact
controller-guarded row-two client enable transaction at
`[0x00421BD2,0x00421CCE)`. No external upstream implementation is
incorporated. Controller selection, low-byte bitmap indexing, timeout refresh,
state compatibility, critical-section ordering, control requests, active/state
publication, cleanup and status mapping are authenticated G2 product behavior.
Physical interrupt, controller/register, timing, bitmap/state ownership and
mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

## G2 bootloader mode-zero disable and cleanup

`runtime_mode0_disable_421cce.c` is first-party clean-room source for the
exact idempotent row-two client disable, last-client control/state clearing,
and active poll/completion cleanup pair at `[0x00421CCE,0x00421D5E)`. No
external upstream implementation is incorporated. Bitmap policy, low-byte
selection, critical-section ordering, control request, active/completion/state
cells, polling and status mapping are authenticated G2 product behavior.
Physical interrupt, controller/register, timing, bitmap/state ownership and
mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

## G2 bootloader row-four enable transaction

`runtime_row4_enable_421d5e.c` is first-party clean-room source for the exact
row-four client-enable transaction at `[0x00421D5E,0x00421E4A)`. No external
upstream implementation is incorporated. Low-byte bitmap indexing, timeout
refresh, readiness, first-client switch/configuration, rollback, critical
ordering, active/completion/state publication, cleanup and status mapping are
authenticated G2 product behavior. Physical interrupt, switch/apply, timing,
bitmap/state ownership and mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader row-four disable and cleanup

`runtime_row4_disable_421e4a.c` is first-party clean-room source for the exact
idempotent row-four client disable, last-client switch-off and active poll/
state cleanup pair at `[0x00421E4A,0x00421EBA)`. No external upstream
implementation is incorporated. Bitmap policy, low-byte selection, critical
ordering, active/state cells, polling and status mapping are authenticated G2
product behavior. Physical interrupt, switch, timing, bitmap/state ownership
and mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

`runtime_popcount_421584.c` is first-party clean-room source for the exact
32-bit population-count helper at `[0x00421584,0x004215AE)`. No external
upstream implementation is incorporated. The target instruction spelling is
an authenticated G2 compatibility constraint; the unsigned arithmetic
contract is independently tested on the host.

`runtime_bitmap_helpers_4215ae.c` is first-party clean-room source for the
exact nonempty, membership, and count helpers at
`[0x004215AE,0x00421632)`. No external upstream implementation is
incorporated. The table root at `0x20026E74`, low-byte selector behavior,
two-word row layout, bit-index narrowing, and popcount binding are authenticated
G2 product behavior. Their contracts are independently tested on the host;
physical table ownership and concurrency qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

`runtime_bitmap_update_421632.c` is first-party clean-room source for the
exact validated bitmap mutator at `[0x00421632,0x004216B2)`. No external
upstream implementation is incorporated. The table root at `0x20026E74`,
low-byte input narrowing, row/bit validation, status mapping, and set/clear
read-modify-write contract are authenticated G2 product behavior. Its contract
is independently tested on the host; physical ownership, concurrency, and
atomicity qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

`runtime_poll_delay_4216b2.c` is first-party clean-room source for the exact
bounded volatile flag/counter polling helper at
`[0x004216B2,0x004216D4)`. No external upstream implementation is
incorporated. The retained delay provider, duration 10, loop conditions and
decrement ordering are authenticated G2 product behavior. Its contract is
independently tested on the host; physical timing, memory visibility and
caller integration remain blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

`runtime_mode_service_4216d4.c` is first-party clean-room source for the exact
mode/configuration transaction at `[0x004216D4,0x004217D2)`. No external
upstream implementation is incorporated. The instance/controller seams,
default/query merge, bitmap-state policy, critical-section ordering,
apply/disable fallback, shared state and status mapping are authenticated G2
product behavior. Its transaction is independently tested on the host;
physical interrupt, register, timing and mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader LittleFS block-program callback

`runtime_littlefs_program_421310.c` is first-party clean-room source for
`[0x00421310,0x00421348)`. Its ABI and configuration binding are the upstream
littlefs v2.10.1 block-program callback contract; the fixed external-flash
partition mapping, source-owned MX25U25643G program call, diagnostic, and
device-status-to-`LFS_ERR_IO` collapse are authenticated G2 product behavior.
The leaf uses strictly authenticated reclaimed initializer body space because
the Apple append boundary is full. Physical MSPI/NOR programming, filesystem
writes, persistence, power-loss, diagnostics, and cold-boot qualification
remain blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader LittleFS block-erase callback

`runtime_littlefs_erase_421348.c` is first-party clean-room source for
`[0x00421348,0x00421372)`. Its ABI is the upstream littlefs v2.10.1 block-erase
callback contract; fixed partition mapping, source-owned MX25U25643G erase,
diagnostic, and status collapse are authenticated G2 behavior. The leaf uses a
second authenticated initializer-tail cave. Physical erase, filesystem
allocation, persistence, power-loss, diagnostics, and cold-boot qualification
remain blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader LittleFS sync and address-index helpers

`runtime_littlefs_sync_4213d4.c` is first-party clean-room source for the
constant-success LittleFS sync callback at `[0x004213D4,0x004213D8)`.
`runtime_address_map_4213d8.c` is first-party clean-room source for the
identity and thresholded address-index helpers at
`[0x004213D8,0x004213E6)`. Both address helpers are exact in-place compiler
reproductions; no external upstream implementation is incorporated.

## G2 bootloader LittleFS format/bootstrap orchestrator

`runtime_littlefs_format_4211b0.c` is first-party clean-room source for
`[0x004211B0,0x00421210)`. It routes through retained public littlefs v2.10.1
unmount, format, and mount wrappers over the authenticated filesystem and
configuration objects, then through the source-owned directory bootstrap.
Ignored unmount/format results, mount/directory failure mapping, diagnostics,
and status `9` are authenticated G2 product behavior rather than upstream
littlefs implementation text. Physical format/mount, flash mutation,
persistence, power-loss, and cold-boot qualification remain blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader LittleFS initializer and boot counter

`runtime_littlefs_init_421210.c` is first-party clean-room source for
`[0x00421210,0x004212D8)`. It routes through retained public littlefs v2.10.1
mount, format, file-open, file-read, file-rewind, file-write, and file-close
wrappers over authenticated objects, and through source-owned directory and
recovery services. Mount retry and status mapping, readiness publication,
`boot_count` persistence policy, ignored file-operation results, and
diagnostics are authenticated G2 product behavior rather than upstream
littlefs implementation text. Physical mount/format, flash mutation and
persistence, power-loss, readiness, boot-counter, and cold-boot qualification
remain blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader LittleFS block-read callback

`runtime_littlefs_read_4212d8.c` is first-party clean-room source for
`[0x004212D8,0x00421310)`. Its ABI and configuration binding are the upstream
littlefs v2.10.1 block-read callback contract; the fixed external-flash
partition mapping, source-owned guarded MSPI read call, exact diagnostic, and
device-status-to-`LFS_ERR_IO` collapse are authenticated G2 product behavior.
The Apple provider consumes the final 60 bytes before the protected main-image
boundary, so later callbacks need authenticated reclaimed-body placement.
Physical MSPI/NOR reads, filesystem content, concurrency, diagnostics, and
cold-boot qualification remain blocked by unavailable physical evidence; future qualification requires authorized hardware
evidence.

## G2 bootloader dual-mode transaction

`runtime_dual_mode_service_4217d2.c` is first-party clean-room source for the
exact dual-controller mode transaction at `[0x004217D2,0x00421978)`. No
external upstream implementation is incorporated. The accepted fixed
instances, local default, controller-query selection, bitmap-state policy,
critical-section ordering, mode enable/disable and commit seams, shared state,
cleanup and status mapping are authenticated G2 product behavior. Its
transaction is independently tested on the host; physical interrupt,
controller/register, timing and mode qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.
## G2 bootloader constraint dispatcher and memchr

`runtime_constraint_memchr_422590.c` is first-party clean-room source for the
two exact bodies in `[0x00422590,0x00422628)`. No external upstream source is
incorporated. The `memchr` body is independently byte-identical to the
Apollo-main IAR DLIB body at `0x004D40E0`; this is binary identity evidence,
not an imported implementation. Constraint handler selection, error `0x22`,
registration cell `0x20027190`, retained default handler, low-byte needle and
word-scanning behavior are authenticated G2 behavior. Physical handler,
memory-access and fault qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.
## G2 bootloader double runtime

`runtime_double_helpers_422628.c` is first-party clean-room source for thirteen
exact bodies in `[0x00422628,0x00422872)`. No external upstream source is
incorporated. Eleven bodies are byte-identical to authenticated Apollo-main
IAR DLIB counterparts; this is binary-identity evidence, not imported source.
Binary64 normalization, comparison flags, scaling, FPSCR preservation,
conversion and arithmetic behavior are authenticated G2 behavior. Physical
VFP flags, retained range-error effects and caller-ABI qualification remains
blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.
## G2 bootloader thread-pointer runtime leaf

`runtime_thread_pointer_422874.c` is first-party clean-room source for the
exact body/literal at `[0x00422874,0x0042287C)`. No external upstream source is
incorporated. The returned `0x20000518` SRAM anchor and sole caller are
authenticated G2 behavior. Physical anchor ownership and lifecycle
qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.
## G2 bootloader unsigned 64-bit divmod runtime

`runtime_u64_divmod_42287c.c` is first-party clean-room source for the exact
560-byte body at `[0x0042287C,0x00422AAC)`. No external upstream source is
incorporated. Digit fast paths, normalized division, quotient correction,
four-register quotient/remainder return and retained zero-divisor handling are
authenticated G2 behavior. Physical trap and caller-ABI qualification remains
blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.
## G2 bootloader atomic snapshot and retained-query wrappers

`runtime_atomic_wrappers_422aac.c` is first-party clean-room source for three
exact bodies totaling 38 bytes at `[0x00422AAC,0x00422AD2)`. No external
upstream source is incorporated. `PRIMASK` ordering, three volatile samples,
no-op behavior and the retained provider binding are authenticated G2
behavior. Physical interrupt/volatile/provider qualification remains blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.

## G2 bootloader four-instance hardware-service initializer

`runtime_hw_instance_init_422ad4.c` is first-party clean-room source for the
exact 212-byte body at `[0x00422AD4,0x00422BA8)`. No external upstream source
is incorporated. Index/output validation, compatible-handle rejection,
`0x11C` stride, `0x20024400` pool, header/index/state initialization and all
four status values are authenticated G2 behavior. Physical SRAM ownership,
concurrency, peripheral effects and cold-boot lifecycle qualification remains
blocked by unavailable physical evidence; future qualification requires authorized hardware evidence.
## Bootloader binary32 runtime admission

The G2 bootloader's `floorf`, `fmodf`, `roundf`, `ceilf`, four integer cores,
and range classifier at `[0x00427C90,0x00427E84)` are now production-routed
from freestanding MIT C. The remainder reduction is derived from musl v1.2.5
commit `0784374d561435f7c787a555aeab8ede699ed298`; the exact terms are retained
in `third_party/lvgl-ambiq-backend/g2-runtime/musl-math/COPYRIGHT.musl`.
The ABI veneers, rounding cores, and classifier are openCFW clean-room work.
Both pinned compiler profiles emit 432 in-place bytes, and 68 authenticated
suffix bytes remain separately typed as unreachable. See
`research/g2-bootloader-float-math-427c90-427e84-source-closure.md`.

## G2 bootloader Apollo510 SPOT-manager transition

`runtime_spotmgr_transition_428378.c` is BSD-3-Clause production source
grounded in Ambiq's public `mcu/apollo510/hal/am_hal_spotmgr_pcm2_2.c` at
commit `5efc0228528a8adce5eae0d226fac85d2551eb3b` (Git blob
`4d2ef939de853108e4cb18a55cb2e12be9e5c9a7`, SHA-256
`eac14263dc23ea211b917e9c3feb69695eb511d204961fdf301c1b0fa9abbeb7`).
The five-microsecond delay and terminal sequence 26 are authenticated G2
product behavior. Both reviewed profiles reproduce the 106-byte stock body at
`[0x00428378,0x004283E2)`. Physical timing, MMIO, voltage, trim, power, reset,
and cold-boot qualification is blocked by unavailable physical evidence.

## G2 bootloader Apollo510 SPOT-manager tranche

The BSD-3-Clause files `runtime_spotmgr_transition_7b_428a94.c`,
`runtime_spotmgr_timer_irq_service_42a04a.c`,
`runtime_spotmgr_buck_deepsleep_state_42a08c.c`,
`runtime_spotmgr_internal_power_domain_42a19c.c`, and
`runtime_spotmgr_power_ton_adjust_42a1bc.c` are grounded in Ambiq's public
`mcu/apollo510/hal/am_hal_spotmgr_pcm2_2.c` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` (Git blob
`4d2ef939de853108e4cb18a55cb2e12be9e5c9a7`, SHA-256
`eac14263dc23ea211b917e9c3feb69695eb511d204961fdf301c1b0fa9abbeb7`).
The MIT factory-trim loader/readiness files are clean-room openCFW work based
on authenticated G2 behavior. Together these seven entries add 950 exact
fixed-address source bytes through `0x0042A2A4`. Physical timer, interrupt,
MMIO, rail, trim, deep-sleep, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_hw_event_apply_42c0b2.c` is first-party MIT clean-room source for the
exact 368-byte retained hardware-event acknowledgement, drain, timed-pulse,
and terminal restoration service. No external upstream implementation is
incorporated. Both compilers, the delay-provider edge, two callers, shared
literals, 361-byte Apollo-main identity, portable state transitions, and
complete-image ownership are pinned. Physical retained-SRAM, MMIO, clock,
peripheral timing, concurrency, interrupt, reset, and cold-boot qualification
is blocked by unavailable physical evidence.

`runtime_platform_finish_430502.c`, `runtime_state_event_zero_42cfe0.c`, and
`runtime_register_profile_transfer_42f020.c` are first-party MIT clean-room
sources for 846 exact authenticated bytes. No external upstream implementation
is incorporated. Their reviewed compiler profiles, caller graphs, strict
provider edges, shared literals, Apollo-main analogues, and portable models are
pinned. Physical SRAM, MMIO, interrupt, clock, peripheral, reset, and cold-boot
qualification is blocked by unavailable physical evidence.

`runtime_event_value_profile_42f204.c` is first-party MIT clean-room source for
the exact 246-byte event-value hardware-profile publisher at
`[0x0042F204,0x0042F2FA)`. No external upstream implementation is
incorporated. Twelve state/register literals, five provider edges, the sole
caller, both compiler profiles, and a 234/246-byte Apollo-main analogue are
authenticated. Physical SRAM, MMIO, clock, power, timing, peripheral, reset,
and cold-boot qualification is blocked by unavailable physical evidence.

`runtime_mode_apply_42ff00.c` is first-party MIT clean-room source for the
exact 242-byte mode router and aggregate-bitset publisher at
`[0x0042FF00,0x0042FFF2)`. No external upstream implementation is
incorporated. The fixed service IDs, `0x200270D0` SRAM state anchor, sole caller,
eight provider edges, and both reviewed compiler profiles are authenticated G2
behavior. Physical SRAM ownership, interrupt/concurrency, peripheral effects,
reset, and cold-boot qualification is blocked by unavailable physical evidence.

`runtime_descriptor_register_430280.c` and
`runtime_hw_state_compose_42bdf0.c` are first-party MIT clean-room source for
666 exact authenticated bootloader bytes. No external upstream implementation
is incorporated. Their dual-toolchain bodies, bounded caller/stored-pointer
ingress, provider edges, shared literals, Apollo-main analogues, and portable
models are pinned. Physical SRAM, configuration storage, MMIO, callback,
interrupt, concurrency, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_dfu_service_task_42de58.c` is first-party MIT clean-room source for
the exact 684-byte DFU queue, image-dispatch, and guarded vector-handoff task
at `[0x0042DE58,0x0042E104)`. No external upstream implementation is
incorporated. Its two reviewed compiler profiles, 29 provider edges, sole
caller, 20 shared literals, portable model, and complete-image ownership are
pinned. Physical scheduler/queue, filesystem/storage, flash programming,
vector-table, interrupt, reset, and cold-boot qualification is blocked by
unavailable physical evidence.

`runtime_state_event_one_value_42d104.c` is first-party MIT clean-room source
for the exact 696-byte state-one register tuning and restoration service at
`[0x0042D104,0x0042D3BC)`. No external upstream implementation is incorporated.
Its two reviewed compiler profiles, three delay-provider edges, sole caller,
16 shared literals, 684/696-byte Apollo-main analogue, portable model, and
complete-image ownership are pinned. Physical SRAM, MMIO, clock, power, trim,
timing, interrupt, reset, and cold-boot qualification is blocked by unavailable
physical evidence.
