# R1 recovered configuration seeds

> **Citations.** Repository paths cited as `path` or `path:line` refer to the tree at commit `832137ec`. The 2026-09-29 cleanup retires many of those evidence files; after they are removed, `git show 832137ec:<path>` still shows them.


These are byte-for-byte copies of the configuration files that the deleted openR1 build and
bootloader reconstruction used. They seed a stock-faithful rebuild of R1 2.2.6.0009. **They are
not the stock configuration.** Each file mixes values proven from the stock image with openR1
design choices. The per-file tables below separate the two.

Tags:
- **Proven**: pinned in the image or a live dump.
- **Strong**: several matching facts.
- **Inferred**: derived.
- **Unverified**: an openR1 guess, or a default with no evidence.
- **openR1**: a deliberate clean-room choice, known not to be stock or irrelevant to stock.

Paths are repository-root relative. Hashes were computed at copy time; every copy is identical to
its original.

| File (here) | Original path | SHA-256 |
|---|---|---|
| `sdk_config.h` | `r1/platform/nrf52840/sdk/config/sdk_config.h` | `d7dd86c6ed2885df8bd7f1d99b6c4fb911fddd00c90f791b03385623c959920c` |
| `FreeRTOSConfig.h` | `r1/platform/nrf52840/sdk/config/FreeRTOSConfig.h` | `48c67875c6bfadf8b4144046575b652d514ad2ed561c387689366fc827e47df9` |
| `cmb_user_cfg.h` | `r1/platform/nrf52840/sdk/config/cmb_user_cfg.h` | `bfd7943411da4614ad8e6a667cf5c164c210d6492052b0025511e5263e5df106` |
| `sdk-source-list.mk` | `r1/platform/nrf52840/sdk/Makefile` | `00dd9090a44cd8d820236f2f7b468d59f566ce0f33ef3439738772159093acf2` |
| `openr1_sdk.ld` | `r1/platform/nrf52840/sdk/openr1_sdk.ld` | `ba64f9a2a7ad0bc35728b1fc860b586c5eeec06948dcfdcc4f11ea761ca17da5` |
| `fal_cfg.h` | `r1/port/fal_cfg.h` | `fcba906d82c82cd92d66859ca4df5f7bde1e0471e15763a3a34e2e3c8b24973f` |
| `fdb_cfg.h` | `r1/port/fdb_cfg.h` | `6cb06d95d79cd4f84b3fc236698489be349e70d0711889e23ca7d9e2adbd91c7` |
| `r1_recovered_config.h` | `r1/research/bootloader-reconstruction/firmware-project/config/r1_recovered_config.h` | `29d041a58ad66d87d93b78b7122e6d6b4b19c9dd38a8cc0ead5bcb67db0e25a9` |
| `r1_sdk_overrides.h` | `r1/research/bootloader-reconstruction/sdk-overlay/r1_sdk_overrides.h` | `bf87a0230829e1b82bd767055b047d3dff6b3a9d14e6f2c10971920961e0a72d` |
| `r1_dfu_public_key.c` | `r1/research/bootloader-reconstruction/sdk-overlay/r1_dfu_public_key.c` | `f26f2aa65ed8e3828c51f9f48e091c19713793193758f8c62e55145cf1daaae9` |
| `openr1_nrf52840.dts` | `r1/platform/nrf52840/zephyr/boards/openr1/openr1_nrf52840/openr1_nrf52840.dts` | `fb3e513be6927269d08dec3e5deab4a8dd5853677faa64ddf4520f7040076e9e` |
| `openr1_nrf52840-pinctrl.dtsi` | `r1/platform/nrf52840/zephyr/boards/openr1/openr1_nrf52840/openr1_nrf52840-pinctrl.dtsi` | `3a9d26b41b9ab6d880526ec9c95324174f9bc091de34183e12bd3d1e80c31a73` |

`r1_sdk_overrides.h` and `r1_dfu_public_key.c` were added beyond the requested set because a
byte-identical bootloader needs them. The firmware-project copy of the key
(`firmware-project/src/r1_dfu_public_key.c`, sha256 `78da8860…fa93`) has the same 64 key bytes and
differs only in comment wording and a trailing blank line.

Evidence documents referenced below live in `r1/docs/correlation/`, `r1/docs/boundaries/`,
`r1/docs/reference/` and `r1/research/bootloader-reconstruction/`.

---

## `sdk_config.h` (application, nRF5 SDK 17.1.0)

Purpose: the minimal `sdk_config.h` for the openR1 GCC application. It sets only the modules
openR1 compiled.

**Stock-proven or strong values**

| Lines | Values | Tag | Evidence |
|---|---|---|---|
| 13-16 | `NRFX_CLOCK_ENABLED 1`, `NRFX_CLOCK_CONFIG_LF_SRC 0` (RC), `NRFX_CLOCK_CONFIG_IRQ_PRIORITY 6` | Proven | `nrfx_clock_enable` writes LF RC and priority 6 (`NORDIC-SDK-CORRELATION.md:561-583`) |
| 17-20 | `NRFX_RTC_ENABLED 1`, `RTC2` only | Proven | `nrfx_rtc_2_irq_handler` at `0x00031750` (`NORDIC-SDK-CORRELATION.md:683`) |
| 29-33 | `NRFX_WDT_ENABLED 1`, `BEHAVIOUR 1`, `RELOAD_VALUE 10000`, `IRQ_PRIORITY 6` | Proven | `WATCHDOG-DEVICE-CORRELATION.md:30-40` |
| 38-42 | `NRFX_SAADC_ENABLED 1`, `RESOLUTION 2` (12-bit), `OVERSAMPLE 0`, `LP_MODE 0`, `IRQ_PRIORITY 6` | Proven | `ANALOG-BATTERY-CORRELATION.md:27-28` |
| 49 | `NRFX_GPIOTE_ENABLED 1` | Proven | GPIOTE cluster (`NORDIC-SDK-CORRELATION.md:700-724`) |
| 56-63 | `NRFX_TWIM0/1_ENABLED 1`, TWIM2/3 0, default frequency `0x06680000` (400 kHz), hold-bus 0, IRQ priority 2 | Proven (instances, freq) / Strong (prio) | `NORDIC-SDK-CORRELATION.md:639-660`; `IQS7211E-PROVIDER-BOUNDARY.md:115-119` |
| 68-73 | `NRFX_SPIM_ENABLED 1`, only SPIM2, `EXTENDED 0` | Proven | `NORDIC-SDK-CORRELATION.md:662-673` |
| 80-84 | legacy `TWI0/1` with EasyDMA (legacy `nrf_drv_twi` wraps `nrfx_twim`) | Proven | `twi_clear_bus` and tail-merged `nrf_drv_twi_init` (`NORDIC-SDK-CORRELATION.md:610-638`) |
| 85 | `NRF_CLOCK_ENABLED 1` (legacy `nrf_drv_clock`) | Proven | `nrf_drv_clock_init` `0x000788C8` |
| 4-5 | `SEGGER_RTT_CONFIG_BUFFER_SIZE_UP 512`, `MAX_NUM_UP_BUFFERS 2` | Proven | `NORDIC-SDK-CORRELATION.md:913-914`; `third-party/fetched/manifest.json` (`segger-rtt`) |
| 7 | `SEGGER_RTT_CONFIG_MAX_NUM_DOWN_BUFFERS 2` | Proven | same |
| 90, 93-94 | `BLE_ADVERTISING_ENABLED 1`; `NRF_BLE_GATT_ENABLED 1` | Proven | advertising closure; `nrf_ble_gatt` init `0x00078186` |
| 97-100 | `PEER_MANAGER_ENABLED 1`, `PM_FLASH_BUFFERS 4` (four-buffer PDB allocator), `PM_CENTRAL_ENABLED 0` | Proven / Strong | `NORDIC-SDK-CORRELATION.md:476-481`; no central role (`r1-capability-matrix.csv:201`) |
| 108 | `NRF_BLE_LESC_ENABLED 0` | Strong | security parameters: no LESC (`r1/docs/README.md:761-764`) |
| 111-115, 119 | `FDS_ENABLED 1`, `FDS_VIRTUAL_PAGES 3`, `FDS_VIRTUAL_PAGE_SIZE 1024` (words), `FDS_VIRTUAL_PAGES_RESERVED 36`, `FDS_BACKEND 2` (SoftDevice), `FDS_MAX_USERS 4` | Proven | `fds_init` `0x00063EB8`; four-user limit (`NORDIC-SDK-CORRELATION.md:448-466`) |
| 121, 125 | `NRF_FSTORAGE_ENABLED 1`, `NRF_FSTORAGE_SD_MAX_WRITE_SIZE 4096` | Proven | 4096-byte write chunking (`NORDIC-SDK-CORRELATION.md:456-460`) |
| 141-146 | `NRF_SDH_ENABLED 1`, `NRF_SDH_CLOCK_LF_SRC 0`, `RC_CTIV 16`, `RC_TEMP_CTIV 2`, `ACCURACY 1` | Proven | LF bytes `00 10 02 01` (`r1-capability-matrix.csv:201`) |
| 142 | `NRF_SDH_DISPATCH_MODEL 2` (polling) | Strong | stock BLE event poller `0x0007A38C`, 500-byte aligned buffer (`NORDIC-SDK-CORRELATION.md:413-415`) |
| 155-164 | `NRF_SDH_BLE_PERIPHERAL_LINK_COUNT 3`, `CENTRAL 0`, `TOTAL 3`, `GAP_EVENT_LENGTH 6`, `GATT_MAX_MTU_SIZE 247`, `GATTS_ATTR_TAB_SIZE 2048`, `VS_UUID_COUNT 2`, `SERVICE_CHANGED 1` | Proven | `r1-capability-matrix.csv:201` (R1-200) |
| 172 | `NRF_SDH_SOC_ENABLED 1` | Proven | `sd_evt_get` SoC observer (`NORDIC-SDK-CORRELATION.md:416-423`) |
| 11 | `NRF_SECTION_ITER_ENABLED 1` | Proven | `nrf_section_iter` linked |
| 128 | `NRF_SORTLIST_ENABLED 1` | Unverified | not function-proven |

**openR1 choices, unverified values, or known mismatches**

| Lines | Value | Status |
|---|---|---|
| 6 | `SEGGER_RTT_CONFIG_BUFFER_SIZE_DOWN 16` | **Wrong for stock.** Stock down buffer is 64 B (`NORDIC-SDK-CORRELATION.md:913`) |
| 8 | `SEGGER_RTT_CONFIG_DEFAULT_MODE 0` | Unverified |
| 10 | `NRF_LOG_ENABLED 0` | **Not stock.** Stock links the `nrf_log` frontend with RTT and serial backends and a `[RING]` prefix (`NORDIC-SDK-CORRELATION.md:15,402-405`) |
| 21-28 | RTC latency/reliable/log fields | Unverified defaults |
| 50-51 | `NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS 2`, GPIOTE IRQ priority 2 | Unverified. Stock uses low-power PORT events for seven inputs, so the count is likely larger |
| 74-75 | SPIM MISO pull 1, SPIM IRQ priority 2 | Unverified |
| 86-88 | clock observer priorities, `POWER_ENABLED 0`, `NRFX_POWER_ENABLED 0` | Unverified. Stock links `nrf_power_event_check/clear` (`NORDIC-SDK-CORRELATION.md:606-608`) |
| 91, 95, 101, 109 | observer priorities | Unverified |
| 98 | `PM_MAX_REGISTRANTS 3` | Unverified |
| 102-107 | `PM_RA_PROTECTION_*`, `PM_HANDLER_SEC_DELAY_MS 0` | Unverified (`auth_status_tracker` not function-proven) |
| 116-118 | `FDS_OP_QUEUE_SIZE 4`, FDS CRC flags 0 | Unverified |
| 122-124 | fstorage param check, SD queue 4, retries 8 | Unverified |
| 133-139 | all `APP_TIMER_*` | Unverified (`app_timer_freertos` not function-proven) |
| 147-153, 165-170, 173-178 | SDH observer levels and log fields | Unverified |
| 160 | `NRF_SDH_BLE_GAP_DATA_LENGTH 27` | Doubtful. Stock requests data length 251 through `nrf_ble_gatt` (`r1/docs/README.md:778`), and S140 sizing may use 251 |
| – | missing entirely | Stock also enables: `NRFX_TIMER` (TIMER2, TIMER4), `NRFX_PDM`, `NRFX_NFCT`, `NRF_PWR_MGMT` (no scheduler), `NRF_LOG` + backends, `NRF_BLE_QWR` (`MAX_ATTR 0`), `BLE_DFU` (buttonless, unbonded), `BLE_LINK_CTX_MANAGER`, `NRF_BALLOC`/`NRF_MEMOBJ`/`NRF_RINGBUF`, `NRF_FPRINTF`, `NRF_STRERROR`, plus the HVN TX queue size 4 (set via `sd_ble_cfg_set`, R1-200) |

## `FreeRTOSConfig.h`

Purpose: FreeRTOS 10.5.1 kernel + Nordic nRF52 port + CMSIS-RTOS2 v10.5.1 configuration.

| Lines | Value | Tag | Evidence |
|---|---|---|---|
| 9-11 | tick source RTC (`configTICK_SOURCE FREERTOS_USE_RTC`) | Strong | Nordic RTC port and tickless path (`NORDIC-SDK-CORRELATION.md:745-813`) |
| 15 | `configTICK_RATE_HZ 1024` | Proven | CMSIS wrapper evidence (`manifest.json` `arm-cmsis-freertos`) |
| 16 | `configMAX_PRIORITIES 56` | Proven | 56-priority validation in `cmsis_os2` |
| 17, 53 | `configMINIMAL_STACK_SIZE 256`, `configTIMER_TASK_STACK_DEPTH 256` | Proven | `FREERTOS-STATIC-MEMORY-CORRELATION.md:10-11,43-47` |
| 20, 22 | preemption 1, tickless idle 1 | Strong | `r1/docs/README.md:695-698` |
| 37-38 | static and dynamic allocation 1 | Proven | `vApplicationGet*TaskMemory` callbacks; `xTaskCreateStatic` and dynamic create in the image |
| 42 | `configCHECK_FOR_STACK_OVERFLOW 2` | Proven | `0xA5A5A5A5` four-word check (`FREERTOS-STACK-OVERFLOW-CORRELATION.md:22-25`) |
| 27-31 | mutexes, recursive mutexes, counting semaphores, task notifications | Strong | CMSIS wrapper call targets (`NORDIC-SDK-CORRELATION.md:793-804`) |
| 50 | `configUSE_TIMERS 1` | Proven | `prvReloadTimer` / `xTimerCreate` present |
| 24 | `configTOTAL_HEAP_SIZE 32768` | **Unverified** (openR1) | the stock `ucHeap` size is not recovered |
| 18 | `configMAX_TASK_NAME_LEN 16` | Unverified | – |
| 32 | `configQUEUE_REGISTRY_SIZE 2` | Unverified | – |
| 45 | `configUSE_TRACE_FACILITY 1` | Unverified | StaticTask_t is 112 B, which constrains trace/other options (`FREERTOS-STATIC-MEMORY-CORRELATION.md:40-41`) |
| 51-52 | timer task priority 40, timer queue length 32 | Unverified | – |
| 23, 25-26, 33-36, 39-49 | remaining `configUSE_*` switches | Unverified | – |
| 56-61 | `configUSE_OS2_*` | Unverified | – |
| 67-84 | `INCLUDE_*` | Unverified | – |
| 86-94 | `xTaskDelayUntil` prototype workaround | openR1 | compile workaround for a GCC/SDK mismatch; not stock |
| 96-99 | interrupt priority mapping (`_PRIO_APP_HIGH`) | Strong | Nordic port defaults |

## `cmb_user_cfg.h`

Purpose: CmBacktrace user configuration.

| Lines | Value | Tag | Evidence |
|---|---|---|---|
| 7-11 | OS FreeRTOS, CPU Cortex-M4, dump stack info, English | Proven | `CMBACKTRACE-CORRELATION.md:26-37` |
| 14-16 | `CMB_NAME_MAX 20`, `CMB_CALL_STACK_MAX_DEPTH 32`, `CMB_DUMP_STACK_DEPTH_SIZE 16` | Proven | same (`cm_backtrace_init` `0x000588A4`; `0x00081918`; `dump_stack` `0x0005CD14`) |
| 5, 18 | include `openr1_cmbacktrace_port.h`; `cmb_println → openr1_cmbacktrace_log` | openR1 | stock output path not recovered (probably Nordic log/RTT) |

Stock init receives the product build path, `603MV1.9.3` and `2.2.6.0009` (`CMBACKTRACE-CORRELATION.md:39-40`).

## `sdk-source-list.mk` (original `r1/platform/nrf52840/sdk/Makefile`)

Purpose: the openR1 GCC build of the application on SDK 17.1.0. Its `SRC_FILES`/`INC_FOLDERS`
list (lines 138-276) is the best existing seed for the stock link set. Unit-by-unit status against
stock is in `docs/toolchain-and-dependencies.md` section 4.

- **Stock-relevant**:
  - the SDK/FreeRTOS/CMSIS/CmBacktrace/BMA456/LIS2DW12/ST25DV/tiny-AES/FlashDB/FAL/Goodix
    democode units (lines 122-136, 139-209);
  - defines `NRF52840_XXAA FLOAT_ABI_HARD NRF_SD_BLE_API_VERSION=7 S140 SOFTDEVICE_PRESENT CONFIG_NFCT_PINS_AS_GPIOS CONFIG_GPIO_AS_PINRESET FREERTOS CMB_USER_CFG`
    (lines 280-288).
- **openR1**:
  - `OPENR1_SOURCES` (lines 33-113);
  - GCC startup and flags (lines 139-140, 278-310);
  - `-D__DATE__/__TIME__` pinning (line 295);
  - `-DOPENR1_*` (lines 281-283, 312-314);
  - `nano.specs`;
  - `../g2/third_party` borrowing (lines 29-31).
- **Missing stock units**: `arm_startup_nrf52840.s`, `nrf_log*`, `nrf_fprintf*`, `nrf_balloc`,
  `nrf_memobj`, `nrf_ringbuf`, `nrf_pwr_mgmt`, `ble_link_ctx_manager`, `ble_dfu`,
  `ble_dfu_unbonded`, `nrf_ble_qwr`, `nrf_dfu_svci`, `nrfx_nfct`, `nrfx_pdm`, `nrfx_timer`, and
  the binary-only vendor libraries.

## `openr1_sdk.ld`

Purpose: GCC linker script over Nordic `nrf_common.ld`.

- **Stock-proven**: `FLASH ORIGIN = 0x00027000`, `RAM ORIGIN = 0x200064A8` (line 7-8; R1-200,
  `research/decompilation/README.md:29`). The end of the application region before FDS
  (`0xD1000`) is Inferred from the FDS/FAL layout.
- **openR1**:
  - the lengths `0xAA000`/`0x39B58`;
  - every `.openr1_*` section and `KEEP` list (lines 21-117);
  - the CmBacktrace `PROVIDE` aliases (lines 121-125);
  - GNU `GROUP(-lgcc -lc -lnosys)`.

  Stock is linked by armlink with a scatter file (compressed RW, `__scatterload_decompress`), so
  this file cannot produce the stock layout.

## `fal_cfg.h`

Purpose: FAL 0.5.99 partition table for `device_flash`.

- **Stock-proven**:
  - the seven partition names, offsets and lengths, and the magic `0x45503130` (lines 12-20);
  - the device name `device_flash` (`INTERNAL-FLASH-CORRELATION.md:5-8,23-28`;
    `FLASHDB-FAL-CORRELATION.md:24`).
- **openR1**: `FAL_PRINTF` no-op, `FAL_DEBUG 0`, the symbol `r1_fal_flash_device` and the table
  macro spelling (lines 4-11). Stock `FAL_PRINTF`/debug routing is unknown; stock probably logs
  through Nordic logging.

## `fdb_cfg.h`

Purpose: FlashDB 2.0.0 configuration.

- **Stock-proven**: `FDB_USING_TSDB` and `FDB_USING_FAL_MODE` (lines 4-5). `health.db` is a TSDB,
  `_fdb_db_path` returns the FAL partition name, and there is no KVDB (`kv.bin` is R1 code)
  (`FLASHDB-FAL-CORRELATION.md:14-22`; `KV-STORE-CORRELATION.md:5-8`).
- **Inferred**: `FDB_WRITE_GRAN 32` (line 6). It matches nRF52840 word programming but is not
  image-pinned.
- **openR1**: `FDB_PRINT` no-op (line 7).

## `r1_recovered_config.h` (bootloader)

Purpose: force-included before Nordic's `pca10056_s140_ble` secure-bootloader `sdk_config.h`.

| Lines | Value | Tag | Evidence |
|---|---|---|---|
| 10-11 | `NRF_DFU_HW_VERSION 52`, `NRF_DFU_BLE_REQUIRES_BONDS 0` | Strong | `r1/research/bootloader-reconstruction/sdk-overlay/r1_sdk_overrides.h:9-10` |
| 19-22 | `NRF_SDH_CLOCK_LF_SRC 0`, `RC_CTIV 16`, `RC_TEMP_CTIV 2`, `ACCURACY 1` | Proven | bytes `00 10 02 01` at `0x000FDC68` |
| 24-27 | enter via GPREGRET and buttonless only | Strong | recovered bootloader config |
| 30 | `NRF_DFU_APP_DATA_AREA_SIZE (36*4096)` | Proven | retail two-byte delta at `0xFB54E` |
| 33-35 | `REQUIRE_SIGNED_APP_UPDATE 1`, `SINGLE_BANK 0`, `BL_APP_SIGNATURE_CHECK_REQUIRED 0` | Strong | SDK defaults kept explicit, consistent with behaviour (`SECURITY-MODEL.md:7-19`) |
| 38 | `NRF_BL_DEBUG_PORT_DISABLE 0` | Strong | tested ring had debug unprotected |
| 46-48 | `NRF_DFU_DEBUG_VERSION` when `R1_BUILD_PROFILE_CAPTURED` | Proven (behaviour is in stock) | `SECURITY-MODEL.md:33-38` |
| – | `R1_BUILD_PROFILE_*` switch mechanism | openR1 | a stock build simply defines `NRF_DFU_DEBUG_VERSION` |

Every other bootloader `sdk_config.h` value is inherited unchanged from the SDK 17.1.0 example.
That is Unverified against stock beyond what the BSim/name correlation implies.

## `r1_sdk_overrides.h` (bootloader overlay)

This is the same delta set as `r1_recovered_config.h`, minus the LF-clock lines. The LF-clock
omission is a known defect of this overlay; add lines 19-22 of `r1_recovered_config.h`.
`NRF_DFU_DEBUG_VERSION` is **off by default** here (`R1_REPRODUCE_CAPTURED_DEBUG_VALIDATION`,
lines 25-32), which is an openR1 hardening choice. Stock behaves as if it were on.

## `r1_dfu_public_key.c`

- **Proven**: the 64 bytes of `pk[]` (lines 13-22) are the raw P-256 key at `0x000FD868` of the
  live bootloader.
- **openR1**: the file text (alignment macro, comment). Stock uses SDK `dfu_public_key.c` form
  with `const uint8_t pk[64]`. The stock placement at `0xFD868` follows from armlink ordering, not
  from this file.

## `openr1_nrf52840.dts` / `openr1_nrf52840-pinctrl.dtsi` (pin reference only)

Purpose: Zephyr board files for the openR1 replacement runtime. They are kept only as a compact
pin reference; `docs/hardware-pinout.md` is authoritative.

- **Stock-proven pins** (`hardware-pinout.md`):
  - TWIM0 SDA P0.01 / SCL P0.12; TWIM1 SDA P0.14 / SCL P0.11 (pinctrl lines 5-31);
  - ADC AIN5/P0.29 1/2 40 µs, AIN3/P0.05 1/2 40 µs, AIN2/P0.04 1/6 10 µs, 12-bit (dts 71-105);
  - motion INT P0.15, touch LDO P0.30, touch RDY P0.17, NFC GPO P0.03, NFC enable P1.10, PMIC
    STACMD P1.01, optical INT P0.21, emitter P0.10, reset P1.04 (dts 26-41);
  - `gpio-as-nreset` (dts 43-45);
  - RTC2 prescaler 4095 (dts 57-61).
- **openR1 / not stock**:
  - the flash partitions (dts 125-155; only the `0xD4000`/`0x24000` data window mirrors stock);
  - `nfc-bus = <&i2c1>` (stock NFC is software `i2c_5`);
  - `GPIO_ACTIVE_HIGH` on touch RDY (stock active-low);
  - compatible strings, `chosen`, Zephyr settings partition, and the `low-power-enable` sleep
    states.
