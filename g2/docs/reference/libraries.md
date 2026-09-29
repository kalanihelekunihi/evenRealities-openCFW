# G2 upstream libraries by payload

This document lists the upstream libraries identified in `s200_v2.2.6.10`,
with their pinned versions, licences, evidence, and recovered configuration.

Citations are `path:line` at commit `832137ec`. Three sources recur:

- **UI**: `g2/docs/upstream-inventory.md`.
- **GP**: the ledger in `g2/docs/research/third-party-utility-gap-priority.md`,
  lines 149–176.
- **DC**: `g2/tools/manifests/g2-third-party-dependency-closure.json`, one entry
  per family.

## Conventions

**Selected commit versus producing checkout.** For almost every library, the
exact private checkout that produced the image cannot be observed from the
binary. The binary proves only a compatible version *interval*. The
"selected" commit is a reproducible baseline chosen inside that interval. It
is not a claim about Even's source tree (GP; DC `historical_generating_commit`
is null for all 26 families).

**Confidence.** Each entry is marked with one of:

- **Proven**: exact bytes, strings, or tables match.
- **Strong**: several independent discriminators agree.
- **Inferred**: one line of evidence.
- **Unverified**: stated but not checked.

**Submodule column.** This gives the root submodule path under
`third-party/upstream/` from `/.gitmodules`, with its pinned commit.

- "—" means no submodule exists. These libraries are flagged ⚑.
- Every submodule is pinned at the same commit as the corresponding
  `g2/third_party/<name>` snapshot.

Recovered configuration headers and patches are copied to
`config-recovered/` (see its README).

## 1. Apollo510 main application

### 1.1 Identity table

| Library | Version / interval | Selected commit | Licence | Conf. | Evidence | Submodule |
|---|---|---|---|---|---|---|
| FreeRTOS-Kernel | V10.5.1, plus a G2 one-field TCB patch | `def7d2df2b0506d3d249334974f51e427c17a41c` (tree `7496dfa8`) | MIT | Proven (port), Strong (kernel) | `g2/docs/research/freertos-g2-config-port-audit.md:12-37`; `g2/docs/research/freertos-g2-tcb-vendor-patch-audit.md:7-30`; UI:25; GP:151 | `freertos-kernel` |
| CMSIS-FreeRTOS (CMSIS-RTOS2 wrapper) | v10.5.1; the exact `cmsis_os2.c` blob first appears at `13acfbef` | `d213f261b5be6bb29a7cce8b84071706b72f4d53` | Apache-2.0 | Proven (43 linked functions) | UI:26; GP:152 | `cmsis-freertos` |
| CMSIS_5 (RTOS2 headers used by the above) | 5.9.0 | `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c` | Apache-2.0 | Strong | GP:152 | `cmsis-5-590` |
| CMSIS-Core (selected header closure) | CMSIS_5 | `d23a6949a0331ca96853bcd98b0fdcc4db47184c` | Apache-2.0 | Strong | GP:153 | `cmsis-core` |
| AmbiqSuite Apollo510 HAL | 5.1.0 lineage (not 5.0.0 `392042e3`); the private pre-release checkout is unavailable | public replay `5efc0228528a8adce5eae0d226fac85d2551eb3b` (AmbiqMicro/ambiqhal_ambiq, "Import Apollo510 HAL from AmbiqSuite SDK 5.1.0") | BSD-3-Clause | Strong | GP:154; `g2/docs/research/third-party-dependency-closure-audit.md:60-68`; `g2/third_party/ambiqsuite-apollo510/PROVENANCE.json` | `ambiqhal-apollo510` |
| AmbiqSuite ANCC profile | 2.2.0–4.5.0 implementation-equivalent; selected 2.5.1 | `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` | BSD-3-Clause (Ambiq per-file) | Strong | GP:157 | `ambiqsuite-sdk` (subset) |
| AmbiqSuite AMOTA profile | 2.2.0–2.5.1 skeleton; selected 2.5.1 | `de5c6ba3` | BSD-3-Clause (Ambiq per-file) | Strong | GP:158 | `ambiqsuite-sdk` (subset) |
| AmbiqSuite Cordio app framework (`app_db.c` and others) | AmbiqSuite 2.5.1 family; stock extends it to a 10-record MRAM DB | `de5c6ba3` | Apache-2.0 | Strong | `g2/docs/research/cordio-ble-stack-identity-audit.md:461-465`; `third-party/README.md:54` | `ambiqsuite-sdk` (subset) |
| Packetcraft Cordio BLE host (WSF, HCI, DM, L2CAP, ATT, SMP) | public r20.05–r20.05c semantics. Ancestry: r19.02 `86372d84`. Ambiq R4.4.1 `4264b930` is a corroborating oracle. The AmbiqSuite 2.5.1 port-family archive `87b03680` is proprietary | `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` (r20.05c) | Apache-2.0 (public), with proprietary Ambiq ports | Strong | `cordio-ble-stack-identity-audit.md:18-51,369-447`; UI:1222; GP:173 | `cordio` |
| Packetcraft GATT profile (`profile_gatt.c`) | r20.05c | `3656312d` | Apache-2.0 | Strong | GP:173; `third-party/README.md:72` | `cordio` (subset) |
| LVGL core | hybrid 9.3-development fork; core interval `60d976c466e8…344c7c31` | `344c7c318047b7348e1be8572a9fd4260c251cfa` | MIT | Strong | `g2/docs/research/lvgl-ambiq-source-abi-recovery-audit.md:28-31`; UI:744-778; GP:172 | `lvgl` |
| ⚑ Ambiq LVGL draw backend (`src/draw/ambiq`) | exact subtree tree `1e774257495fa43177e04fc5c8a42a77c2d7d619`; handler ABI from `d4dcd26b`/`925470dd`; next commit `6770071c` excluded | AmbiqMicro/LVGL `5be8e0ae5077aa3880aba8a322b1487d6bc73c07` (byte-identical replay `67fd93e2`) | MIT | Proven (subtree) | `lvgl-ambiq-source-abi-recovery-audit.md:7-26,50-60` | — (vendored at `g2/third_party/lvgl-ambiq-backend`) |
| ⚑ NemaGFX / NemaVG / Ambiq GPU patch | NemaGFX 1.4.12 (API `0x01040C`), NemaVG 1.1.8; AmbiqSuite 5.1.0 `release_sdk5p1p0-634f7c117b`. Stock uses IAR objects, while the public packages ship GCC archives | ambiqhal_ambiq `b853fded7e545f005727e13bf2ce83018c7e242d`, subtree `components/graphics/NemaGFX_SDK` tree `e690768a`. Apollo5 archive first at `c6f54a95`; GPU patch first at `e3eec7f3` | Think Silicon permissive header licence (`headers/LICENSE`); archives are vendor binaries | Strong | `g2/docs/research/nemagfx-ambiq-g2-provenance-audit.md:8-45`; GP:159 | — (same repository as `ambiqhal-apollo510`, different commit; headers vendored at `g2/third_party/nema-sdk-headers`) |
| FreeType | 2.9.1 (tag object `ad55868d`) | `86bc8a95056c97a810986434a3f268cbe67f2902` | FTL | Proven | UI:32; GP:160 | `freetype` |
| littlefs | v2.10.1: the assertion-line fingerprint is unique among 38 v2 tags | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | BSD-3-Clause | Proven | UI:322-373 | `littlefs` |
| TLSF | v3.1-compatible | `deff9ab509341f264addbd3c8ada533678591905` | BSD-3-Clause | Strong | GP:162 | `tlsf` |
| LZ4 (decompress only: `LZ4_decompress_safe` at `0x0054F338`) | v1.9.4–v1.10.0 | `ebb370ca83af193212df4dcbadcc5d87bc0de2f0` (v1.10.0) | BSD-2-Clause | Strong | UI:1223; GP:163 | `lz4` |
| nanopb (runtime at `0x0048F000–0x00491400`) | 0.4.7–0.4.9.1 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` (0.4.9) | Zlib | Strong | UI:1226,1232-1239; GP:164 | `nanopb` |
| FlashDB (KVDB + FAL) | 2.1.1 (the string `2.1.1` is at `0x0078D60C`) | `714d6159e7e6afb267a3953756abca445c350e61` | Apache-2.0 | Proven (version and config) | `g2/docs/research/flashdb-configuration-recovery-audit.md:13-45`; UI:780-812 | `flashdb` |
| EasyLogger | 2.2.99 core; byte-identical from `cd93d9c7` to `a596b264` (no upstream tag). `elog_async_api.c` is G2 downstream glue | `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` | MIT | Strong | UI:814-836 | `easylogger` |
| FreeRTOS-Plus-CLI | classic V1.0.1–V1.0.4; C/H identical `43defa56…1309654d`; plus a G2 blank-input patch | `43defa566cc440251dbd6b48d1fcca27f88cfcdd` | MIT | Strong | UI:1225; GP:167 | `freertos-plus-cli` (FreeRTOS/FreeRTOS monorepo) |
| ⚑ mpaland/printf (application log formatter, with G2 `%PV`/`%pV` extensions) | formatter lineage | `d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e` | MIT | Strong | GP:168; DC `mpaland-printf` | — |
| TinyFrame | post-2.3.0; core-identical `eb75483e…a29167a6` | `eb75483e035916ef9f3e9fce0d2ae389cb09785f` | MIT | Proven (ten `TF_Error` line numbers) | UI:1224; GP:169 | `tinyframe` |
| CmBacktrace | post-1.4.1 line advertising 1.4.2. Interval `4abadfa0…73714489`; `55e7b69`+ excluded | `73714489f9d8af130aacb515586b397b604a5768` | MIT | Strong | `g2/docs/research/cmbacktrace-identity-audit.md:9-20,50-56`; GP:170 | `cmbacktrace` |
| AndersKaloer Ring-Buffer | interval `cda00e1e…190e30be` | `190e30bebcec22d7311fd941179d70b4f439c441` | MIT | Strong | GP:171 | `ring-buffer` |
| DaveGamble cJSON (parser only; 21 functions at `0x004D798C–0x004D83D8`) | v1.7.9–v1.7.12, from four discriminators | `3c8935676a97c7c97bf006db8312875b4f292f6c` (v1.7.12) | MIT | Strong | `third-party-dependency-closure-audit.md:36-58`; GP:176 | `cjson` |
| Google liblc3 (LC3 encoder in `service_audio.c`) | compatible `bb85f7dd…1de85e2d`; `9f1e206` excluded | `96a3af0beb5487aca3b98a4b992a539a1f6d80d1` (v1.1.3) | Apache-2.0 | Strong | GP:156; `g2/third_party/liblc3/PROVENANCE.json` | `liblc3` |
| Nordic nPMX (nPM1300 PMIC driver) | `v1.0.1-1-ge1aaec5`; 42 linked entries | `e1aaec53f456887a7d7b80d82f684d1ac3cb08c8` | BSD-3-Clause | Strong | GP:155 | `npmx` |
| TDK InvenSense ICM45608 driver | ABI baseline tag 1.1.2 (transport offsets 0/4/8/12; later releases add a context pointer) | `b79ae575f7f310e5ae2e1164096d1a858bb74662` | mixed: root BSD-3-Clause; five headers restricted; EDMP payloads | Strong | `g2/third_party/invensense-icm45608/README.md:1-20` | `invensense-icm45608` |
| ⚑ Goodix GR551x `app_error.c`, copied as `utils\assert\util_error_check.c` | SDK 1.7.0 exact blob `d5027735`; V1.00 and 2.0.1+ excluded | earliest public carrier `854c43e0b96a24051ffce4c06ff629255aa56c59` (tiko0755/X216) | BSD-3-Clause (Goodix per-file) | Proven (43-row table) | `third-party-dependency-closure-audit.md:70-82`; GP:174 | — (vendored at `g2/third_party/goodix-gr551x-app-error`) |
| ⚑ IAR DLIB / compiler runtime | EWARM 9.20+; 9.60.2 is the leading candidate | none (proprietary) | IAR proprietary | family Proven | see [toolchains.md](toolchains.md) | — |

The retained `__FILE__` paths show seven third-party directory families
(LVGL `lvgl_v9.3`, Cordio, EasyLogger, littlefs, TLSF, TinyFrame, Ring-Buffer).
They anchor 530 functions. The other families are identified by code and
strings only (`g2/docs/research/apollo-embedded-source-path-census.md:29-41`).

### 1.2 Recovered configuration (main)

**FreeRTOS** (Proven unless noted;
`freertos-g2-config-port-audit.md:175-265`):

- **Port and FPU.**
  - `ARM_CM55_NTZ/non_secure` port (IAR), with `configENABLE_TRUSTZONE=0`,
    `configENABLE_MPU=0`, `configENABLE_FPU=1`.
  - `configENABLE_MVE` is unresolved.
- **Interrupt priorities.**
  - `configMAX_SYSCALL_INTERRUPT_PRIORITY=0x30`.
  - The PendSV/SysTick priority is `0xFF`.
- **Scheduler.**
  - `configMAX_PRIORITIES=56`, `configMAX_TASK_NAME_LEN=32`, 32-bit ticks.
  - `configTICK_RATE_HZ=1024`, driven by STIMER 32.768 kHz/32.
  - Preemption, time slicing, and idle-yield are enabled.
  - No port-optimised task selection.
  - Tickless idle is enabled, with an expected idle time of 2.
- **Hooks.** The idle hook and malloc-failed hook are enabled; the tick hook is
  not. Stack-overflow checking is `>1`, with four `0xA5A5A5A5` words.
- **Allocation.** Both static and dynamic allocation are enabled.
- **Timers.** Timers are enabled, with `INCLUDE_xTimerPendFunctionCall=1`,
  queue length 50, and timer task priority 54.
- **Kernel features.**
  - Mutexes, recursive mutexes, and the trace facility are enabled.
  - Queue sets are off, and there is no queue registry.
  - Task notifications have one array entry.
- **Heap.** `heap_4` with `configTOTAL_HEAP_SIZE=0x2F000`.
- **TCB fields.** No application tag, TLS pointers, runtime stats, newlib or
  C-runtime TLS, or POSIX errno. `INCLUDE_vTaskSuspend=1`.
- **Vendor patch.** The TCB is 112 bytes: a vendor `uint32` stack depth sits
  at `+0x54`, after `pcTaskName`. This is recovered as the patch
  `config-recovered/freertos-kernel/g2-patches/g2-tcb-v10.5.1.patch`.

**CMSIS-FreeRTOS.** All 43 linked wrapper functions are recovered (38 public
and 5 private). The historical checkout is unobservable (GP:152).

**littlefs** (Proven; UI:322-393):

- the geometry recorded in [memory-map.md](memory-map.md) §2.4;
- assertions and debug/warn/error output enabled;
- trace, `LFS_THREADSAFE` and `LFS_MULTIVERSION` disabled;
- dynamic allocation enabled;
- NOR address = `0x01400000 + block·0x1000 + offset`.

**FlashDB** (Proven; `config-recovered/flashdb/g2-config/fdb_cfg.h`):

- `FDB_USING_KVDB` in FAL mode;
- `FDB_WRITE_GRAN=1`, sector 4 KiB;
- KV and sector cache tables of 64 entries each;
- no `FDB_KV_AUTO_UPDATE`, no debug, no file mode, no live TSDB.

It has two databases: `sysenv` on partition `kvdb` and `factory` on `NVdb`.
The 21 default KV values are recovered as well
(`flashdb-configuration-recovery-audit.md:13-50,64-77`).

**EasyLogger** (Proven; UI:838-866):

- a 1,024-byte output buffer, with text colours enabled;
- filter level `ELOG_LVL_INFO`;
- five 33-byte tag-level slots;
- format masks: `0xFF` for assert, `0x87` for error through verbose;
- a CMSIS mutex with a 1,000-tick timeout;
- G2-specific async queue glue: 255-record cap, event bits 1/2/4/8.

**LVGL** (Proven subset; `config-recovered/lvgl/`; UI:744-778):

- **Display and colour.** A 576×288 display at DPI 130. The native format is
  L8 (`LV_COLOR_DEPTH 8`); the Ambiq output is A4, with a `0x14400`-byte
  buffer.
- **OS and allocator.** FreeRTOS OS integration, and a custom malloc (not the
  built-in TLSF).
- **Enabled features.**
  - FreeType, littlefs FS, BMP, flex, grid, span, and built-in object IDs;
  - the Ambiq draw backend and Ambiq VG, with 100 × 1 KiB command-list
    sectors.
- **Disabled features.** Complex software masks and compressed fonts.
- **Logging.** The log level is WARN, with null assertions enabled.
- **ABI.**
  - `sizeof(lv_global_t)=0x1EC`, `lv_display_t=0x31C`, `lv_draw_buf_t=0x1C`;
  - the draw-thread stack is 32 KiB;
  - the ABI needs the Ambiq `clear_cb`/`copy_cb` extension
    (`config-recovered/lvgl/tools-patches/`).

**FreeType.** Ten modules, in this order: autofit, truetype, cff, psaux,
psnames, pshinter, sfnt, smooth, smooth-lcd, smooth-lcdv. Other recovered
settings are v40-minimal TrueType hinting, GX variation services, and an
`am_ftsystem.c` allocator. The module table `ft_default_modules[]` is at
`0x0073EEF8` (Proven; `config-recovered/freetype/`; GP:160).

**NemaGFX.** `NEMAGFX_POWER_SAVE=1`. Stock uses
`nema_cl_bind_sectored_circular`, which forces NemaGFX ≥ 1.4.12
(`nemagfx-ambiq-g2-provenance-audit.md:37-45`).

**Cordio** (Proven where stated; `config-recovered/cordio/`):

- `DM_CONN_MAX=3` and `WSF_BUF_FREE_CHECK_ASSERT=1`;
- WSF buffer stats/histogram and OS diagnostics are off;
- WSF buffer pools are 8×16, 4×32, 10×64 and 20×480;
- the WSF timer uses the field order `ticks +4`, `msg +8`, with `sec*100` /
  `ms/10` conversions. This is the Ambiq variant, not public r20.05c
  (`g2/components/README.md:54-67`);
- advertising messages use Ambiq's inline flexible-array ABI at `+8`;
- `smp_main.c` carries the Ambiq stale-AES queue cleanup
  (`cordio-ble-stack-identity-audit.md:378-410`).

**nanopb** (Proven; `config-recovered/nanopb/`; UI:1232-1239):

- `pb_size_t` is 16-bit, with 64-bit and native double support;
- error strings and callback streams are enabled;
- packed encoding is enabled;
- `PB_MAX_REQUIRED_FIELDS=64`;
- no malloc and no UTF-8 validation.

The old 0.3.x trees are ABI-incompatible.

**TinyFrame** (Proven; `config-recovered/tinyframe/`; UI:1224; the instance
is at `0x200749C4`):

- **Framing.**
  - SOF `0x01`;
  - 2-byte big-endian ID, LEN, and TYPE fields;
  - CRC-16/ARC checksum;
  - `TF_MAX_PAYLOAD_RX=0x6000`;
  - a 1 KiB send buffer.
- **Listeners and timeout.** ID/type/generic listener tables of 128/32/10
  entries, and a parser timeout of 100 ticks.
- **Concurrency.** No mutex.
- **ID allocation.** Request IDs are `(next++ & 0x7FFF) | peer_bit`, with
  master = bit 1.

**CmBacktrace** (Proven for the first block of `cmb_user_cfg.h`):

- FreeRTOS OS platform;
- dump stack info enabled;
- `CMB_NAME_MAX 40`;
- call-stack depth 32;
- dump depth 16;
- English messages (39 entries at `0x006D3718`).

The CPU is set to M33-class; this is a compatibility choice
(`cmbacktrace-identity-audit.md:24-50`).

**FreeRTOS-Plus-CLI.** Blank input suppresses the "Command not recognised"
text. The stock span is `[0x005848CA,0x005848F4)`
(`config-recovered/freertos-plus-cli/`).

## 2. Apollo510 bootloader

| Library | Identity | Conf. | Evidence | Submodule |
|---|---|---|---|---|
| littlefs | v2.10.1: same geometry as main; `lfs_config` at `0x00431070`; public subset `0x00415128–0x0041531C` | Proven | UI:344-378 | `littlefs` |
| EasyLogger | 2.2.99 (`elog.c`, `elog_utils.c` only); synchronous channel-1 sink | Strong | UI:817-820 | `easylogger` |
| TLSF | v3.1 family; allocator initializer at `0x0041FD70` | Strong | `g2/docs/research/peripheral-oss-library-provenance-audit.md:27`; UI:39 | `tlsf` |
| AmbiqSuite MSPI HAL | 5.1.0; `am_hal_mspi_interrupt_clear` is an exact translation-unit leaf; `am_hal_mspi_interrupt_service` and `power_control` | Strong | `g2/docs/memory-map.md:229-231,256` | `ambiqhal-apollo510` |
| FreeRTOS with a CMSIS-RTOS2-style wrapper | family certain; revision **not** inherited from main | Strong (family) | `peripheral-oss-library-provenance-audit.md:28` | `freertos-kernel` / `cmsis-freertos` (revision unverified) |
| ⚑ IAR runtime (C11 constraint handler, qsort, 64-bit divmod, double helpers, TLS leaf) | IAR | Strong | [toolchains.md](toolchains.md) §2 | — |

## 3. EM9305 (BLE controller)

| Library | Identity | Licence | Conf. | Evidence | Submodule |
|---|---|---|---|---|---|
| Quantum Leaps QP/C (QEP/QF/QK; the EM "RTEF" port) | v6.5.1 (`QP_VERSION 651U`, release code `0x8E7055B4`); commit `416dcec8820b9cdb5827497e645d0d9375db53c6` | GPL-3.0-or-later OR commercial | Proven (exact SDK archive bodies) | `g2/docs/research/em9305-qpc-arcompact-audit.md:46-75`; UI:1228 | `qpc` |
| ⚑ EM9305 SDK v4.2 libraries: PML, sleep manager, sleep timer, protocol timer, unitimer, EM system/HAL/radio/NVM, `aoad` | exact archive bodies (98 in the first six archives) | proprietary; third-party mirror oracle `e4412bc9` | Proven | `g2/docs/research/em9305-sdk-archive-match-audit.md:15-35` | — |
| ⚑ Packetcraft / EM Bleu BLE 5.4 controller (`lib_emb_controller.a`, `…_iso.a`) | `LL_VER_NUM=28992`. The public r20.05c has `1366`, so there is no public source commit | proprietary/confidential notices | Proven (artifact) | `g2/docs/research/em9305-expanded-sdk-archive-census.md:126-160` | — (the `cordio` submodule is the older host-only comparator) |

**QP/C configuration** (Proven; `em9305-qpc-arcompact-audit.md:214-235`):

- **Framework limits.**
  - `QF_MAX_TICK_RATE=0`: no time events are linked.
  - `QF_MAX_ACTIVE=16` and `QF_MAX_EPOOL=2`.
- **Field sizes.**
  - `Q_SIGNAL_SIZE=2`.
  - `QF_EQUEUE_CTR_SIZE=1`.
  - `QF_MPOOL_SIZ_SIZE=2` and `QF_MPOOL_CTR_SIZE=2`.
- **Structure sizes.** `sizeof(QActive)=36` and `QK_attr_=8`.
- **Q-SPY and critical sections.**
  - `Q_SPY` is off.
  - The critical section is `CLRI; SYNC` / `SETI`.
- **Vendor hooks.** `QF_onStartup` is at `0x00311154` and `QK_onIdle` at
  `0x003115E4`.

**Controller configuration.** This is Proven for the baseline archive header,
but that header does not fully describe the final link:

- BT 5.4 (`BT_VER=13`), with all four roles enabled;
- encryption, PAST, and power control enabled;
- CTE and ISO disabled in the header, although ISO/BIG bodies are linked;
- `LL_MAX_CONN=4`, `LL_MAX_FRAG=8`, `LL_NUM_ADV_FILT=8`;
- `LL_MAX_ADV_SETS=2`, `LL_SCAN_PHY_MAX=3`, `LL_MAX_PER_SCAN=6`.

Source: `em9305-expanded-sdk-archive-census.md:126-146`.

## 4. GX8002 codec

All entries are ⚑: no submodule exists for any GX8002 library.

**NationalChip LVP KWS SDK (`grus` platform, SPL, drivers, KWS app)**
(Strong; SDK objects match 68 stock symbols).

- Identity: `github.com/NationalChip/lvp_kws` at
  `8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5`.
- Licence: MIT for the source, but the prebuilt driver, speech, decoder, and
  DSP libraries are not source.
- Evidence:
  - `g2/docs/research/gx8002-upstream-object-candidates.md:5-38`;
  - `g2/components/shared/gx8002/NATIONALCHIP-*-NOTICE.txt`, which covers
    main, KWS, mode, parameters, stream, TWS, idle, libc, SPL/startup, and
    UART boot stage 1/2.

**NationalChip LVP boot container / UART protocol** (Proven format).

- Identity: the `lvp_kws`/`lvp_sed` `uart_sendboot.c` and `patch_boot.c`
  format.
- Licence: MIT.
- Evidence: `g2/docs/research/g2-codec-fwpk-segments-recovery.md:21-41,86-98`.

**tinyprintf** (Strong).

- Identity: the SDK copy at `utility/libc/tinyprintf.c`.
- Licence: see `TINYPRINTF-NOTICE.txt` (BSD-style).
- Evidence: `g2/docs/research/gx8002-printf-recovery.md:1-20,96-109`.

**newlib libm** (for example `scalbnf`) (Inferred).

- Identity: lineage at newlib mirror commit `4aa696c8` (`FLT_SMALLEST_EXP -22`).
- Licence: newlib (BSD-style).
- Evidence: `g2/components/shared/gx8002/scalbnf-underflow-correction.md:23-28`.

**GCC libgcc `fp-bit.c` soft-double** (Strong).

- Identity: C-SKY GCC `1e9b70447a8417f5c692370de4533e43d754e8fa` source
  lineage.
- Licence: GPL with the Runtime Library Exception.
- Evidence: `g2/docs/source-only-goal.md:13481,13553`.

**U-Boot-derived simple CLI** (stage 1) (Strong family).

- Identity: fork and release unknown.
- Licence: GPL-2.0 (U-Boot).
- Evidence: `g2/docs/research/peripheral-oss-library-provenance-audit.md:19,103-108`.

**LVP_KWS gxNPU model** (Proven extents).

- Identity: a trained model: 9,164-byte command stream and 120,800 weights.
- Licence: proprietary.
- Evidence: `g2/docs/research/g2-codec-stage2-sections-recovery.md:79-95`.

## 5. Touch (PSoC 4000T)

No open-source library is authenticated. The binary shows GCC/newlib startup
idioms and EasyLogger-style strings only. Whether ModusToolbox, PDL, or
CapSense middleware was used is unresolved
(`g2/docs/research/peripheral-oss-library-provenance-audit.md:23`;
`g2/docs/research/g2-touch-identity-recovery.md:56-61`).

## 6. Case (STM32G0)

| Library | Identity | Conf. | Evidence | Submodule |
|---|---|---|---|---|
| FreeRTOS kernel, GCC `ARM_CM0` port | V10.x (likely V10.3.1–V10.5.1 via STM32CubeG0). Tasks: `ledTask`, `pwrManagerTask`, `glsDetectTask`, `defaultTask`. Timers are enabled | family and port Proven; release Inferred | `g2/docs/research/g2-box-stm32g0-platform-recovery.md:61-110` | `freertos-kernel` (V10.5.1 pin is **not** proven for the case) |
| ⚑ STM32CubeG0 HAL/LL (FLASH, OB, UART) | version unknown (no strings) | family Strong | `g2-box-stm32g0-platform-recovery.md:112-146` | — |
| ⚑ STM32 CMSIS device header (`stm32g0b1xx.h` IRQ map) | `cmsis_device_g0` | Strong | `g2-box-stm32g0-platform-recovery.md:38` | — |

## 7. Libraries lacking a root submodule

- **Ambiq LVGL backend** (AmbiqMicro/LVGL `5be8e0ae`). It is vendored only at
  `g2/third_party/lvgl-ambiq-backend`.
- **NemaGFX SDK headers** (ambiqhal_ambiq `b853fded`). They are vendored at
  `g2/third_party/nema-sdk-headers`. The existing `ambiqhal-apollo510`
  submodule is the same repository at a different commit.
- **Goodix GR551x `app_error.c`** (carrier `tiko0755/X216@854c43e0`). It is
  vendored at `g2/third_party/goodix-gr551x-app-error`.
- **mpaland/printf** (`d3b98468`) has no snapshot at all.
- **Proprietary items, which cannot be submodules:** IAR DLIB, the EM9305 SDK
  v4.2 archives and controller, the NationalChip prebuilt libraries and model,
  and the STM32CubeG0 HAL. The NationalChip `lvp_kws` SDK is itself public and
  MIT but has no submodule.
- **Subsets of an existing submodule:**
  - `ambiqsuite-{amota,ancc}-profile` and `ambiqsuite-cordio-app-framework`
    come from `ambiqsuite-sdk`;
  - `packetcraft-gatt-profile` comes from `cordio`.

## 8. Licensing position

The official payloads are vendor-proprietary and not redistributable
(`g2/blobs/official/g2-2.2.6.10/PROVENANCE.md:27-29`). The licences above
govern only the identified upstream sources.
