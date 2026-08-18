# Goodix GH3X2X democode integration correlation

This note documents how the pinned Goodix GH3X2X democode is compiled into the openR1 host,
Nordic SDK, and source-built Zephyr images, which parts of the vendor tree are admitted, and how every external symbol
the admitted subset needs is satisfied. Evidence: the per-entry mapping
[`../boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md`](../boundaries/GOODIX-DEMO-DRIVER-MAPPING-2026-08.md)
(97 ledger entries mapped function-level onto this tree) and the `goodix-gh3x2x-democode` pin in
`third-party/fetched/manifest.json` (commit `2c0034a23b675a5f9a29e4a47e8b504c7a88e321`, archive
SHA-256 `48564d724f1de0004dd19ed3d8b156841400b7e652714f46dcb64d0397c76d29`, Goodix 5-clause
license; clause 4 restricts use to Goodix ICs — satisfied, the R1 ring contains the GH3x2x;
clause 5 forbids reverse-engineering the binary archives — they are never extracted, wrapped, or
linked).

## Admitted subset (compiled from the pinned tree, unmodified)

Consumed via `GOODIX_DEMOCODE_ROOT` (and passed to Zephyr as
`OPENR1_GOODIX_DEMOCODE_ROOT`); the tree itself is never edited.

- `demo_code/demo_kernel_code/driver/src/gh_drv_config.c`
- `demo_code/demo_kernel_code/driver/src/gh_drv_control.c`
- `demo_code/demo_kernel_code/driver/src/gh_drv_dump.c`
- `demo_code/demo_kernel_code/driver/src/gh_drv_interface.c`
- `demo_code/demo_kernel_code/kernel/gh_demo.c`
- `demo_code/demo_kernel_code/kernel/gh_demo_hook.c`
- `demo_code/demo_kernel_code/kernel/gh_demo_reg_array.c`
- `demo_code/demo_kernel_code/kernel/gh_demo_user.c`
- `demo_code/demo_kernel_code/module/gh_agc/gh_agc.c`
- `demo_code/demo_kernel_code/module/gh_other/gh_changeinttime.c`
- `demo_code/demo_kernel_code/module/gh_other/gh_movedetect.c`
- `demo_code/demo_kernel_code/module/gh_soft_adt/gh_multi_sen_pro.c`
- `algo_lib/algo_params/SPO2/goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c`
  (the config table whose tag matches the R1 firmware exactly)

Deliberately excluded:

- `algo_lib/*/*.a`, `drv_lib/*.a` — Armv8-M.mainline (STAR-MC1, FPv5) objects; cannot execute on
  the Cortex-M4F and are license-blocked from analysis.
- `demo_code/demo_algo_code/` — the algorithm-call layer; C source, but its global frame/result ABI
  depends on the absent algorithm archives. The corresponding recovered typed algorithm and
  `goodix_mem` bodies remain transparent local C rather than being replaced by those archives.
- `demo_code/demo_kernel_code/kernel/gh_demo_protocol.c` and `module/gh_protocol/` — the Goodix
  PC-tool upload protocol parser; excluded so the driver gains no external command surface.
- `module/gh_ecg/` — ECG front-end; the R1 ring has no ECG and the configuration disables it.
- `algo_lib/algo_params/SPO2/goodix_spo2_net_for_gh3x2x-v2.23_7ecd2a.c` — neural-network weights
  consumed only by the absent SPO2 library.
- `algo_lib/algo_params/{HR,HRV,NADT,ECG}` tables — consumed only by absent libraries.

## Configuration overlay

The stock democode configuration takes the FIFO read path
(`GH3X2X_ReadFifodata` / `GH3X2X_CheckRawdataBuf` / `GH3X2X_CalRawdataBuf`) from the binary DrvLib
archive. The R1 firmware contains these bodies compiled from `gh_drv_control.c` (mapped at
`0x0002AA10` and neighbors), so the build selects the all-source mode through
`r1/port/goodix_gh3x2x/config/gh_demo_config.h`, an `#include_next` overlay that sets
`__DRIVER_OPEN_ALL_SOURCE__` to 1 after chaining to the pinned vendor configuration. Only
`driver/src/gh_drv_control.c` reads that macro, and its directory has no sibling
`gh_demo_config.h`, so the include-path overlay is sufficient and the vendor file stays untouched.
The interface stays on I2C at device base `0x28` (`GH3X2X_I2C_ID_SEL_1L0L`), exactly as recovered.

The democode version strings embed `__DATE__`/`__TIME__`; both target builds pin them
(`-D__DATE__="Aug 14 2026" -D__TIME__="00:00:00"` with `-Wno-builtin-macro-redefined`) so the
unsigned target code remains deterministic.

## External-symbol classification

The subset was compiled for the host and for the target; every undefined symbol it produces is
accounted for below.

### (a) Supplied by the subset

All driver control/config/dump/interface entry points (`GH3X2X_Init`, `GH3X2X_CommunicateConfirm`,
`GH3X2X_RegisterI2cOperationFunc`, `GH3X2X_StartSampling`/`GH3X2X_StopSampling`,
`GH3X2X_ReadFifodata`, the virtual-reg config write path, …), the demo kernel
(`Gh3x2xDemoInit`, `Gh3x2xDemoStartSampling(Inner)`, `Gh3x2xDemoStopSampling`,
`Gh3x2xDemoArrayCfgSwitch`, `Gh3x2xDemoInterruptProcess`, …), the soft-AGC / move-detect /
soft-ADT modules, the `hal_*` template wrappers in `gh_demo_user.c`, all driver state globals, and
the SPO2 config table (`goodix_spo2_config_get_instance/_get_size/_get_version`, `external_cfg`).

### (b) Supplied by the R1 port (`r1/port/goodix_gh3x2x/`)

| Symbol | Role |
| --- | --- |
| `gh3026_i2c_init` / `gh3026_i2c_write` / `gh3026_i2c_read` | I2C board hooks expected by `gh_demo_user.c`; forwarded to the bound `r1_gh3x2x_hal` bus ops |
| `gh3026_int_pin_init` / `gh3026_reset_pin_init` / `gh3026_reset_pin_ctrl` | INT/reset pin board hooks |
| `gh3026_gsensor_data_get` | accelerometer feed for the FIFO alignment path |
| `delay_us` | microsecond delay used by driver timing |
| `gh3x2x_print_fmt` | log sink; the port forwards the format text only and never formats varargs (no C library on the freestanding target) |
| `gh3x2x_rawdata_notify` / `gh3x2x_wear_evt_notify` | raw-frame and wear-state notification sinks |
| `Gh3x2xPoolIsNotEnough` | `goodix_mem` integrator surface declared by `goodix_mem.h`; bridges to the existing `r1_goodix_pool_not_enough` glue (the `void(void)` seam carries no `info1`, so 0 is recorded) |

`r1_gh3x2x_port.c` is R1-authored, vendor-header-free, and freestanding-safe (explicit loops, no
`string.h`); it is part of the strict-flag host build, the sanitizer build, and `arm-objects`.
Unbound or partially bound HALs fail closed: I2C reads return a zeroed buffer, so the driver's own
magic-value checks (0xAA55 communicate-confirm, register verify) fail instead of consuming
fabricated data. `r1_gh3x2x_bind.c` adapts the kernel entry points to the existing
`r1_goodix_provider_ops` seam (0 == success / nonzero == failure, matching `GH3X2X_RET_OK` vs the
negative democode codes); `Gh3x2xDemoStartSampling`/`Gh3x2xDemoStopSampling` return `void`
upstream, and driver-level failures already surface through `Gh3x2xDemoInit`.

### (c) Checked democode algorithm ABI and excluded protocol ABI

Implemented in `r1/port/goodix_gh3x2x/r1_gh3x2x_stubs.c` with vendor headers included so the
signatures are checked against the real prototypes. The R1-owned, vendor-header-free provider
contract lives in `r1_gh3x2x_algo_bridge.h`. It normalizes the 20 function IDs, channel/sample
metadata, raw/AGC/flag pointers, three motion axes, and frame counter into a bounded frame view.
The pinned headers are now compile-time checked against the provider-independent offsets
`HR=1`, `HRV=2`, and `SpO2=6`; this closes an earlier bridge defect that labeled HR as row zero.
Provider output is admitted only when the update flag, 16-bit result mask, population count, and
fixed 16-word payload agree. An unbound, unsupported, malformed, or uninitialized provider still
fails closed with the democode's own error family. Init rollback, repeated init, per-function
deinit, version, sensor-enable, and algorithm virtual-register writes route through the copy-bound
provider table. A separately bound observer runs only after an updated result has passed all of
those checks and has been copied into the vendor result record; rejected and non-updated results
are never observed. No bridge function fabricates sensor or biometric data.

The same checked layer reproduces all three recovered outer-input ABIs before algorithm state is
invoked. `0x0002C944` is HR/HBA and applies its 12-slot map. `0x0002CAD8` is HRV and copies the
first four raw/AGC words plus the last accepted HR. `0x0002CFE8` is SpO2 and applies its separate
12-slot map while deriving gain and drive-current values from each mapped AGC word. All three
preserve the low frame-counter byte, four-channel marker, sleep flag, 24-bit marker, chip/data
constants, signed raw-word bit patterns, and three motion axes; failure leaves the destination
unchanged. `r1_gh3x2x_primitive_adapter.h` exposes borrowed bounded views as
`goodix_primitives_hba_process_input`, `goodix_primitives_hrv_process_input`, and
`goodix_primitives_spo2_calc_input`. Retail roots are correspondingly identified as HBA
`0x0006C6A8`, HRV `0x0006D51C`, and SpO2 `0x0006E838`.
The default SpO2 lane map is also local and exact: recovered initializer `0x0002ACF4` first fills
all 32 private lanes with `0xFF`, then writes source `1` at private map index 8 and source `0` at
index 16. Flattened into the three four-lane groups consumed by `0x0002CFE8`, that is
`{FF,FF,FF,FF, 1,FF,FF,FF, 0,FF,FF,FF}`. The bridge exposes a checked copy of this map and does
not depend on the former RAM object at `0x20030227`. The HBA initializer `0x0002A630` separately
produces `{0,1,2,3, FF,FF,FF,FF, FF,FF,FF,FF}` at `0x20030204`.

Two previously source-routed but unlinked initializer inputs are now retained too. Retail ROM
`0x000AD13C..<0x000AD160` is the exact 36-byte public Exclusive HR configuration:
mode 0, 25 Hz, four valid channels, output limits 9/20, sigma 1, raw scale 202, delay 5, and score
scale 1. Retail ROM `0x0009D5EC..<0x0009D604` is the exact 24-byte public HRV configuration:
interpolation enabled, 100 Hz, and acceleration thresholds 200000/100000/30000/30000. The pinned
`goodix_hba_config.c` and `goodix_hrv_config.c` now compile into both targets, their objects have
nonempty retained spans, and the host integration test checks every field. This admits transparent
configuration data only.

`r1_gh3x2x_provider_composer.c` now owns the exact recovered outer-wrapper composition shared by
both targets. It admits only complete HBA, HRV, and SpO2 root bindings; constructs each root's
distinct normalized input; publishes HR with mask `0x003F`/six words and HRV with mask
`0x007F`/six written words plus a zero seventh slot; and preserves the HR wrapper's
accepted-heart-rate carry into HRV after the HRV initializer resets it. For SpO2 it deliberately
follows the retail R1 divergence at `0x0002D14A`, not the public democode: mask `0x00FF`, six
distinct written words, word 0 mirrored into slot 6, and the cleared slot 7 retained as zero.
Repeated init, process-before-init, malformed row masks, incomplete roots, and unsupported rows all
fail closed. `r1_gh3x2x_reconstructed_roots.c` supplies complete composer bindings for the three
canonical recovered roots. It converts the normalized records into the existing bounded primitive
inputs, invokes HBA `0x0006C6A8`, HRV `0x0006D51C`, and SpO2 `0x0006E838`, routes their exact
recovered version identities, and implements the private-to-public HBA and SpO2 result layouts.
The SpO2 executor accepts only retail statuses 0, 3, and 4, gates publication on private word 12,
applies the recovered `/10000` epsilon-aware rounding to word 0, and selects private words
`{0,11,2,1,4,6}`. Each executor requires caller-owned plan, state, workspace, and lifecycle
bindings. Zephyr now owns and binds those initializer-derived persistent objects for HBA, HRV, and
SpO2; incomplete compositions remain rejected by the shared composer.

All inventoried Goodix executable bodies and generated-model data compile from transparent local
source and are retained in the Nordic image. On Zephyr, the independent observer now narrows the
public HR words `{hba_out, valid_score, valid_level}` and the six public SpO2 words into the exact
recovered R1 result records. It runs the bounded one-shot planners and their exact scalar storage
consumers only while the `dev_info` global-health bit is enabled. The exact seven-slot authorization
union opens HR, HRV, and the observer-only HSM raw source only for slots whose recovered dependency
masks request them. HSM forwards the checked first raw frame word and never fabricates a result.

| ABI surface | Behavior | Remaining boundary |
| --- | --- | --- |
| `GH3X2X_AlgoInit` / `GH3X2X_AlgoDeinit` / `GH3X2X_AlgoCalculate` | validate the function bitmap and frame globals, then dispatch through the normalized provider; the retained composer and target-bound reconstructed-root executors reproduce all three outer-wrapper and root-call contracts; mixed-mask initialization rolls back earlier roots on a later failure; HSM is observer-only | physical equivalence and long-run state behavior require owned-hardware validation |
| `GH3X2X_AlgoSensorEnable` | routes the three boolean sensor dependencies to the bound provider | no effect while unbound |
| `GH3X2X_AlgoVersion` / `GH3X2X_GetVersion` | algorithm versions route per function and fall back to `no_ver`; protocol aggregate getter stays `no_ver` | the protocol version getter belongs to the excluded PC-tool protocol |
| `GH3X2X_AlgoCallConfigInit` / `GH3X2X_WriteAlgConfigWithVirtualReg` | captures the real 20-row frame table and routes virtual-register writes to the provider; hardware register windows below `0x3000` remain applied by the compiled driver | provider decides which algorithm registers it proves and accepts |
| `GH3X2X_TimestampSync{AccInit,PpgInit,SetPpgIntFlag,FillAccSyncBuffer,FillPpgSyncBuffer}` | no-op | ACC/PPG synchronization has not yet been adapted to the typed reconstructed stream state |
| `GH3X2X_TimestampSyncGetFrameDataFlag` | returns 1 | exact matched public-democode and recovered `0x0002AE00` behavior |
| `GH3X2X_UprotocolPacketFormat` | returns 0 (zero-length packet) | PC-tool upload protocol excluded — no external command surface |
| `Gh2x2xUploadDataToMaster` / `Gh3x2xDemoSendProtocolData` | drop payloads | same |

### Toolchain residue

`memcpy`/`memset`/`memmove`/`strlen`/`snprintf`/`bzero`/`atan` resolve to the C library (newlib
nano in the SDK image, which links `-lc -lm`). The R1-authored port itself makes no C library
calls.

## Reachability and boot behavior

The legacy Nordic SDK target still retains the provider without board operations or a command
route. The source-built Zephyr target now binds the acquisition transport and lifecycle from
transparent source. It uses the recovered software `i2c_4` engine on SCL P1.09 and SDA P0.31,
keeps the Goodix eight-bit device ID `0x28`, converts the two command bytes to a big-endian
16-bit register for reads, and forwards writes exactly as the democode supplied them. P0.21 is
the falling-edge interrupt, P0.10 controls the emitter, and P1.04 controls reset. The interrupt
handler schedules a worker that calls `Gh3x2xDemoInterruptProcess`; motion FIFO samples can feed
the public democode alignment callback. Board preparation acquires YHM2710 optical client bit 1,
and shutdown disables the interrupt, releases the software bus pins, deasserts emitter/reset,
and releases the lease.

Zephyr startup only installs those source bindings and configures emitter/reset inactive. It does
not acquire the rail, initialize the chip, or start sampling. Start/switch/stop remain retained
typed platform APIs with no BLE or other wire command route. Raw-frame notifications increment a
diagnostic count; they are not interpreted as HR, SpO2, HRV, or any other biometric result. The
democode global ABI itself is normalized and checked, but no target biometric provider is bound
yet, so those function rows remain resource-unavailable and hardware-register/raw-acquisition
work cannot silently fabricate health output. The target nevertheless binds the result observer
after the optical adapter, restores the persisted health-enable bit and timestamp, and has complete
HR/SpO2 result-plan-to-hourly-cache plumbing ready for a future admitted provider. The HRV scalar
consumer is retained but deliberately has no live producer.

## Verification

- `make -C r1 vendor-goodix-test GOODIX_DEMOCODE_ROOT=...` compiles the subset plus port for the
  host and runs `tests/test_vendor_goodix.c`: port bind/unbind and fail-closed paths, HAL
  translation through the compiled driver (device id `0x28`, big-endian register wire format,
  read-modify-write bit fields, communicate-confirm magic and restore), democode-to-R1 error
  mapping, unbound failure behavior, normalized frame/lifecycle/version/register dispatch,
  exact function-offset agreement, all three recovered input constructors, direct transparent-
  primitive views, exact composer lifecycle/masks/publication/HR carry, validated-result observer
  ordering, malformed-result non-observation, excluded protocol hooks,
  the pool glue, and an end-to-end `Gh3x2xDemoInit` +
  start/stop-sampling run against a fake I2C register file. No hardware required. The port is
  additionally covered under ASan/UBSan by the strict `sanitize` build; the vendor subset itself
  carries two pre-existing UBSan findings (`1 << 31` shifts at `gh_drv_control.c:3696` and
  `:3789`) that ship in the upstream source and are not introduced by this port.
- `make -C r1 arm-objects` compiles `r1_gh3x2x_port.c` and the provider composer freestanding for
  Cortex-M4F with clang under the project's strict flags; `provider-composer-check` also applies the
  strict host warning set before the vendor-democode integration test.
- `make -C r1 sdk-image ... GOODIX_DEMOCODE_ROOT=...` links the subset into
  `openr1_nrf52840_s140`; `tools/verify_sdk_image.py` pins the resulting size and SHA-256 digests
  and requires the democode objects and key symbols (`GH3X2X_Init`,
  `GH3X2X_RegisterI2cOperationFunc`, `GH3X2X_ReadFifodata`, `Gh3x2xDemoStartSampling`,
  `Gh3x2xPoolIsNotEnough`, the stub names, …) in the map.
- `make -C r1 zephyr-bundle ... GOODIX_DEMOCODE_ROOT=...` hash-gates the 59-file admitted
  source/header/license set, compiles 15 upstream translation units (including byte-matched HR,
  HRV, and SpO2 configuration inputs) plus the four local port/bind/composer/checked-bridge units,
  and requires nonempty loadable spans for all 19 objects. The offline
  source-boundary verifier also pins the software-`i2c_4` pins, device ID, devicetree GPIOs,
  YHM client, interrupt worker, startup order, no-boot-sampling rule, and bounded normalized algorithm ABI.
