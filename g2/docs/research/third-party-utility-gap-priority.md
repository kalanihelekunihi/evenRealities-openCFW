# Third-party utility provenance and functional-gap priority

Status date: 2026-08-12
Target: official G2 `s200_v2.2.6.10`

## Conclusion

No Apollo-main third-party utility family remains unidentified. The remaining
uncertainty is narrower: historical checkout identity, Even/Ambiq patches,
compile-time configuration, hardware-facing ports, generated schemas/assets,
or production source admission. Those distinctions matter because an exact
upstream family or blob does not make every opaque byte safely replaceable.

The aggregate closure ledger now makes that distinction machine-readable for
all 26 dependency families and reports zero locally actionable bounded third-
party functional gaps. It composes the 130,000-byte retained-path lower bound,
Cordio reusable-path closure, the seven-function LVGL display-port closure,
FreeType lifecycle negative evidence, and the authenticated first-party
classification of the EUS/ESS/EFS/NUS Cordio adapters. See the
[dependency closure audit](third-party-dependency-closure-audit.md).

The newest family identification is the cJSON-class JSON parser shared by
`service_android_notify.c` and `service_whitelist.c`: DaveGamble cJSON,
version interval v1.7.9–v1.7.12, proven by four binary discriminators (the
≥1.7.9 issue-#315 `get_object_item` fix, the <1.7.13 `buffer_skip_whitespace`
offset behavior, the absent <1.7.14 `head->prev` tail store, and the <1.7.19
64-byte stack `parse_number` buffer). The family is bounded as 21 functions /
2,572 body bytes at `[0x004D798C,0x004D83D8)` with 34 external caller sites.
It is now admitted as an authenticated pristine MIT snapshot selecting the
interval-ceiling tag v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`) as
the reproducible OpenCFW baseline, with all 21 linked functions re-verified
byte-identical across the interval. The snapshot is **production-excluded** by
explicit decision, so its remaining gap is a compiler/ABI readiness matrix and
a production-overlay admission decision, not identity or function opacity. See
[`g2-json-parser-source-candidate-audit.md`](g2-json-parser-source-candidate-audit.md)
and [`third_party/cJSON/README.openCFW.md`](../../third_party/cJSON/README.openCFW.md).

The newest family correction is a copied Goodix diagnostic helper hidden under
the first-party path `utils\assert\util_error_check.c`. Its complete handler
and 43-row table select a byte-exact GR551x SDK 1.7.0 `app_error.c` snapshot;
2.0.1 is the first located incompatible 46-row/static-buffer form. The
earliest public carrier commit is selected only as a reproducible source
baseline because an official 1.7.0 release commit and Even checkout are not
public. This does not imply a linked Goodix BLE stack. See
[`g2-util-error-check-goodix-recovery.md`](g2-util-error-check-goodix-recovery.md).
Sweeping all 1,681 unique C/header blobs at the same SDK commit finds no other
new family: the remaining multi-string hits are an older Goodix
`cortex_backtrace.c` sharing already identified CmBacktrace ancestry and
nanopb 0.4.2 files excluded by stock's 0.4.7-era `pb_read` behavior.

The newest dependency admission is Nordic Semiconductor's `npmx` nPM1300 PMIC
library, previously hidden behind the first-party transplant wrapper. Two
adjacent public commits provide an unusually strong pin: stock includes the
ADC result-register rewrite from `e1aaec53…` and retains the double-promoted
logarithm implementation removed by its immediate successor `53de7af4…`.
The exact public candidate is therefore `e1aaec53…`, Git describe
`v1.0.1-1-ge1aaec5`. A byte-identical compact driver snapshot is admitted;
the remaining gap is hardware-facing G2 integration rather than library
identity or PMIC API opacity. See
[`g2-npmx-main-driver-recovery.md`](g2-npmx-main-driver-recovery.md).

The audio frontier exposed one additional linked family that retained-path
classification alone could not name: Google's Apache-2.0 `liblc3`. Stock calls
four public codec entries from `service_audio.c`. Its SNS `FLT_MAX` constant
and pre-`ltpf_bypass` encoder layout bound the public implementation from
`bb85f7d…` through `1de85e2…` and exclude successor `9f1e206…`. Official tag
v1.1.3 at `96a3af0…` is the selected reproducible baseline and its complete
38-file tree is admitted byte-for-byte. The linked binary cannot distinguish
v1.1.3 from the dead-stripped spelling-only successor, so no exact private or
public producing checkout is claimed. See
[`g2-liblc3-source-recovery.md`](g2-liblc3-source-recovery.md).

Closing the complete `service_audio.c` consumer confirms that admission. Its
five codec calls are the only direct liblc3 edges; the other 99 external calls
terminate at already admitted or closed providers. The one register-indirect
PCM dispatch is bounded to two authenticated first-party production-microphone
callbacks. No second audio library, embedded codec body, or further version
discriminator remains in the adapter. See
[`g2-service-audio-recovery.md`](g2-service-audio-recovery.md).

The largest remaining retained-path object was also checked as a dependency
consumer. `pt_protocol_procsr.c` expands to 73 complete functions and 1,526
external direct calls, including a hidden external handler and a bounded
66-entry command table. Its third-party seams are entirely the already selected
EasyLogger, CMSIS-FreeRTOS v10.5.1, FreeRTOS V10.5.1, mpaland printf, and
bounded IAR runtime. It embeds no reusable dependency body and supplies no
new commit discriminator, so the object is now first-party reconstruction work
rather than an opaque utility gap. See
[`g2-pt-protocol-procsr-dependency-boundary.md`](g2-pt-protocol-procsr-dependency-boundary.md).

The quicklist UI page likewise adds no utility gap. Its 80-function complete
object terminates at selected LVGL/EasyLogger, exact CMSIS-FreeRTOS tick
access, bounded IAR runtime, and first-party providers. See
[`g2-ui-quicklist-page-dependency-boundary.md`](g2-ui-quicklist-page-dependency-boundary.md).

The dashboard news page adds no utility gap either. Its 45-function complete
object closes over selected LVGL/EasyLogger, exact CMSIS-FreeRTOS mutex
wrappers, bounded IAR/EABI runtime, and first-party providers. See
[`g2-ui-widget-news-page-dependency-boundary.md`](g2-ui-widget-news-page-dependency-boundary.md).

The newest dependency-closure result is the GPU layer below LVGL. The exact
AmbiqSuite 5.1.0 Nema package matches public subtree `e690768a…` at
`b853fded…`; it identifies NemaGFX 1.4.12, NemaVG 1.1.8, the exact Apollo5
GCC archive, and the Ambiq GPU-patch archive/header. Stock independently
forces the NemaGFX 1.4.12 floor and fixes a 100 x 1,024-byte command list.
All 11 GPU-patch exports / 4,232 section bytes are now clean-room source
candidates qualified against exact ELF/DWARF, public layouts, exact-object
control flow/emulation, and, where surviving bodies exist, stock IAR code. This
includes all six recovered-LVGL dependencies and the four rendering paths in
the 1,036-byte bitmap-glyph routine. The remaining boundary is original-source
or binary admission plus hardware validation, not function opacity, family, or
public artifact identity.

The highest-value earlier result is TinyFrame. Ten retained `TF_Error` `__LINE__`
arguments select the exact upstream `TinyFrame.c` and `TinyFrame.h` blobs first
introduced by `eb75483e035916ef9f3e9fce0d2ae389cb09785f`. Repository head
`a29167a69f052975b0e0134a73b4d31d03afa8fa` retains those blobs and changes
only demo content, so the historical checkout cannot be narrowed below that
two-commit interval from linked firmware. Release 2.3.0 and the earlier
post-release core state `44ecc068` are excluded from the minimum-patch source
baseline. The full proof is in
[`tinyframe-send-version-recovery-audit.md`](tinyframe-send-version-recovery-audit.md).
The complete linked TinyFrame translation unit is also closed: 31 functions /
2,994 code bytes and a 124-byte non-executable literal pool account for all
3,118 bytes in `[0x004916C8,0x004922F6)`. Thirteen unused upstream API bodies
are explicitly dead-stripped, so no TinyFrame executable function remains
anonymous.

The next-ranked CMSIS-FreeRTOS gap is now similarly bounded. One contiguous
3,780-byte stock object at `[0x0044900E,0x00449ED2)` contains all 43 linked
functions: 38 public CMSIS APIs and five private helpers. Its 3,758 executable
bytes, 22 literal bytes, 831 external direct callers, 41 internal calls, and
sole stored callback entry are authenticated by the linked-function census.
Thirty-three other public APIs are explicitly dead-stripped. Live behavior
requires the change first introduced by `600ba38a` and lacks the later
`bb8a350a` thread-flags repair, while the selected release source is exact at
v10.5.1 commit `d213f261`; its `cmsis_os2.c` blob was introduced by
`13acfbef`. This closes binary ownership and a defensible source baseline,
although later source-identical/dead-code-only commits prevent proof of one
unique historical checkout.

## Verified dependency ledger

“Source pin” is the maintained or minimum-patch source openCFW should reuse.
It is not automatically a claim that Even used an unmodified checkout.

| Dependency | Origin and recovered version | Source pin or bounded state | Remaining functional/provenance gap |
|---|---|---|---|
| FreeRTOS-Kernel | Amazon/FreeRTOS V10.5.1 | `def7d2df2b0506d3d249334974f51e427c17a41c`; minimal G2 TCB patch `cf8c457153b75ad6a3163b9b6e6873e476e03537bb4534c9c8e4557de0eb4eb3`; `vTaskStartScheduler`, `xPortStartScheduler`, complete Apollo STIMER setup/IRQ/tickless algorithms, and the 13-function task-vote/application-hook object are bounded | Original private patch commit/name unobservable; atomic production binding, hardware timing/sleep validation, first-party hook admission, and trace seams |
| CMSIS-FreeRTOS | Arm CMSIS-FreeRTOS v10.5.1; CMSIS_5 5.9.0 | selected release `d213f261b5be6bb29a7cce8b84071706b72f4d53`; exact source blob first at `13acfbef7be85119fc6bc56832c455d4547d92c7`; CMSIS_5 `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`; all 43 linked functions and all 38 public plus five private production entries source-owned | Unique historical checkout remains binary-unobservable; no linked wrapper functional gap remains |
| CMSIS Core | Arm CMSIS Core selected header closure | `d23a6949a0331ca96853bcd98b0fdcc4db47184c` | None in selected closure |
| AmbiqSuite Apollo510 | AmbiqSuite 5.1.0 lineage; exact private pre-release checkout unavailable | public replay `5efc0228528a8adce5eae0d226fac85d2551eb3b`; stock `am_hal_sysctrl_sleep` has the 5.1.0 two-WFI internal-timer retry and excludes 5.0.0 commit `392042e3…`; watchdog restart is source-compatible across both; RTC utility/HAL identities are exact-source identified; the GX8002B host object adds 13 calls mapped to 12 exact `am_hal_i2s.c` APIs from file revision `release_sdk5p1p0-366b80e084` | Stock build predates the public 5.1.0 import, so the generating private commit remains unobservable; broader HAL admission and hardware validation |
| Nordic nPMX | NordicSemiconductor/npmx for nPM1300; `v1.0.1-1-ge1aaec5` | exact public candidate `e1aaec53f456887a7d7b80d82f684d1ac3cb08c8`; positive February ADC rewrite and negative adjacent April float-promotion fingerprint; 72 wrapper calls to 42 linked nPMX entries; complete driver snapshot admitted | Private Even checkout/cherry-pick remains unprovable; generated nPM1300 ADK/configuration, Apollo510 I2C and interrupt integration, G2 rail/charger/orientation policy, and hardware validation |
| Google liblc3 | Google/liblc3; selected tagged baseline v1.1.3 | `96a3af0beb5487aca3b98a4b992a539a1f6d80d1`; stock `FLT_MAX` and encoder-layout discriminators prove compatible interval `bb85f7d…1de85e2` and exclude `9f1e206`; four public entries/five direct calls and complete 38-file snapshot authenticated | Exact checkout is unobservable across linked-surface-identical public states; target build profile, floating-point/performance, G2 audio-buffer integration, and interoperability validation |
| AmbiqSuite ANCC profile | AmbiqSuite 2.2.0-4.5.0 implementation-equivalent; selected 2.5.1 | selected public import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; earliest authenticated same implementation `ca79fc6e…`; exact 17-definition source/header admitted; 12 source-derived and nine G2-local stock functions separated | Exact private generating release/commit is source-identical and binary-unobservable; G2 message/sync/whitelist extensions are first-party reconstruction, not a third-party gap |
| AmbiqSuite AMOTA profile | AmbiqSuite 2.2.0-2.5.1 stable application skeleton; selected 2.5.1 | selected public import `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`; exact 2.5.1 source/API oracle; stable CCC/A0/A1/handler architecture; four OTA functions skeleton-derived and three G2-local | Exact private release/commit is binary-unobservable; Even OTA actions are first-party reconstruction, not another upstream function gap |
| NemaGFX / NemaVG / Ambiq GPU patch | AmbiqSuite 5.1.0 revision `release_sdk5p1p0-634f7c117b`; NemaGFX 1.4.12 stock floor/exact candidate; NemaVG 1.1.8 exact co-package | exact public subtree `e690768a…` at `b853fded…`; Apollo5 archive first at `c6f54a95…`; GPU patch first at `e3eec7f3…`; all 11 exports / 4,232 section bytes source-qualified; complete 18-function / 614-byte stock bare-metal HAL behavior bounded, with public Zephyr ancestry first on-lineage at `4e7d4276…` | Original IAR archive and exact private HAL source commits, atomic integration, production admission, and hardware validation |
| FreeType | FreeType 2.9.1 | annotated tag `ad55868d889b6ba8d2aed846b4b4b460f8a83e42`, commit `86bc8a95056c97a810986434a3f268cbe67f2902`; ten-module table, v40-minimal TrueType, GX services, allocator seam, and exact `FT_Done_Face` closure pinned | Optional toggles, external font payloads, IAR link details, and production admission; whole-image absence proves no conventional linked `FT_Done_FreeType` entry can be recovered safely |
| littlefs | littlefs v2.10.1-equivalent | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | Exact Even checkout is not distinguishable; full port needs a golden external-flash capture |
| TLSF | mattconte/tlsf v3.1-compatible | compatible ceiling `deff9ab509341f264addbd3c8ada533678591905` | Exact historical checkout only; selected implementation is already source-owned |
| LZ4 | lz4 block decoder, stock compatible with v1.9.4/v1.10.0 | maintained v1.10.0 `ebb370ca83af193212df4dcbadcc5d87bc0de2f0` | Point-release discriminator is absent; optional unreachable-stock compaction |
| nanopb | nanopb 0.4.7–0.4.9.1 family | maintained 0.4.9 `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | Exact point release and first-party schemas/generated messages |
| FlashDB | armink/FlashDB 2.1.1 | `714d6159e7e6afb267a3953756abca445c350e61`; all 21 defaults, boot-counter lifecycle, and eleven G2 migrations bounded | Vendor-checkout proof, schema/non-destructive mount policy, golden-capture validation |
| EasyLogger | armink/EasyLogger 2.2.99 core | exact core blobs first at `cd93d9c768415f4b7279f2d3ef2366ce15ea087c`; selected identical snapshot `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; all downstream `elog_async_api.c` queue, consumer, and worker algorithms bounded and dual-profile qualified | Target concurrency/hardware stress, production admission, and image-specific transport ownership |
| FreeRTOS-Plus-CLI | classic V1.0.1–V1.0.4-compatible interpreter; selected V1.0.4 source | exact C/H pair at `43defa566cc440251dbd6b48d1fcca27f88cfcdd` through `1309654d…`, plus isolated G2 blank-input patch; all five linked interpreter functions and console/accessor seams are source-owned | Unique historical checkout is binary-unobservable; 76 descriptors/commands are first-party, and static-allocation policy is a future design choice rather than recoverable provenance |
| mpaland/printf | mpaland/printf formatter lineage | `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e`; all linked reverse-output, integer, float, exponential, string, variadic-core, and public-wrapper bodies are production source-owned, including recovered G2 `%PV`/`%pV` extensions | Exact historical vendor checkout only; no linked formatter functional gap remains |
| TinyFrame | MightyPork/TinyFrame post-2.3.0 | exact core blobs introduced by `eb75483e035916ef9f3e9fce0d2ae389cb09785f`; checkout interval through `a29167a69f052975b0e0134a73b4d31d03afa8fa`; all 31 linked functions mapped; one-instance role census, heap port, retained transport, no-op logging policy, and 14-function atomic production graph closed | Hardware golden packets; exact historical checkout inside the core-identical interval is binary-unobservable |
| CmBacktrace | armink/CmBacktrace post-1.4.1 line advertising 1.4.2 | compatible interval `4abadfa0…73714489`; selected `73714489f9d8af130aacb515586b397b604a5768` | Exact checkout and remaining port/config details |
| AndersKaloer/Ring-Buffer | dynamic-buffer upstream family | exact-compatible interval `cda00e1efb815bad5100757f0d10d117f633ced6…190e30bebcec22d7311fd941179d70b4f439c441`; selected ceiling | Historical checkout is binary-indistinguishable; source replacement is complete |
| LVGL | Hybrid LVGL 9.3-development vendor fork | official core interval `60d976c466e8…344c7c318047b7348e1be8572a9fd4260c251cfa`; exact Ambiq subtree tree `1e774257…`, canonical `5be8e0ae…`, replay `67fd93e2…`; handler ancestry `d4dcd26…`/`925470dd…`; all seven private display-port functions / 638 stock bytes are source-owned | Whole hybrid-tree and private display-port commits are binary-unobservable; assets, hardware validation, and first-party input/display integration remain; no third-party input-port artifact is linked |
| Packetcraft Cordio | Packetcraft BLE host with mixed Ambiq r20/R4-era ports | public r20.05–r20.05c interval ending at `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`; r19.02 `86372d84…` ancestry; later Ambiq R4.4.1 oracle `4264b930…`; exact R2.5.1 port-family archive `87b03680…`; 27/27 retained reusable paths and 68/68 focused module audits classified; copied `profile_gatt.c` is upstream while EUS/ESS/EFS/NUS are authenticated G2-local adapters | Exact mixed producing commit is unobservable; production admission/placement and hardware/controller validation; retained application/product paths are first-party boundary work |
| Goodix GR551x application-error utility | Copied/adapted SDK 1.7.0 `components/libraries/app_error/app_error.c` under G2 `utils/assert` | exact blob `d5027735dd01b0948a7315d9c595356fcb91f59b`; selected earliest carrier `854c43e0b96a24051ffce4c06ff629255aa56c59`; 43 exact rows, 512-byte stack buffer, 178-byte handler and 344-byte table closed | Official SDK 1.7.0 release commit and Even generating checkout unavailable; source behavior is closed and no Goodix BLE-stack linkage is inferred |
| IAR DLIB | IAR EWARM runtime, practical 9.20+ floor; 9.60.2 leading compatibility candidate | no defensible exact archive/commit pin; all 13 bounded units are exact clean-room source recreations, with the new `frexpf`/helper/`ldexpf` tranche canonical-Apple routed | Exact EWARM release, VFP and Normal/Full library variants, wider archive census, Linux Clang 22.1.8 profile recording, and hardware validation |
| DaveGamble cJSON | DaveGamble/cJSON, version interval v1.7.9–v1.7.12 | four binary discriminators: ≥1.7.9 issue-#315 `get_object_item` fix, <1.7.13 `buffer_skip_whitespace` offset behavior, absent <1.7.14 `head->prev` tail store, <1.7.19 64-byte stack `parse_number` buffer; 21 functions / 2,572 body bytes at `[0x004D798C,0x004D83D8)` with 34 external caller sites bounded | Authenticated pristine MIT snapshot admitted at interval-ceiling tag v1.7.12 (`3c8935676a97c7c97bf006db8312875b4f292f6c`); production-excluded by explicit decision: remaining gates are a compiler/ABI readiness matrix and a production-overlay admission decision, not identity work |

The EM9305 controller adds third-party/vendor binary dependencies outside the
Apollo utility set: QP/C v6.5.1 is pinned to
`416dcec8820b9cdb5827497e645d0d9375db53c6`; EM SDK v4.2 archive artifacts
identify PML, sleep manager/timer, protocol timer, unitimer, EM HAL/radio, and
a Bluetooth-5.4 Packetcraft/EM Bleu controller. Those archives provide exact
binary provenance but not redistribution-safe source. Their residual work is
tracked separately because it is controller reconstruction, not an Apollo
utility-version gap.

The latest first-party frontier sweep also closes
`app\gui\logger\logger_setting.c`. Its `/log` scan/delete and protobuf routing
logic calls the same already admitted EasyLogger, nanopb, littlefs-backed file,
FreeRTOS, and IAR DLIB providers listed above. The recovered eight-function
object embeds zero upstream definitions and supplies no new exact-version
evidence, so it does not reopen the third-party utility queue. See
[`g2-logger-setting-recovery.md`](g2-logger-setting-recovery.md).

The adjacent `app\ux\ux_system\ux_system.c` closure likewise does not reopen
the utility queue. Its eleven-function status-sync object contains only
first-party OTA/BLE/ring policy; the sole third-party seam is the already
admitted EasyLogger diagnostic core at selected commit `a596b264…`. It adds
no family, opaque definition, or version discriminator. See
[`g2-ux-system-recovery.md`](g2-ux-system-recovery.md).

The subsequent `app\gui\health\health.c` closure independently confirms the
CMSIS-FreeRTOS seam: its only RTOS operations are source-owned `osMutexNew`,
`osMutexAcquire`, and `osMutexRelease` from exact v10.5.1 commit `d213f261…`.
EasyLogger and nanopb ancestry terminate at admitted providers. No hidden
utility body or additional commit discriminator is present. See
[`g2-health-recovery.md`](g2-health-recovery.md).

The paired `app\gui\quicklist\quicklist.c` closure reaches the same exact
CMSIS-FreeRTOS v10.5.1 mutex wrappers and admitted EasyLogger/nanopb seams.
Its stored event handler is local UI policy, not a hidden utility body. See
[`g2-quicklist-recovery.md`](g2-quicklist-recovery.md).

The dashboard watchface-manager closure adds an indirect-provider check: 30
direct utility edges reach the admitted EasyLogger commit, while all 15
register-indirect calls are constrained by four byte-pinned first-party
operation tables. The object contains no CMSIS-FreeRTOS call, hidden utility
body, new dependency family, or new version discriminator. See
[`g2-dashboard-watchface-manager-recovery.md`](g2-dashboard-watchface-manager-recovery.md).

The EvenAI text-stream service supplies a broader composition check. Its 39
CMSIS-FreeRTOS, 17 LVGL, 10 EasyLogger, nine TLSF-wrapper, five nanopb, and 22
IAR DLIB calls all terminate at existing admissions. The recovered UTF-8 timer
callback, seven caller-callback dispatches, and four animation presets are
first-party policy. No hidden upstream body or narrower commit discriminator
appears. See
[`g2-text-stream-service-recovery.md`](g2-text-stream-service-recovery.md).

The terminal-core closure likewise exposes no new utility gap. Thirty calls
reach admitted EasyLogger, three reach exact CMSIS-FreeRTOS v10.5.1 mutex
wrappers, and three reach bounded IAR memory primitives; all 29 remaining
calls are first-party role, protobuf-service, UI, or command routing. See
[`g2-terminal-core-recovery.md`](g2-terminal-core-recovery.md).

The RTC-driver closure identifies both remaining functional providers by
source: AmbiqSuite `am_util_time_computeDayofWeek` and Apollo510
`am_hal_rtc_time_set`, selected at 5.1.0 replay `5efc022…`. Their exact public
5.0.0 and 5.1.0 blobs are pinned, and the combined wrapper behavior is already
production source-routed. This closes an Ambiq utility/HAL attribution gap but
adds no local version discriminator because the executable code is unchanged
between those two releases. See
[`g2-drv-rtc-recovery.md`](g2-drv-rtc-recovery.md).

The teleprompt file-list closure adds no utility gap. Its exact three-function
object uses ten admitted EasyLogger calls and one bounded IAR `memcpy` plus one
`memset`; the private file-list schema is only stored here and is decoded by a
separate first-party caller. See
[`g2-teleprompt-file-list-recovery.md`](g2-teleprompt-file-list-recovery.md).

The EvenAI timer closure confirms that no hidden RTOS timer implementation is
present. The 13-function object keeps two 12-byte first-party deadline records
and reads time through four exact CMSIS-FreeRTOS v10.5.1
`osKernelGetTickCount` calls. Thirty diagnostics and one three-byte clear stop
at admitted EasyLogger and bounded IAR DLIB; all scheduling and timeout actions
are first-party. See
[`g2-even-ai-timer-recovery.md`](g2-even-ai-timer-recovery.md).

The BLE-status callback facade contains no new utility seam. Its only upstream
calls are ten admitted EasyLogger diagnostics; register, unregister, and
notify terminate at three first-party `callback_manager.c` providers. See
[`g2-cb-ble-status-recovery.md`](g2-cb-ble-status-recovery.md).

The Conversate menu-page closure composes only admitted EasyLogger and LVGL
9.3-compatible primitives with first-party UI policy. Five stored callbacks
remain inside the object and no allocator, RTOS, protobuf, or compiler-runtime
edge appears. See
[`g2-conversate-ui-menu-page-recovery.md`](g2-conversate-ui-menu-page-recovery.md).

The Conversate tag-page closure adds no utility gap. Its two RTOS calls are the
exact admitted CMSIS-FreeRTOS v10.5.1 tick wrapper at selected commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; all other non-first-party edges
terminate at admitted EasyLogger/LVGL or bounded IAR clear/copy primitives.
See [`g2-conversate-ui-tag-page-recovery.md`](g2-conversate-ui-tag-page-recovery.md).

The exit-prompt closure also adds no utility gap. Thirty-five calls terminate
at admitted EasyLogger and fifteen at the selected LVGL 9.3-compatible commit;
the only remaining providers are three first-party fade-animation entrypoints.
See [`g2-exit-prompt-recovery.md`](g2-exit-prompt-recovery.md).

The eAT core closure resolves its utility boundary without inventing an
upstream identity. Its only reusable calls are admitted EasyLogger and six
known IAR DLIB primitives; exact public-source fingerprint searches returned
no match, while parser and callback policy remain first-party/private. See
[`g2-at-core-recovery.md`](g2-at-core-recovery.md).

The HAL I2C closure broadens the selected AmbiqSuite 5.1.0 shortcut to the
complete GPIO/IOM call family used by the G2 I2C wrapper. Public replay commit
`5efc0228…` is the authenticated source oracle; the private pre-import
generating commit and hardware validation remain open. See
[`g2-hal-i2c-recovery.md`](g2-hal-i2c-recovery.md).

The ring-battery service adds no utility gap: 15 calls terminate at admitted
EasyLogger, two at bounded IAR `memset`, and two at first-party service-record
transport. Its exact public symbols and filename have no indexed public source,
so no upstream identity or commit is invented. See
[`g2-service-ring-battery-recovery.md`](g2-service-ring-battery-recovery.md).

The OPT3007 register initializer is specification-closed. Its 57 output bytes
reconstruct 19 `(MSB, LSB, register)` triples matching TI SBOS864 exactly;
there is no public code checkout to version, and its five calls are admitted
EasyLogger. See
[`g2-opt3007-registers-recovery.md`](g2-opt3007-registers-recovery.md).

The codec porting seam adds no utility gap. Its sole generic data-structure
call is the exact production-owned AndersKaloer `ring_buffer_init` at the
already proven commit interval; all other edges are admitted logging or
first-party UART lifecycle. See
[`g2-service-codec-porting-recovery.md`](g2-service-codec-porting-recovery.md).

The notification-thread closure exercises seven exact, production-source-owned
CMSIS-FreeRTOS v10.5.1 wrappers at `d213f261…`. Queue, thread, flags, and delay
chains therefore add no opaque utility gap; the remaining policy is first-party.
See [`g2-thread-notification-recovery.md`](g2-thread-notification-recovery.md).

The GX8002B host driver closes a misleading vendor-named seam. Its three
embedded utility bodies are exact CMSIS-Core NVIC helper semantics, and its 13
HAL calls map to 12 functions in AmbiqSuite 5.1.0 `am_hal_i2s.c` at public
replay `5efc0228…`. NationalChip's gated LVP package is external device
firmware/tooling and contributes no linked code to the G2 object. See
[`g2-drv-gx8002b-recovery.md`](g2-drv-gx8002b-recovery.md).

The adjacent production PDM object applies the same shortcut to a second HAL
module: 13 calls map to 12 functions in Apollo510 `am_hal_pdm.c` at public
replay `5efc0228…` / Git blob `23a440bf…`. Its three local utility bodies are
CMSIS-Core NVIC helpers already admitted at `d23a6949…`; no hidden PDM utility
or new vendor dependency remains. See
[`g2-drv-pdm-production-recovery.md`](g2-drv-pdm-production-recovery.md).
The generic PDM wrapper closes the same seam through interrupt operation: it
adds the service and status APIs, bringing the confirmed public source surface
to 14 APIs, with a vector-proven IRQ entry and no hidden utility body. See
[`g2-drv-pdm-recovery.md`](g2-drv-pdm-recovery.md).

The complete `service_ancc.c` closure likewise exposes no utility gap. Its
12-function object makes 85 EasyLogger, 17 exact CMSIS-FreeRTOS mutex, 10
bounded IAR, and 17 closed first-party calls, with no direct or embedded Ambiq
ANCC implementation. Its callback and ingress topology is fully pinned. See
[`g2-service-ancc-dependency-boundary.md`](g2-service-ancc-dependency-boundary.md).

The ALS frontier also adds no utility gap: six calls terminate at the already
bounded private OPT3007 adapter built from TI SBOS864, while all other reusable
edges are admitted EasyLogger, CMSIS-FreeRTOS delay, or bounded IAR. The full
ALS ingress and callback topology is now pinned. See
[`g2-als-dependency-boundary.md`](g2-als-dependency-boundary.md).

The BLE production thread exposes no new utility gap. Its fifteen RTOS calls
terminate at exact admitted CMSIS-FreeRTOS thread, flags, queue, delay, and
memory-pool wrappers, and its three assertion calls terminate at the admitted
FreeRTOS `ulSetInterruptMask` leaf. The complete 14-function object and hidden
stored task entry are now closed; no Cordio implementation body is present. See
[`g2-thread-ble-production-dependency-boundary.md`](g2-thread-ble-production-dependency-boundary.md).

The FlashDB service adapter adds a consumer-side provenance and safety check.
Its two database calls map exactly to `fdb_kv_get_blob` and
`fdb_kv_set_blob` in the authenticated FlashDB 2.1.1 baseline at
`714d6159…`; seven other calls map to exact CMSIS-FreeRTOS v10.5.1 wrappers.
No third-party definition is embedded. The remaining defect is first-party:
the stock FAL callbacks return zero on device failure even though FlashDB maps
only negative values to errors. OpenCFW must replace that adapter behavior
rather than attribute it to upstream FlashDB. See
[`g2-service-db-api-recovery.md`](g2-service-db-api-recovery.md).

The complete EvenAI UI object is another high-volume negative dependency
check. Its 182 LVGL calls terminate at the admitted 9.3-compatible source
family selected at `344c7c31…`; its sole RTOS call is exact
`osKernelGetTickCount` from CMSIS-FreeRTOS v10.5.1. EasyLogger and bounded IAR
memory/string seams account for the remaining utility calls, while 103 calls
remain first-party UI/stream/animation policy. No upstream body or additional
version discriminator is hidden in the 43-function object. See
[`g2-ui-even-ai-recovery.md`](g2-ui-even-ai-recovery.md).

The time-service object closes another potential utility seam without adding a
dependency family. Eight calls map to bounded IAR DLIB copy/set routines; all
remaining external calls are first-party, there are no direct CMSIS-FreeRTOS
calls, and no upstream implementation is embedded. Its placement after the
closed CMSIS object, separated only by alignment bytes, strengthens rather
than weakens the existing RTOS ownership boundary. See
[`g2-service-time-recovery.md`](g2-service-time-recovery.md).

The complete audio-thread object closes the strongest remaining compact RTOS /
codec consumer seam. Its twenty RTOS calls reach fourteen exact
CMSIS-FreeRTOS v10.5.1 wrappers at `d213f261…`; nineteen codec calls compose
already closed G2 objects, and the sole DLIB call is a four-byte fill. No
NationalChip LVP code or new third-party implementation is present. See
[`g2-thread-audio-recovery.md`](g2-thread-audio-recovery.md).

The compact-log core closes the next utility-adjacent ambiguity. The
whole-image high-volume hook at `0x0043CE9E` is G2-private compact-record code,
not the authenticated EasyLogger `elog_output` body at `0x0043D574`. Its 67
external calls terminate at admitted EasyLogger, FreeRTOS/CMSIS-FreeRTOS,
bounded IAR, and first-party providers, with no embedded third-party
definition or new version discriminator. The dependency commits therefore
shortcut the surrounding seams, but not the private 44-byte record format.
See [`g2-compress-log-core-recovery.md`](g2-compress-log-core-recovery.md).

The port closure removes the remaining storage-utility ambiguity in the pair.
All open/close/read/write/seek/remove calls are already production source-owned
over the selected littlefs v2.10.1-equivalent baseline, and both delayed-event
entries are production source-owned. What remains is only G2's five-file
rotation/manager policy and two bounded IAR format calls. See
[`g2-compress-log-port-recovery.md`](g2-compress-log-port-recovery.md).

The full shared file runtime is now formally closed too. All eighteen public
file, directory, synchronized-heap, and initialization entries are production
source-owned, and their outbound calls terminate at already selected
CMSIS-FreeRTOS, littlefs, TLSF, EasyLogger, bounded IAR, and first-party seams.
This removes the file-runtime layer from future utility-gap triage rather than
reopening it for each consumer. See
[`g2-file-runtime-recovery.md`](g2-file-runtime-recovery.md).

The compact audio estimator is now closed as first-party signal-processing
policy over bounded compiler helpers. Its ten functions contain no
NationalChip LVP or other third-party DSP body; the only reusable edges are
IAR memory/math routines and a source-owned 64-bit division helper. The exact
IAR executable identities are pinned, but an original archive checkout cannot
be inferred. The recovered 800-frame, lag-search algorithm and its stock
short-buffer over-read hazard are documented in
[`g2-service-algo-recovery.md`](g2-service-algo-recovery.md).

The UART-sync orchestration object now closes another dependency-rich consumer.
Its exact RTOS, TinyFrame, EasyLogger, IAR, and AmbiqSuite compatibility commits
explain every reusable seam, while all five local functions remain first-party
transport policy. No third-party definition or new commit discriminator is
embedded. The remaining RAM-dispatched initializer and UART electrical/timing
behavior are respectively first-party and hardware boundaries; see
[`g2-uart-sync-recovery.md`](g2-uart-sync-recovery.md).

The factory NV service similarly collapses onto the selected FlashDB 2.1.1
commit. Its five local functions embed no FlashDB body and add no version
discriminator; they own only explicit-length defaults, serial-number policy,
and magic-triggered wholesale reset. This makes the remaining work a
first-party schema/safety and golden-media problem, not an upstream utility
gap. See [`g2-service-nvdb-recovery.md`](g2-service-nvdb-recovery.md).

The production microphone test path is closed as first-party capture/routing
policy too. Restoring its stored stereo callback reveals no hidden codec-vendor
or NationalChip DSP code; only bounded IAR memory helpers and known logging are
reusable. Acoustic and routing validation remain hardware work rather than a
source-provenance gap. See
[`g2-production-mic-recovery.md`](g2-production-mic-recovery.md).

The adjacent audio-manager path is also first-party orchestration rather than a
hidden utility. Its restored peer handler and initializer expose a bounded
one-byte frame-`0x010C` protocol and first-acquire/last-release power policy.
Only admitted logging plus one IAR `memset` are reusable; there is no direct
CMSIS-FreeRTOS or DSP definition. See
[`g2-service-audio-manager-recovery.md`](g2-service-audio-manager-recovery.md).

The system KVDB path provides a direct third-party shortcut result. It reuses
the selected FlashDB 2.1.1 commit unchanged at its four core call sites and
proves that the formerly unresolved `kvbooCount` default is zero through the
reset-called IAR scatter record. Its runtime read/increment/write lifecycle and
eleven first-party migration callbacks are now bounded. Remaining FlashDB work
is golden-media, schema, non-destructive policy, and hardware validation. See
[`g2-service-kvdb-recovery.md`](g2-service-kvdb-recovery.md).

The battery-sync callback chain closes without another reusable dependency.
The `0x105` handler, ring facade, parallel charge/message facades, and shared
generic callback manager now account for 24 linked functions and all recovered
source-order gaps. Their reusable direct edges stop at admitted EasyLogger and
the production-source-owned synchronized TLSF wrappers. The generic manager's
single dynamic notify site is bounded by its own registration nodes. This
retires the callback-manager seam as a possible hidden RTOS/utility gap; the
remaining work is first-party source reconstruction and optional production
routing. See [`g2-ux-battery-sync-recovery.md`](g2-ux-battery-sync-recovery.md)
and [`g2-callback-manager-recovery.md`](g2-callback-manager-recovery.md).

The neighboring silent-mode object is likewise first-party UI policy over
already selected sources: 70 LVGL calls at `344c7c318…`, 70 EasyLogger calls at
`a596b264…`, one exact V10.5.1 `vTaskDelay`, and one bounded IAR `memset`. Its
three restored stored callbacks reveal no additional utility body or version
discriminator. See [`g2-silent-mode-recovery.md`](g2-silent-mode-recovery.md).

The adjacent onboarding data manager also adds no opaque utility definition.
Its seven functions compose 35 admitted EasyLogger calls, exact CMSIS-FreeRTOS
`osEventFlagsSet`/mutex wrappers, three bounded IAR `memset` calls, the closed
FlashDB-backed onboarding KVDB leaf, and the closed nanopb-backed onboarding
encoder. This independently reuses the selected CMSIS-FreeRTOS, FreeRTOS,
FlashDB, and nanopb commits without narrowing their existing version intervals
or exposing a private G2 generating commit. See
[`g2-onboarding-data-manager-recovery.md`](g2-onboarding-data-manager-recovery.md).

The controller above it is likewise negative for a new utility gap. Recovering
five pre-anchor helpers and three stored callbacks expands `onboarding.c` to
twelve functions, but its reusable calls remain 165 EasyLogger, 32 LVGL, exact
CMSIS-FreeRTOS `osMutexNew`, two bounded IAR `memset` sites, and already closed
onboarding/KVDB/protobuf/callback providers. See
[`g2-onboarding-controller-recovery.md`](g2-onboarding-controller-recovery.md).

The 52-function onboarding main-page object reaches a much larger reusable
surface but still exposes no new dependency: 264 selected-LVGL calls, 45
EasyLogger calls, 23 exact CMSIS-FreeRTOS tick/mutex calls, 17 bounded IAR DLIB
calls, four admitted mpaland formatter calls, and the closed nanopb-backed
onboarding service account for every non-first-party edge. See
[`g2-onboarding-main-page-recovery.md`](g2-onboarding-main-page-recovery.md).

## Priority by shortcut value

1. **FreeRTOS retained-kernel closure.** The complete linked CMSIS object and
   its version-discriminating behavior are closed. All 38 public wrappers and
   all five private helpers are production source-owned. Both message-queue
   operations are now closed through source-owned task and ISR send/receive
   chains, including copy, unlock, priority-disinherit, event-list, and
   delayed-list helpers. The G2 112-byte TCB remains a verified one-field
   V10.5.1 patch. `osDelay` and its task-delay dependency are source-owned, as
   is the complete thread-flags/notification chain with the pre-`bb8a350a`
   discriminator preserved. `osThreadNew` is also source-owned over the
   authenticated retained creators and recovered `0x70` G2 TCB seam. The
   writer-coupled kernel lifecycle pair is now source-owned too. Below CMSIS,
   the authenticated V10.5.1 `vTaskStartScheduler` algorithm is now a
   production-excluded dual-profile candidate with every G2 global and port
   dependency explicit. The authenticated `xPortStartScheduler` core and G2
   Apollo STIMER setup are now separately dual-profile qualified as well; the
   latter is corroborated by AmbiqSuite 5.1.0 commit `5efc0228`. The elapsed-
   tick/IRQ and tickless-idle algorithms are now dual-profile candidates too,
   including both stock wrap quirks. The complete generic
   `vTaskSwitchContext` path is now source-qualified as well, including the G2
   four-word stack guard and 64-entry switched-out/in trace ring. Remaining
   work is atomic production binding, device scheduling/timing/sleep
   validation, and first-party power/overflow-hook bodies; no bounded STIMER,
   scheduler-selection, or trace-ring algorithm remains opaque.
2. **EasyLogger downstream closure.** Core blob identity is already exact.
   The fixed-record pool, dummy queue, allocate/recycle/enqueue/dequeue, and
   one-shot initialization are now closed as a clean-room dual-profile
   candidate. The callback setters, default-metadata setter, and bounded record
   drain are closed by a second dual-profile candidate. A third closes the
   CMSIS event-worker/thread orchestration across all 16 event combinations,
   leaving the seven first-party persistence handlers explicit. Remaining work
   is target concurrency/hardware stress, production admission, and
   image-specific transports; no upstream commit can supply these G2-local
   routines.
3. **LVGL/FreeType hardware-port boundary.** FreeType is exact; the LVGL
   official-core interval, exact Ambiq subtree, handler-patch ancestry,
   complete `lv_global_t` ABI, NemaGFX/NemaVG versions, public archives, and
   command-list/power configuration are closed. All 11 exact-archive GPU-patch
   exports now have bounded source candidates; all recovered-LVGL patch
   dependencies and all non-required exports are behaviorally closed.
   The complete stock 18-function / 614-byte bare-metal HAL cluster is also
   behaviorally bounded, including IRQ 28, three heaps, cache policy, and the
   100-entry ring. Remaining work is an explicit source/binary production-
   admission choice, atomic HAL integration, and Apollo510 validation. The
   separate private Ambiq display port is already source-owned across all
   seven linked functions / 638 stock bytes; no third-party input-port path is
   linked, and input/display managers are first-party boundaries.
4. **Cordio mixed-tree admission.** The aggregate closure audit reconciles all
   27 retained reusable stack/port paths with 68 focused module audits and
   leaves no third-party module unclassified. Continue with per-module r20,
   R4, or AmbiqSuite oracles; a single pristine checkout cannot explain the
   stock host. Remaining work is production admission/placement and target
   validation. The retained application/product paths are first-party boundary
   work, not another upstream dependency gap; EUS/ESS/EFS/NUS are now
   explicitly closed on that side of the boundary.
5. **First-party CLI commands and schemas.** The reusable FreeRTOS+CLI
   interpreter and mpaland-derived formatter are source-owned. Further command,
   descriptor, and schema recovery is first-party work, not an upstream utility
   gap; the CLI's exact historical checkout and formatter checkout are
   binary-unobservable and have no functional payoff.
6. **IAR DLIB provenance.** Continue only when release-matched archives become
   available. The currently bounded executable functionality has already been
   recreated, so an exact archive has lower functional payoff than the rows
   above.

## Gates before declaring third-party opacity closed

- Preserve the new origin-aware Apollo companion manifest. It exactly splits
  all 3,424,780 builder-owned opaque-base bytes into 130,000 retained third-
  party-path bytes, 461,468 first-party/project-path bytes, 675,636 unanchored
  discovered-function bytes, and 2,157,676 bytes outside trustworthy function
  envelopes. It also fails closed on 1,592 controlled patch bytes that the
  hand-partitioned flash plan still labels `official_blob`.
- Keep the authenticated TinyFrame core immutable in production routing;
  do not treat the G2 `TF_Config.h`, object magic, logging, callbacks, or
  transport as upstream.
- Obtain golden hardware captures for littlefs, FlashDB, and TinyFrame where
  the remaining uncertainty is runtime media/wire behavior rather than source
  lineage.
- Keep exact-checkout claims `null` when source-identical commits or vendor
  patches make the historical repository state unobservable from the binary.
- Keep the 43-entry CMSIS function map and physical-object hash as the
  admission boundary; do not infer ownership of dead-stripped APIs or the
  Even-extended FreeRTOS TCB from the upstream wrapper source.

After those gates, the useful next frontier is first-party ownership recovery,
not discovering another Apollo third-party family.

The complete `ui_onboarding_stock_page.c` audit reinforces that boundary. Its
597 external direct calls all terminate at selected LVGL/EasyLogger sources,
exact CMSIS-FreeRTOS mutex wrappers, bounded IAR DLIB, or already bounded G2
providers. It contains no reusable implementation body and exposes no new
version or commit discriminator; see
[`g2-onboarding-stock-page-recovery.md`](g2-onboarding-stock-page-recovery.md).

The sibling `ui_onboarding_news_page.c` closure reaches the same result across
470 external calls. Its only additional reusable seams are the already routed
ARM EABI unsigned-division helper and the closed G2 time service. Two apparent
interior BL targets are overlapping halfword decodes, not functions. No new
dependency body, version discriminator, or recoverable producing commit is
present; see
[`g2-onboarding-news-page-recovery.md`](g2-onboarding-news-page-recovery.md).

The complete first-party `lvgl_font_manager.c` object now confirms that its
only font-engine calls are the admitted `lv_freetype_font_create`/`delete`
entries over exact FreeType 2.9.1 commit `86bc8a950…`. XIP access, allocation,
and logging terminate at already closed providers. External font media and
hardware validation remain gates; no additional local FreeType or LVGL utility
body is hidden in the manager. See
[`g2-lvgl-font-manager-recovery.md`](g2-lvgl-font-manager-recovery.md).

The complete `common_list_container.c` object adds no dependency gap. All 419
direct external calls terminate at admitted or bounded providers, and both
indirect selection calls resolve through the only two constructor sites to one
exact first-party callback. See
[`g2-common-list-container-recovery.md`](g2-common-list-container-recovery.md).

The complete `common_text_container.c` object likewise adds no dependency
gap. Its 426 direct external calls terminate at admitted or bounded providers,
and all four indirect navigation calls resolve through the only two
constructor sites to one exact `evenhub_ui.c` callback. Three restored
functions add no embedded utility definition or version discriminator. See
[`g2-common-text-container-recovery.md`](g2-common-text-container-recovery.md).

The complete `evenhub_ui.c` object adds no dependency gap despite its larger
surface. All 823 direct external calls terminate at admitted or bounded
providers; two dynamic sites resolve to three exact internal callbacks. The
sixteen restored functions embed no reusable utility definition and expose no
new version discriminator. See
[`g2-evenhub-ui-recovery.md`](g2-evenhub-ui-recovery.md).

The complete `evenhub_data_parser.c` object adds no dependency gap. Its 541
direct external calls terminate at admitted nanopb, CMSIS-FreeRTOS, LVGL, and
EasyLogger sources or bounded providers; it has no indirect calls. Two
restored functions and the inline parser tables expose no reusable utility
definition or new version discriminator. See
[`g2-evenhub-data-parser-recovery.md`](g2-evenhub-data-parser-recovery.md).

The complete `sync_framework.c` object also adds no dependency gap. Its 1,051
external direct calls terminate at admitted CMSIS-FreeRTOS, FreeRTOS,
TinyFrame, AmbiqSuite, nanopb, and EasyLogger sources or bounded providers.
Twenty restored listener/callback functions and fourteen indirect sites expose
only first-party synchronization policy and no new version discriminator. See
[`g2-sync-framework-recovery.md`](g2-sync-framework-recovery.md).

The adjacent `sync_interface_api.c` object adds no dependency gap either. Its
CMSIS-FreeRTOS event/thread/queue entries and FreeRTOS assert seam are already
source-owned at the selected v10.5.1 commits; the remaining providers are
bounded EasyLogger, IAR, heap, and first-party role edges. See
[`g2-sync-interface-api-recovery.md`](g2-sync-interface-api-recovery.md).

The final large sync object, `display_thread.c`, also adds no dependency gap.
Its reusable edges terminate at the same admitted CMSIS-FreeRTOS, FreeRTOS,
LVGL, and EasyLogger sources or bounded providers. The main display loop and
stored callback are already production source-routed; the remaining opacity is
first-party display policy. See
[`g2-display-thread-recovery.md`](g2-display-thread-recovery.md).

The complete `drv_mx25u25643g.c` flash-driver object likewise adds no
dependency gap. Its transport calls reuse the selected AmbiqSuite Apollo510
commit `5efc0228…`; synchronization reuses CMSIS-FreeRTOS `d213f261…` over
FreeRTOS-Kernel `def7d2df…`; and three calls to `0x0048949C` are only the
already admitted shared nanopb-compatible zero initializer. The remaining
edges are bounded EasyLogger/IAR or source-owned runtime/delay providers. See
[`g2-drv-mx25u25643g-recovery.md`](g2-drv-mx25u25643g-recovery.md).

The complete `ui_msg_notif_list.c` object adds no dependency gap. Its 599
external calls reuse LVGL commit `344c7c318…`, CMSIS-FreeRTOS `d213f261…`
over FreeRTOS-Kernel `def7d2df…`, EasyLogger `a596b264…`, and TLSF
`deff9ab5…`, plus bounded IAR and first-party provider seams. Thirteen
Ghidra-missed bodies expose only notification-list construction and product
policy, not another reusable implementation. See
[`g2-ui-msg-notif-list-recovery.md`](g2-ui-msg-notif-list-recovery.md).

The complete dashboard main-screen object adds no dependency gap either. Its
519 external calls reuse EasyLogger `a596b264…`, LVGL `344c7c318…`, and
CMSIS-FreeRTOS `d213f261…` over FreeRTOS-Kernel `def7d2df…`, plus bounded IAR
and first-party dashboard/widget seams. Seventeen restored functions and seven
real interior callbacks contain only product UI behavior. See
[`g2-dashboard-main-screen-recovery.md`](g2-dashboard-main-screen-recovery.md).

The complete `teleprompt_ui.c` object also adds no dependency gap. Its 724
external calls reuse EasyLogger `a596b264…` and LVGL `344c7c318…`, plus bounded
IAR and first-party teleprompt/display providers. Thirty-eight restored bodies
and one bounded mode/event table dispatch contain no reusable implementation
or new version discriminator. See
[`g2-teleprompt-ui-recovery.md`](g2-teleprompt-ui-recovery.md).

The complete `service_em9305_dfu.c` object provides a useful vendor-negative
boundary: it contains zero direct EM9305/Packetcraft calls. Its providers are
EasyLogger `a596b264…`, the source-owned littlefs/TLSF runtime, bounded IAR,
the shared initializer admitted at nanopb compatibility commit `98bf4db6…`,
and first-party DFU helpers. See
[`g2-service-em9305-dfu-recovery.md`](g2-service-em9305-dfu-recovery.md).

The complete `conversate_tag_data.c` object is another useful negative: it
has zero nanopb or JSON calls. Its structured tag-list behavior is first-party
code over EasyLogger `a596b264…`, production TLSF wrappers over `deff9ab5…`,
and bounded IAR primitives. See
[`g2-conversate-tag-data-recovery.md`](g2-conversate-tag-data-recovery.md).

The complete `dashboard_watchface_layout4.c` object adds no dependency gap.
Its 230 external calls reuse EasyLogger `a596b264…`, LVGL `344c7c318…`, and
the AmbiqSuite 5.1.0 source-equivalent replay `5efc0228…`, plus bounded IAR and
first-party dashboard providers. The three Ambiq HAL calls form a stored MSPI
cleanup callback; the layout contains no embedded reusable implementation and
adds no private generating-commit discriminator. See
[`g2-dashboard-watchface-layout4-recovery.md`](g2-dashboard-watchface-layout4-recovery.md).

The complete `dashboard_ext.c` object also adds no dependency gap. Its
291 external calls reuse EasyLogger `a596b264…`, littlefs `0494ce71…`, nanopb
`98bf4db6…`, and FreeRTOS-Kernel `def7d2df…`, plus bounded IAR and first-party
dashboard providers. Ten recovered bodies expose first-party file-transfer and
schema policy, not another reusable implementation. See
[`g2-dashboard-ext-recovery.md`](g2-dashboard-ext-recovery.md).

The complete `dashboard_data_process.c` object adds no dependency gap. Its
255 external calls reuse EasyLogger `a596b264…`, nanopb `98bf4db6…`,
CMSIS-FreeRTOS `d213f261…`, and FreeRTOS-Kernel `def7d2df…`, plus bounded IAR
and first-party providers. The recovered bodies expose product schemas and
dashboard state policy, not another reusable implementation. See
[`g2-dashboard-data-process-recovery.md`](g2-dashboard-data-process-recovery.md).

The complete `displaydrv_manager.c` object adds no dependency gap. Its direct
reusable edges are EasyLogger `a596b264…` and CMSIS-FreeRTOS `d213f261…` over
FreeRTOS-Kernel `def7d2df…`; ULED/MSPI, thread-manager, and LVGL-port calls all
remain behind first-party seams. It contains zero direct LVGL or AmbiqSuite
edge and no embedded reusable implementation. See
[`g2-displaydrv-manager-recovery.md`](g2-displaydrv-manager-recovery.md).

The complete dashboard `ui_stock_page.c` object likewise adds no dependency
gap. Its 852 external calls reuse LVGL `344c7c318…` and EasyLogger
`a596b264…`, plus bounded IAR and first-party providers. It contains zero
CMSIS-FreeRTOS/FreeRTOS calls, no embedded reusable implementation, and no
historical source-commit discriminator. See
[`g2-ui-stock-page-dependency-boundary.md`](g2-ui-stock-page-dependency-boundary.md).

The complete `navigation_ui.c` object adds no dependency gap. Its 2,237
external calls reuse LVGL `344c7c318…`, EasyLogger `a596b264…`,
CMSIS-FreeRTOS `d213f261…`, nanopb `98bf4db6…`, and mpaland printf
`d3b98468…`, plus bounded IAR and first-party providers. The 29 restored
entries expose navigation layout and product policy, not another reusable
implementation or historical commit discriminator. See
[`g2-navigation-ui-dependency-boundary.md`](g2-navigation-ui-dependency-boundary.md).

The complete `menu_page.c` object adds no dependency gap. Its 746 external
calls reuse LVGL `344c7c318…`, EasyLogger `a596b264…`, CMSIS-FreeRTOS
`d213f261…`, and nanopb `98bf4db6…`, plus bounded IAR and first-party
providers. Its restored callbacks expose product menu/persistence behavior,
not another reusable implementation or historical commit discriminator. See
[`g2-menu-page-dependency-boundary.md`](g2-menu-page-dependency-boundary.md).

The complete `ui_health_page.c` object adds no dependency gap. Its 666
external calls reuse LVGL `344c7c318…`, EasyLogger `a596b264…`, and mpaland
printf `d3b98468…`, plus bounded IAR and first-party providers. It contains
zero CMSIS-FreeRTOS calls and no embedded implementation or historical commit
discriminator. See
[`g2-ui-health-page-dependency-boundary.md`](g2-ui-health-page-dependency-boundary.md).

The complete Ring-service object adds no dependency gap. Its external edges
terminate at EasyLogger, CMSIS-FreeRTOS, nanopb, IAR, and first-party seams;
there are zero direct Cordio calls.
See [`g2-ring-service-dependency-boundary.md`](g2-ring-service-dependency-boundary.md).

The complete input-manager object also adds no dependency gap. Its ten
functions directly call no LVGL or Cordio body; all utility edges terminate at
admitted EasyLogger, CMSIS-FreeRTOS, nanopb, bounded memory/runtime leaves, or
first-party policy. See
[`g2-service-input-manager-dependency-boundary.md`](g2-service-input-manager-dependency-boundary.md).

The complete calendar-page object adds no dependency gap. Its 722 external
calls reuse admitted LVGL, EasyLogger, and CMSIS-FreeRTOS sources plus bounded
IAR and first-party providers. The three restored functions expose page
lifecycle and timer policy, not another reusable implementation. See
[`g2-ui-calendar-page-dependency-boundary.md`](g2-ui-calendar-page-dependency-boundary.md).

The complete OTA transport adds no dependency gap. Direct calls reuse
EasyLogger, bounded IAR memory, the source-owned CRC and synchronized TLSF
wrappers, and closed first-party OTA policy. Four indirect calls are bounded
registered product callback seams. See
[`g2-ota-transport-dependency-boundary.md`](g2-ota-transport-dependency-boundary.md).

The complete EFS transport likewise adds no dependency gap. It shares the
admitted CRC/TLSF/EasyLogger/runtime seams and adds one exact source-owned
CMSIS-FreeRTOS tick call; four indirect sites remain bounded first-party
callback dispatches. See
[`g2-efs-transport-dependency-boundary.md`](g2-efs-transport-dependency-boundary.md).

The complete EvenHub loading-page object also adds no dependency gap. Its 137
external calls reuse admitted LVGL and EasyLogger sources, plus two bounded
runtime and fourteen first-party providers. Two stored function pointers close
ingress; no embedded reusable implementation or historical app commit
discriminator appears. See
[`g2-evenhub-loading-page-dependency-boundary.md`](g2-evenhub-loading-page-dependency-boundary.md).

The complete dashboard watchface layout-1 object adds no dependency gap. Its
215 external direct calls reuse selected LVGL, EasyLogger, and mpaland printf,
plus bounded IAR and first-party dashboard providers. Both indirect calls bind
to recovered local callbacks; no embedded implementation or private commit
discriminator appears. See
[`g2-dashboard-watchface-layout1-recovery.md`](g2-dashboard-watchface-layout1-recovery.md).

The complete teleprompt FSM adds no dependency gap. Its 172 external direct
calls reuse admitted EasyLogger, LVGL, and nanopb plus bounded runtime and
first-party teleprompt providers. Its only indirect call is constrained to a
nine-entry recovered local handler table. See
[`g2-teleprompt-fsm-dependency-boundary.md`](g2-teleprompt-fsm-dependency-boundary.md).

The complete health data manager adds no dependency gap. Its calls reuse
admitted EasyLogger and bounded runtime or terminate at already closed health
mutex wrappers over exact CMSIS-FreeRTOS. No reusable health calculation or
DSP implementation is embedded. See
[`g2-health-data-manager-dependency-boundary.md`](g2-health-data-manager-dependency-boundary.md).

The complete EvenHub main controller adds no dependency gap. Its 180 external
direct calls reuse admitted EasyLogger, LVGL, exact CMSIS-FreeRTOS v10.5.1,
nanopb, and production TLSF-backed heap wrappers, plus bounded runtime and
first-party EvenHub/service providers. It has no indirect call, embeds no
reusable implementation, and adds no version or historical application-commit
discriminator. See
[`g2-evenhub-main-dependency-boundary.md`](g2-evenhub-main-dependency-boundary.md).

The complete translate controller likewise adds no dependency gap. Its 156
external calls reuse admitted EasyLogger, LVGL, exact CMSIS-FreeRTOS v10.5.1,
and nanopb plus bounded IAR/EABI and first-party translate providers. See
[`g2-translate-dependency-boundary.md`](g2-translate-dependency-boundary.md).

The complete teleprompt controller also adds no dependency gap. Its 149
external calls reuse admitted EasyLogger, LVGL, CMSIS-FreeRTOS, and nanopb,
bounded IAR/EABI, or first-party teleprompt providers. See
[`g2-teleprompt-controller-dependency-boundary.md`](g2-teleprompt-controller-dependency-boundary.md).

The complete Conversate common-data object adds no dependency gap. Its 72
external calls terminate at admitted EasyLogger and LVGL text measurement or
bounded IAR DLIB. See
[`g2-conversate-comm-data-dependency-boundary.md`](g2-conversate-comm-data-dependency-boundary.md).

The complete dashboard watchface layout-3 object adds no dependency gap. Its
173 external calls terminate at admitted LVGL, EasyLogger, and mpaland printf,
bounded IAR runtime, or first-party dashboard providers. Five apparent raw
Thumb calls are the second halfwords of pinned four-byte `sdiv` instructions,
not hidden control-flow edges. See
[`g2-dashboard-watchface-layout3-recovery.md`](g2-dashboard-watchface-layout3-recovery.md).

The complete Ring-thread object adds no dependency gap, but corrects one prior
ownership boundary. Its CMSIS thread entry at `0x004C4CEC` had been counted as
Ring-profile noncode; it is now admitted once under `thread_ring.c`. The
object's reusable calls terminate at exact CMSIS-FreeRTOS v10.5.1, bounded
FreeRTOS assert and IAR seams, admitted EasyLogger, or production TLSF-backed
heap wrappers. See
[`g2-thread-ring-dependency-boundary.md`](g2-thread-ring-dependency-boundary.md).

The complete firmware event loop also adds no dependency gap and is already
source-routed. Its scheduler-facing calls terminate at exact CMSIS-FreeRTOS
v10.5.1 and FreeRTOS critical-section port bodies; diagnostics use admitted
EasyLogger. The single indirect call invokes the callback dequeued with its
argument from a bounded event record. See
[`g2-fw-event-loop-dependency-boundary.md`](g2-fw-event-loop-dependency-boundary.md).

The complete Ring-connect policy object also adds no dependency gap. Its 108
external calls terminate at admitted EasyLogger, exact CMSIS-FreeRTOS tick
access, or the already closed event-loop, protobuf-pair-manager, and BLE-owner
facades. It makes no direct Cordio or nanopb call. Three pathless tick/timeout
helpers and the stored reconnect-timeout callback complete the 15-function
object. See
[`g2-ring-connect-policy-dependency-boundary.md`](g2-ring-connect-policy-dependency-boundary.md).

The complete SystemClose object adds no dependency gap either. Fifteen
functions missed by Ghidra complete its event FIFO, page handlers, selection
animation, option builder, reflash dispatch, and display lifecycle. Its
reusable edges terminate at selected LVGL and EasyLogger or bounded IAR DLIB;
there is no CMSIS-FreeRTOS or other hidden utility. See
[`g2-system-close-dependency-boundary.md`](g2-system-close-dependency-boundary.md).

The complete Conversate controller likewise adds no opaque utility. Its
vector-referenced fatal entry calls the already identified CmBacktrace fault
provider once, corroborating the proven `4abadfa0…73714489` compatible interval
and OpenCFW's selected `73714489` snapshot without identifying Even's private
checkout. The remaining 138 external calls terminate at selected EasyLogger,
CMSIS-FreeRTOS, LVGL, nanopb, bounded IAR/EABI, or first-party seams. See
[`g2-conversate-controller-dependency-boundary.md`](g2-conversate-controller-dependency-boundary.md).

The complete EvenHub common image container also adds no opaque utility. Its
only reusable dependencies are already selected EasyLogger/LVGL plus
production source-owned TLSF-backed free and Apollo510 cache-clean leaves; one
eight-byte absolute-value helper is fully bounded. See
[`g2-common-image-container-dependency-boundary.md`](g2-common-image-container-dependency-boundary.md).

Dashboard watchface layout 2 adds no opaque utility either. Its provider graph
is the already selected EasyLogger/LVGL/mpaland-printf family plus bounded IAR
memset and first-party dashboard seams. See
[`g2-dashboard-watchface-layout2-recovery.md`](g2-dashboard-watchface-layout2-recovery.md).

The complete Conversate main-page object also adds no opaque utility or new
version signal. Its reusable edges terminate at the selected EasyLogger and
LVGL commits or the already bounded/source-recreated IAR `snprintf` seam; the
remaining edges are first-party Conversate code. See
[`g2-conversate-ui-main-page-recovery.md`](g2-conversate-ui-main-page-recovery.md).

The universal-setting service also adds no opaque utility. Its reusable edges
are selected EasyLogger, bounded IAR memory operations, the production
source-owned CCITT-FALSE provider, and already closed first-party KV writers.
No new library/version or private commit signal appears. See
[`g2-service-universal-setting-recovery.md`](g2-service-universal-setting-recovery.md).
