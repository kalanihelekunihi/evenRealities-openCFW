# R1 toolchain and dependency identities (stock 2.2.6.0009)

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


Goal: a from-source build whose bundle is byte-identical to the locked official artifact. This
file records what the stock image is built from, the evidence for each identity, and what still
blocks byte equality.

Tags: **Proven** means body/hash-pinned or version-string-pinned. **Strong** means several
function-level matches. **Inferred** is derived. **Unverified** has no evidence. Sources are
repository-root paths with line numbers.

## 1. Stock component identities

| Component | Identity | Pin / hash | Tag | Evidence |
|---|---|---|---|---|
| Nordic nRF5 SDK | 17.1.0 (`nRF5_SDK_17.1.0_ddde560.zip`) | archive sha256 `5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061` | Proven | `third-party/fetched/manifest.json` (`nordic-nrf5-sdk`); `r1/research/bootloader-reconstruction/SDK-SOURCE-MANIFEST.md:9-12`; 782 source-routed functions (564 app + 218 bootloader), `r1/docs/correlation/NORDIC-SDK-CORRELATION.md:928-931` |
| SoftDevice | S140 7.2.0, FWID `0x0100` | hex sha256 `c52b61a6ceeb58438dbef075abfc5f6812718dda78630b39e82a20829f09c125` | Proven | `manifest.json` (`nordic-s140`); `r1/research/decompilation/README.md:28` |
| Bootloader | SDK 17.1.0 secure BLE bootloader, `pca10056_s140_ble` family, CC310_BL + nrf_crypto ECDSA-P256/SHA-256, nanopb. Split: 218 Nordic / 41 CryptoCell / 30 nanopb / 12 ArmCC runtime / 3 R1 | live sha256 `566cd2a5…34ab8b` | Proven | `r1/research/bootloader-reconstruction/README.md:26-28`; `SDK-SOURCE-MANIFEST.md:46-56` |
| CryptoCell library | `nrf_cc310_bl` (SDK 17.1.0 ships `libnrf_cc310_bl_0.9.13.a`); `PkaEcdsaVerify` etc. | SDK archive | Strong (family); version Inferred from SDK | `research/bootloader-reconstruction/README.md:91`; `firmware-project/Makefile:162-165` |
| FreeRTOS kernel | 10.5.1 (tag V10.5.1) | commit `def7d2df2b0506d3d249334974f51e427c17a41c`, tree `7496dfa8…` | Proven (`prvReloadTimer` at `0x00085440`, SHA-256 `d03d69b2…b635`) | `r1/docs/correlation/FREERTOS-KERNEL-VERSION-CORRELATION.md:3-13`; `manifest.json` (`freertos-kernel`) |
| FreeRTOS port | Nordic SDK 17.1.0 `external/freertos/portable/{<toolchain>/nrf52, CMSIS/nrf52}` (RTC tick, tickless via `nrf_pwr_mgmt`) | SDK archive | Strong | `manifest.json` (`nordic-freertos-nrf52-port`); `NORDIC-SDK-CORRELATION.md:745-813` |
| CMSIS-RTOS2 wrapper | Arm CMSIS-FreeRTOS 10.5.1 (CMSIS_5 5.9.0 headers) | commit `d213f261b5be6bb29a7cce8b84071706b72f4d53`, `cmsis_os2.c` sha256 `8a0d60b5…c36` | Strong (56-priority check, 0x100-word default stack, 1024 Hz, 10.5.1 ISR event-flag behaviour, `0x7D154-0x7D9EA`) | `manifest.json` (`arm-cmsis-freertos`) |
| FreeRTOS heap | `heap_4` | – | Strong | `r1/docs/README.md:695-698` |
| FlashDB | 2.0.0 | commit `4e5677408256f82d47cd56a6b04605dcee35ed9a`, archive `7758fb46976acebc754fb452bbac2144badc713a3e158bab8a8961bc112eca1b` | Proven (reverse TSL iteration, `_fdb_db_path`) | `r1/docs/correlation/FLASHDB-FAL-CORRELATION.md:5-27,88-93` |
| FAL | 0.5.99 (nested in FlashDB 2.0.0) | string at `fal_init` `0x00062F40` | Proven | `FLASHDB-FAL-CORRELATION.md:24-26` |
| CmBacktrace | 1.4.2-compatible interval `4abadfa0..73714489` (first incompatible `55e7b699`) | snapshot `73714489f9d8af130aacb515586b397b604a5768` | Strong (interval); exact checkout Unverified | `r1/docs/correlation/CMBACKTRACE-CORRELATION.md:5-24` |
| SEGGER RTT | 6.18a (SDK-bundled). `SEGGER_RTT_Init` at `0x36D68`; Terminal channel; up buffer 512 B, down buffer 64 B | `SEGGER_RTT.c` sha256 `52f9a10b…9088` | Proven | `manifest.json` (`segger-rtt`); `NORDIC-SDK-CORRELATION.md:913-916` |
| SEGGER printf | 6.14d formatter (`nrf_fprintf`) | `nrf_fprintf_format.c` sha256 `d377680d…4487` | Strong | `manifest.json` (`segger-fprintf`) |
| Nordic logging | `nrf_log` frontend + RTT and serial backends, `[RING]` module prefix, R1 clock prefix hook at `0x0008185C` | SDK | Proven | `NORDIC-SDK-CORRELATION.md:15,402-405,734-736` |
| Accelerometer 1 | Bosch BMA456 (BMA456W) SensorAPI 2.29.0 | commit `3266db2c5de15be1a00232b8c0f2fd23e07934e0` | Proven (`delay_us` at struct offset `0x2C` discriminator vs 2.24.1) | `r1/docs/correlation/MOTION-PROVIDER-CORRELATION.md:17-19`; `manifest.json` |
| Accelerometer 2 | ST LIS2DW12 pid 2.1.0 (compatible interval `18b0866f..8d4bd522`) | `8d4bd522015004a9646102702901ba5a15ec6d39` | Strong | `MOTION-PROVIDER-CORRELATION.md:53-54`; `manifest.json` |
| Accelerometer 3 | QST QMA6100/QMA6100P V1.0 lineage; no licensed source | correlation only | Inferred | `r1/docs/boundaries/NAMED-PERIPHERAL-BOUNDARIES.md:61-92` |
| NFC tag | ST ST25DVxxKC BSP (fp-sns-stbox1, compatible) | `e9a35449b777699b5e1dd0f1466de0ead554893a` | Strong (BSim 1.0 on ReadReg/WriteReg) | `r1/docs/correlation/ST25DVXXKC-CORRELATION.md`; `manifest.json` |
| AES | tiny-AES-c 1.0.0-compatible, AES-128 inverse core only (8 functions) | `e72b6eff0884673997d0ca6385169bbd9b31936d` | Strong; exact checkout Unverified | `r1/docs/correlation/TINY-AES-CORRELATION.md:3-31` |
| Touch | Azoteq IQS7211E; source lineage unproven (reference snapshots `0a88e26b…`, `436d3c42…`) | – | Inferred | `r1/docs/boundaries/IQS7211E-PROVIDER-BOUNDARY.md`; `manifest.json` |
| PPG | Goodix GH3x2x `gh3x2x-v2.23_7ecd2a`, democode v1.6, algo-call v0.5, DrvLib v4.3.0.0, Virtual_Reg v3.4. Public copy `coredevices/pebbleos-nonfree@2c0034a2`. HBA/HRV/SpO2/NADT algorithm libraries are binary-only | archive `48564d72…6d29` | Proven (version strings) | `manifest.json` (`goodix-gh3x2x`, `goodix-gh3x2x-democode`) |
| Health algorithms | GoMore SDK (362 functions). No version, source or licence identified | – | Unverified identity | `r1/docs/boundaries/GOMORE-PROVIDER-BOUNDARY.md` |
| Temperature / PMIC | GXCAS GXT310 x2; YHMICROS YHM2710. No source | – | Proven (names/IDs) | `NAMED-PERIPHERAL-BOUNDARIES.md:11-53` |
| Platform middleware | Bravechip ChipletRing / BCL603M "B210" platform (build path `product/B210/app/_build/B210_Application`; `603MV1.9.3`): device registry, software TWI, sensor stream, quantized NN runtime, time/calendar, RTC device (169 functions) | – | Strong (identity); no source | `r1/docs/PROVENANCE.md:83` |
| Compiler runtime | Arm Compiler (armcc/armlink) C library + `__aeabi_*` + math. `__scatterload`/`__scatterload_decompress` in both images | – | Proven (runtime family) | `r1/docs/correlation/TOOLCHAIN-RUNTIME-CORRELATION.md:7-79` |

Function census: 3,326 functions (3,022 application + 304 bootloader), none unclassified
(`r1/docs/reference/FUNCTION-OWNERSHIP-SUMMARY.json`, kept).

## 2. Arm Compiler evidence

| Observation | Where | Implication | Tag |
|---|---|---|---|
| `__scatterload` at `0x000283A0` and `__scatterload_decompress` at `0x000286F4` (literal/back-reference/zero-run decoder) | app; `TOOLCHAIN-RUNTIME-CORRELATION.md:47-48` | armlink with compressed RW data | Proven |
| Bootloader `armcc_scatterload` (16-byte records), runtime entry veneer → `main`, `__CC_ARM`-order `memset` core | `r1/research/bootloader-reconstruction/generated/function-names.csv` (rows `0x000f8208`, `0x000f845c`, `0x000f84c8`, `0x000f9c44`); `research/bootloader-reconstruction/README.md:90` | armcc runtime in the bootloader | Proven |
| App atomic FIFO / `nrf_atomic` at `0x000272B8..0x00027461` reproduce the SDK's `__CC_ARM` inline-assembly sequences | `NORDIC-SDK-CORRELATION.md:369-371` | `__CC_ARM` is defined by armcc (Arm Compiler 5), not by armclang (Arm Compiler 6). Points to AC5 | Strong (Inferred for AC5 vs AC6) |
| Bootloader `nrf_atomic_internal_*` match the SDK's ArmCC assembly exactly | `SDK-SOURCE-MANIFEST.md:42-44`; `research/bootloader-reconstruction/README.md:88` | same | Strong |
| `Reset_Handler`/`NMI_Handler`/`Default_Handler` route to `modules/nrfx/mdk/arm_startup_nrf52840.s` (`SystemInit` then `__main`) | `NORDIC-SDK-CORRELATION.md:38-40,372-373` | Keil/Arm startup file, not `gcc_startup_nrf52840.S` | Proven |
| Linker splits one function into a 54-byte head and 148-byte tail (`0x00075038`/`0x0007E2FC`) | `NORDIC-SDK-CORRELATION.md:436-439` | armlink / armcc code placement | Strong |
| Runtime: `rand` = `seed*1103515245+12345`, returns `seed>>1`; `qsort`, `gmtime`, `sscanf`, `strtok`, printf core, math (`atan2f`, `expf`, `powf`, …) | `TOOLCHAIN-RUNTIME-CORRELATION.md:9-79` | Arm C library (microlib or standard not yet determined) | Proven (functions) |
| CmBacktrace `cmb_get_psp`/`cmb_get_sp` are "exact GCC forms" (`MRS r0, psp; BX lr`) and CMB toolchain is recorded as GCC | `CMBACKTRACE-CORRELATION.md:32,58-59` | Contradiction to resolve: armcc `__asm` functions may emit identical bytes | Unverified |
| `nrfx_coredep_delay_us` arrays emitted per translation unit (21 copies); 8 copies of `nrf_delay_ms`; 56 out-of-line GPIO HAL copies | `NORDIC-SDK-CORRELATION.md:504-520,587-603` | armcc inlining/emission behaviour; this also fixes the translation-unit set | Strong |

**Unknown**: the exact Arm Compiler release (5.06 update level, or 6.x), library variant
(microlib or standard), optimisation level, `--split_sections`/`--feedback` use, the scatter file
and link order. This is the main blocker for byte identity
(`r1/research/bootloader-reconstruction/REBUILDABILITY.md:34,36-42`).

## 3. Bootloader rebuild attempts (GCC)

| Build | Toolchain | Result | Source |
|---|---|---|---|
| Stock (live) | armcc (unknown version) | bin sha256 `566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b`, logical 24,420 B, 285–304 functions | `research/bootloader-reconstruction/README.md:10-24` |
| SDK example reference (symbol-bearing, for BSim) | GCC 9.3.1 (`gcc-arm-none-eabi-9-2020-q2-update`, sha256 `bbb9b87e…9ac6`) | ELF `c9e3a6a0…c409`; text 24016 / data 184 / bss 21976; 321 functions | `SDK-SOURCE-MANIFEST.md:14-31` |
| sdk-overlay build | GCC 9.3.1 | ELF `f105f2392c557805c93c4feb721a31449c398c044d7c410ce06c503dd3d764d3` | `research/bootloader-reconstruction/sdk-overlay/README.md:43-46` |
| firmware-project `captured` profile (`NRF_DFU_DEBUG_VERSION`) | GCC 9.3.1 | **bin `583bb6b52a055f4955c4e1336c1d8b0397f742ac44b368678a50861755ac238e`** (hex `b0889621…b904`, out `47226c7e…da54`); used 24,256 B; text 24080; data 184; bss 21976; 321 functions; 74 objects; key at `0x000FDA44`; MSP `0x20040000`; deterministic across rebuilds and relocation | `research/bootloader-reconstruction/firmware-project/verification/reproducibility.json:2-23` |
| firmware-project `hardened` profile | GCC 9.3.1 | bin `c391cb17f90d85e433a6e103ecd312b636ea4c78b8bd2a74f15dab43ec137ac5` | same `:24-45` |

Conclusion: `REBUILDABILITY.md:34` says "byte-identical source rebuild demonstrated: no". The
vendor ArmCC version, product configuration and link decisions are absent. The GCC outputs share
the stock layout (`0xF8000`/`0x6000`, RAM `0x20005978`) but differ in:

- code generation;
- initial MSP: GCC `0x20040000` vs stock `0x2000CFA0`;
- key placement: `0xFDA44` vs `0xFD868`;
- `.data` size: 184 vs 200 bytes.

The bootloader's product inputs are recovered: the public key (`config-recovered/r1_dfu_public_key.c`),
`r1_recovered_config.h` and `r1_sdk_overrides.h`. `vendor/` contained 316 SDK files with 0
mismatches against the archive (`firmware-project/verification/upstream-inputs.json`).

Bootloader SDK compile list (firmware-project `Makefile:40-109`; the pca10056_s140_ble example set):
- startup, `nrf_log_frontend`/`str_formatter`, `app_error_weak`, `app_scheduler`,
  `app_util_platform`, `crc32`, `mem_manager`, `nrf_assert`, `nrf_atfifo`, `nrf_atomic`,
  `nrf_balloc`, `nrf_fprintf`(`_format`), `nrf_fstorage`(`_nvmc`, `_sd`), `nrf_memobj`,
  `nrf_queue`, `nrf_ringbuf`, `nrf_section_iter`, `nrf_strerror`, `system_nrf52840`;
- `cc310_bl_backend_{ecc,ecdsa,hash,init,shared}`, `boards`, `nrf_sdh`(`_ble`, `_soc`),
  `nrf_nvmc`, `nrfx_atomic`, `nrf_crypto_{ecc,ecdsa,hash,init,shared}`, `dfu_public_key`,
  `main`, `nrf_dfu_svci`(`_handler`), `nrf_svc_handler`, `ble_srv_common`;
- `nrf_bootloader`(`_app_start`, `_app_start_final`, `_dfu_timers`, `_fw_activation`, `_info`,
  `_wdt`), `pb_common`, `pb_decode`, `dfu-cc.pb`, `nrf_dfu`, `nrf_dfu_ble`, `nrf_dfu_flash`,
  `nrf_dfu_handling_error`, `nrf_dfu_mbr`, `nrf_dfu_req_handler`, `nrf_dfu_settings`(`_svci`),
  `nrf_dfu_transport`, `nrf_dfu_utils`, `nrf_dfu_validation`, `nrf_dfu_ver_validation`;
- `oberon_backend_*`;
- libraries `liboberon_3.0.8.a` and `libnrf_cc310_bl_0.9.13.a`.

Defines: `BLE_STACK_SUPPORT_REQD BOARD_PCA10056 CONFIG_GPIO_AS_PINRESET FLOAT_ABI_HARD NRF52840_XXAA NRF_DFU_SETTINGS_VERSION=2 NRF_DFU_SVCI_ENABLED NRF_SD_BLE_API_VERSION=7 S140 SOFTDEVICE_PRESENT SVC_INTERFACE_CALL_AS_NORMAL_FUNCTION`.
The stock bootloader was built with the Keil/armcc project (`arm5_no_packs`), not this GCC
Makefile (Inferred).

## 4. Application SDK/library source list (best current guess)

The openR1 GCC Makefile `r1/platform/nrf52840/sdk/Makefile:138-211` (copied byte-for-byte as
`config-recovered/sdk-source-list.mk`) is the best existing seed for the stock link set. Each
upstream unit is annotated against the stock function correlation. Legend:

- **S** = stock-linked (functions from this unit are body-matched in the image).
- **S?** = plausible but not function-proven.
- **X** = openR1-only, or known to differ from stock.

| Unit (openR1 Makefile) | Stock | Note / evidence |
|---|---|---|
| `modules/nrfx/mdk/gcc_startup_nrf52840.S` | X | stock uses `arm_startup_nrf52840.s` (`NORDIC-SDK-CORRELATION.md:38-40`) |
| `platform/.../openr1_cmbacktrace_fault.S` | X | openR1 glue; stock has five exception-entry stubs at `0x000274AC..0x000274DC` (`CMBACKTRACE-CORRELATION.md:65-68`) |
| `modules/nrfx/mdk/system_nrf52840.c` (includes `system_nrf52.c`) | S | `SystemInit` `0x00033364`, `nvmc_config` `0x0007CA7C`; `CONFIG_NFCT_PINS_AS_GPIOS`, `CONFIG_GPIO_AS_PINRESET` (`NORDIC-SYSTEM-INIT-CORRELATION.md:8-53`) |
| `external/segger_rtt/SEGGER_RTT.c` | S | 6.18a |
| `components/libraries/util/app_error.c`, `app_error_handler_gcc.c`, `app_error_weak.c` | S? / X | stock would use `app_error_handler_keil.c` (Inferred); `app_error` not function-proven |
| `components/libraries/util/app_util_platform.c` | S? | |
| `experimental_section_vars/nrf_section_iter.c` | S | |
| `atomic/nrf_atomic.c`, `atomic_flags/nrf_atflags.c`, `atomic_fifo/nrf_atfifo.c` | S | `__CC_ARM` paths |
| `fds/fds.c` | S | 41 functions; 3 pages, reserved 36 |
| `fstorage/nrf_fstorage.c`, `nrf_fstorage_sd.c` | S | API table `0x0009C86C` |
| `sortlist/nrf_sortlist.c` | S? | not in correlation list |
| `strerror/nrf_strerror.c` | S | 37-entry table |
| `timer/app_timer_freertos.c` | S? | not function-proven |
| `ble_advertising/ble_advertising.c` | S | 8 functions (`NORDIC-ADVERTISING-START-CLOSURE.md`) |
| `ble/common/ble_advdata.c`, `ble_conn_state.c`, `ble_srv_common.c` | S | |
| `nrf_ble_gatt/nrf_ble_gatt.c` | S | init `0x00078186` |
| `peer_manager/auth_status_tracker.c` | S? | not function-proven |
| `peer_manager/{gatt_cache_manager,gatts_cache_manager,id_manager,peer_data_storage,peer_database,peer_id,peer_manager,peer_manager_handler,pm_buffer,security_dispatcher,security_manager}.c` | S | 130 functions |
| `softdevice/common/nrf_sdh.c`, `nrf_sdh_ble.c`, `nrf_sdh_soc.c` | S | 500-byte BLE event buffer |
| FreeRTOS `event_groups.c list.c queue.c stream_buffer.c tasks.c timers.c` (10.5.1) | S (`stream_buffer` S?) | kernel 10.5.1 |
| `portable/MemMang/heap_4.c` | S | |
| `external/freertos/portable/GCC/nrf52/port.c` | X | an armcc build would use the SDK's ARM/RVDS nrf52 port directory (Inferred) |
| `external/freertos/portable/CMSIS/nrf52/port_cmsis.c`, `port_cmsis_systick.c` | S | RTC tick |
| `integration/nrfx/legacy/nrf_drv_clock.c` | S | clock cluster (`NORDIC-SDK-CORRELATION.md:561-583`) |
| `integration/nrfx/legacy/nrf_drv_twi.c` | S | `twi_clear_bus` `0x000938BC` |
| `nrfx_clock.c nrfx_gpiote.c nrfx_rtc.c nrfx_saadc.c nrfx_spim.c nrfx_twim.c nrfx_wdt.c` | S | SPIM2 only; TWIM0+1 |
| `CMSIS-FreeRTOS/.../cmsis_os2.c` | S | |
| `cm_backtrace/cm_backtrace.c` | S | 7 upstream bodies |
| `bma4.c`, `bma456w.c` | S | |
| `lis2dw12_reg.c` | S | |
| `st25dvxxkc.c`, `st25dvxxkc_reg.c` | S | |
| `tiny-AES-c/aes.c` (`-DECB=1 -DCBC=0 -DCTR=0`) | S | inverse core only (build defines Inferred) |
| FlashDB `fdb.c fdb_tsdb.c fdb_utils.c` + FAL `fal.c fal_flash.c fal_partition.c` | S | 33 + 10 functions |
| Goodix democode subset (`gh_drv_*`, `gh_demo*`, `gh_agc`, `gh_changeinttime`, `gh_movedetect`, `gh_multi_sen_pro`, `goodix_{hba,hrv,spo2}_config`) | S | 174 democode functions; plus binary-only algorithm libraries (not in the list) |
| `OPENR1_SOURCES` (`r1/src`, `platform`, `port`, `reconstructed`) | X | clean-room; replaced by product C to be written from pseudocode |

Stock-linked Nordic units **missing** from the openR1 list
(`NORDIC-SDK-CORRELATION.md` admitted table and sections at 504-959):

| Unit | Evidence |
|---|---|
| `components/ble/ble_link_ctx_manager/ble_link_ctx_manager.c` | `blcm_link_ctx_get` `0x000514E0` |
| `components/ble/ble_services/ble_dfu/ble_dfu.c`, `ble_dfu_unbonded.c` | 10 functions, `SUPPORTS_BONDS=0` |
| `components/ble/nrf_ble_qwr/nrf_ble_qwr.c` | `MAX_ATTR 0` |
| `components/libraries/bootloader/dfu/nrf_dfu_svci.c` | SVCI 3 |
| `components/libraries/balloc/nrf_balloc.c`, `memobj/nrf_memobj.c`, `ringbuf/nrf_ringbuf.c` | logger chain |
| `components/libraries/log/src/nrf_log_frontend.c`, `nrf_log_str_formatter.c`, `nrf_log_backend_rtt.c`, `nrf_log_backend_serial.c`, `nrf_log_default_backends.c` | logging with `[RING]` |
| `external/fprintf/nrf_fprintf.c`, `nrf_fprintf_format.c` | |
| `components/libraries/pwr_mgmt/nrf_pwr_mgmt.c` | `nrf_pwr_mgmt_shutdown` `0x00079D50`; `configPRE_SLEEP_PROCESSING` |
| `modules/nrfx/drivers/src/nrfx_nfct.c` | IRQ + 3 helpers |
| `modules/nrfx/drivers/src/nrfx_pdm.c` | PDM IRQ vector `0x000309DC` |
| `modules/nrfx/drivers/src/nrfx_timer.c` | TIMER dispatcher `0x000729EC` |
| `modules/nrfx/mdk/arm_startup_nrf52840.s` | vectors/reset |

openR1 compile flags that are not stock:
- `-Os -g3`, the GCC `-mfloat-abi=hard -mfpu=fpv4-sp-d16` spelling, `--specs=nano.specs`,
  `-ffunction-sections`/`--gc-sections`.
- The forced `__DATE__`/`__TIME__ = "Aug 14 2026" "00:00:00"`.
- `-DOPENR1_*`.

Stock-relevant defines that are Proven or Strong: `NRF52840_XXAA`, `FLOAT_ABI_HARD`,
`NRF_SD_BLE_API_VERSION=7`, `S140`, `SOFTDEVICE_PRESENT`, `CONFIG_NFCT_PINS_AS_GPIOS`,
`CONFIG_GPIO_AS_PINRESET`, `FREERTOS`, `CMB_USER_CFG`.

## 5. Cross-tree pins a stock-faithful R1 build must own

openR1 borrowed these from `g2/third_party/`. They must be pinned independently
(`r1/platform/nrf52840/sdk/Makefile:29-31`):

| Component | Commit |
|---|---|
| FreeRTOS-Kernel | `def7d2df2b0506d3d249334974f51e427c17a41c` |
| CMSIS-FreeRTOS | `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| CmBacktrace | `73714489f9d8af130aacb515586b397b604a5768` |

## 6. Open questions blocking byte equality

1. Exact Arm Compiler version (AC5 5.06uN vs AC6), C library variant, `-O`/`-Otime`/`-Ospace`
   level, `--cpu`/`--fpu` spelling, and whether link-time feedback was used. Evidence of
   `__CC_ARM` suggests AC5.
2. The armlink scatter file: region order, RW compression, ZI, stack/heap. For the bootloader,
   the stock `.data` is 200 B vs GCC 184 B, and the MSP is `0x2000CFA0`.
3. Object/link order and translation-unit boundaries of product C. Per-unit
   `nrfx_coredep_delay` copies constrain this.
4. Product `sdk_config.h` for app and bootloader. Several values in `config-recovered/sdk_config.h`
   are openR1 guesses; see `config-recovered/README.md`.
5. Kernel/port split: 10.5.1 core with SDK nRF52 port, vs the "SDK-bundled FreeRTOS 10.0.0"
   wording in `NORDIC-SDK-CORRELATION.md:745-813`. Settle which `tasks.c`/`list.c` bodies match.
6. Binary-only inputs that cannot be rebuilt from source:
   - Goodix algorithm libraries;
   - GoMore SDK;
   - Bravechip B210 platform layer;
   - `nrf_cc310_bl` / `nrf_oberon` archives;
   - the S140 hex.

   These need either vendor objects or reviewed C that reproduces the exact bytes.
7. Model data: the 46,324-byte constant union at `0x000B19E4` (`reconstructed/model_data`).
8. CmBacktrace "GCC" accessor bytes vs an armcc build (section 2).
