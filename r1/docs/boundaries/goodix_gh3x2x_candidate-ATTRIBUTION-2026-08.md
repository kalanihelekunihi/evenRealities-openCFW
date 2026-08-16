# Attribution re-examination — goodix_gh3x2x_candidate (2026-08)

> Historical attribution audit. Its binary-library findings remain provenance evidence and the
> vendor archives remain excluded from production. The implementation gate was later superseded
> by the owner-authorized transparent-C Goodix reduction and source-admitted model data.

## Family

499 functions / 79,948 bytes, all `vendor_source_required_not_redistributable`. Embedded version
markers: `GH(M)3X2X_DEMO_v1.6_AC_v0.5(build:Jul  9 2026_21:49:08)` @ `0x0002A560`,
`v4.3.0.0 (build:Jul  9 2026_21:49:07)` @ `0x0002A59C`,
`Gh3x2x_Virtual_Reg_v3.4` @ `0x0002A62C` (the ledger string "`pGGh3x2x_...`" is a `strings(1)`
artifact — `pG` is the preceding `bx lr` (`0x4770`); the true string starts at `Gh3x2x_`), and
config tag `gh3x2x-v2.23_7ecd2a` @ `0x0006A028` (file offsets `0x3560`/`0x359c`/`0x362c`/`0x43028`
in `rebuilt-application.bin`, load base `0x27000`).

## Public upstream located

`github.com/coredevices/pebbleos-nonfree`, path `gh3x2x/` (created 2025-06-19; vendored in commit
`f0122d9256` "gh3x2x: add vendor binary blobs and demo code", 2025-09-26). This tree is the Goodix
GH3X2X SDK with **version markers exactly matching the R1 firmware**:

| Marker | R1 firmware | pebbleos-nonfree `gh3x2x/` |
| --- | --- | --- |
| Democode | `GH(M)3X2X_DEMO_v1.6_AC_v0.5` | `gh_demo_version.h`: MAJOR 1 / MINOR 6; `gh3x2x_demo_algo_call_version.h`: MAJOR 0 / MINOR 5 → `_AC_v0.5` |
| DrvLib | `v4.3.0.0` | `gh_drv_version.h`: `4.3.0.0` (changelog: `2024-12-27 v4.3.0.0`; `2023-05-16 v4.2.0.0 1.open source`) |
| Virtual-reg | `Gh3x2x_Virtual_Reg_v3.4` | `GH3X2X_GetVirtualRegVersion()` machinery in `demo_kernel_code/driver/src/gh_drv_config.c` (string itself is tool-generated per config array; matches Goodix developer-forum traces) |
| Config tag | `gh3x2x-v2.23_7ecd2a` | `algo_lib/algo_params/SPO2/goodix_spo2_config_for_gh3x2x-v2.23_7ecd2a.c` — identical tag |

The tree splits into: **source** (`demo_code/demo_kernel_code/{kernel,driver}`,
`demo_code/demo_algo_code/*`, `demo_code/demo_mp_code/*`) and **binary-only archives**
(`algo_lib/{COMMON_DL,COMMON_DSP,HR,HRV,NADT,SPO2}/*.a`, `drv_lib/libarm-none-eabi-gcc-softfp-Os-gh_common.a`).

License: `gh3x2x/LICENSE`, © 2025 Shenzhen Goodix — 5-clause BSD-style. Redistribution in source
form is expressly permitted with notice retention; **clause 4: "must only be used with a Goodix
integrated circuit"**; **clause 5: binary-form software "must not be reverse engineered,
decompiled, modified and/or disassembled"** (this is the license the sensor-algorithm-heap boundary
doc already characterized). Source files carry `© 2003-2022 Goodix` headers. Nothing indicates a
leak: CoreDevices ships GH3x2x-based products, the license file accompanies the code, and the
driver's own changelog records a Goodix "open source" release at v4.2.0.0. Goodix's own GitHub org
(`goodix-ble`, 21 repos checked) publishes only GR5xxx BLE SDKs — no gh3x2x; Goodix's official
channel (goodix.com `software_tool/gh3x2x_driver`) is registration-gated.

Second candidate: `github.com/linhui200699/ats3089`, path
`zephyr/framework/sensor/sensor_algo/SensorAlgoHR_GH3x2x_V4200/` — a V4200 (DrvLib v4.2.0.0-era)
SDK copy. **No license anywhere** (repo license API: 404; headers are "All rights reserved" only),
version-skewed, presumptive leak. It unblocks nothing and was not used as evidence.

## Stratification (499 entries)

| Stratum | Entries | Bytes | Layer | Verdict |
| --- | ---: | ---: | --- | --- |
| S1 closed algorithm libs (NADT 91, SPO2/dlCom+neural 101, HR 40, HRV 9) | 241 | 57,674 | `algo_lib/*.a` — binary-only even publicly | **stay blocked** (license clause 5 bars RE of the binary libs; no source exists) |
| S2 `goodix_mem`/`GdMem` allocator internals (12) + guarded alloc/free glue (35) | 47 | 2,738 | `gh_common`/`common_dsp` .a — binary-only | **stay blocked** (provenance already resolved by SENSOR-ALGORITHM-HEAP doc; license unchanged) |
| S3 demo kernel layer (Gh3x2xDemo*, MultiSensor, config search/switch/slot, sampling control, demo state inits) | 23 | 4,760 | public source `demo_code/demo_kernel_code/kernel/` | **re-attributable as a layer** (see matches) |
| S4 driver layer (init, I2C/SPI registration, reg-write dispatch, virtual-reg/profile decode, config-table load, rawdata/channel decode, gsensor cache) | 28 | 3,644 | public source `demo_code/demo_kernel_code/driver/` | **re-attributable as a layer** (see matches) |
| S5 unresolved: 116-entry frozen closure residue, generic thunks/stubs, fixed-point/median helpers | 160 | 12,372 | mixed/unknown | **stay blocked** pending per-entry mapping (existing boundary doc already holds tiny non-unique thunks in the gate) |

S3/S4 boundary is evidence-text-based and approximate at the edges (e.g. `0x0002A380`
communicate-confirm is driver, not demo; the five packed-24-bit integrity helpers sit between
driver rawdata packing and common lib). Counts should be treated as ±a few entries.

## Function-level matches verified (S3/S4)

| R1 address | Upstream function (pebbleos-nonfree path) | Evidence |
| --- | --- | --- |
| `0x0002A55C` | `GH3X2X_GetDemoVersion` — `demo_kernel_code/kernel/gh_demo.c:1281` | body is `adr r0,[0x2a560]; bx lr` → returns `"GH(M)3X2X_DEMO_v1.6_AC_v0.5(build:…)"`; source: `return GH3X2X_DEMO_VERSION_STRING;` built from the same macros |
| `0x0002A598` | `GH3X2X_GetDriverLibVersion` — `demo_kernel_code/driver/src/gh_drv_control.c:2208` | `adr r0,[0x2a59c]; bx lr` → returns `"v4.3.0.0 (build:…)"`; source: `return (GCHAR*)GH3X2X_VERSION_STRING;` |
| `0x0002D87C` | `Gh3x2xDemoInit` version-report block — `gh_demo.c:1512-1518` | calls `0x2A55C`/`0x2A598` (bl sites `0x2D89A/0x2D8B6/0x2D8D0/0x2D8EC`) emitting the exact `Democode Version`/`DrvLib Version`/`Config Version` log topology of the public function, incl. `GH3X2X_GetVirtualRegVersion()` |
| `0x0002E358` | `Gh3x2xDemoStartSampling` — `gh_demo.c:3137` | tail: `FUN_0002e36c(param_1,0); FUN_0002e340(param_1);` ≡ `Gh3x2xDemoStartSamplingInner(unFuncMode,0); Gh3x2xDemoStartAlgoInner(unFuncMode);` |
| `0x0002E36C` | `Gh3x2xDemoStartSamplingInner` — `gh_demo.c:2951` | full structural match: log `"[Gh3x2xDemoStartSampling] unFuncMode = 0x%x"`; `if(mode==1) t=1; else t=mode&0xFFFFFFFE` ≡ `~GH3X2X_FUNCTION_ADT`; `(t & ~cur)!=0` ≡ `(t&cur)!=t`; switch-enable branch logs `"Cfg Error:Reg cfg file not exist!!!APP mode:0x%x"` then `while(1)`; else `Gh3x2xDemoSearchCfgListByFunc(&idx,mode,1)` (`0x2C2EC`), `Gh3x2xDemoSamplingControl(0xFFFFFFFF,STOP)` (`0x2E0D0`), hard reset (`0x2ACCC`), `BspDelayMs(15)` (`0x2EB34` w/ 0xf), `GH3X2X_Init(arr+idx)` (`0x2A754`), ADT-recovery block with the two exact log strings, `GH3X2X_FunctionStart` (`0x2A4B4`), `GH3X2X_EnterLowPowerMode` (`0x2A328`), error log `"APP Mode Switch Error:…"`, then `Gh3x2xFunctionSlotBitInit` (`0x2E7A4`) and `Gh3x2xDemoSamplingControl(mode,START)` |
| `0x0002AAF8` | `GH3X2X_RegisterI2cOperationFunc` — `demo_kernel_code/driver/src/gh_drv_interface.c:849` | exact: checks `param2 && param3 && param1 < GH3X2X_I2C_ID_INVALID(4)`; stores `(sel<<1)\|0x28` = `GH3X2X_I2C_DEVICE_ID_BASE\|(sel<<1)` (confirms base 0x28 and that the R1 ring wires the GH3x2x on **I2C**, not SPI); then 2 registered callbacks + 5 internal op pointers (I2cSendCmd/WriteReg/ReadReg/ReadRegs/ReadFifo); returns -2/0. Ledger label "SPI-operation registration" is the sibling API; the R1 body is the I2C variant |
| `0x0002A754` | `GH3X2X_Init` — `demo_kernel_code/driver/src/gh_drv_control.c:527` | exact sequence: config-init (`0x29CC0`), `GH3X2X_CommunicateConfirm` (`0x2A214`, →-4 on fail), `WriteReg(0x508,0x7FFF)` = `INT_STR_REG_ADDR/MSK_ALL_BIT`, `pusPmuFifoModuleCtrlVal[chipIdx]=ReadReg(0x88)` = `PMU_CTRL4_REG_ADDR`, `GH3X2X_LoadNewRegConfigArr(cfg,len,0,&agc)` (`0x2A8DC`, 4-arg signature exact), `WriteReg(0x700,0x20/0x30)`, `while(!(ReadReg(0x718)&1))`, `ReadReg(0x712)`→`SetDrvEcode`, init-hook call, `SET_CHIP_INIED`. **Divergence:** R1 adds `WriteReg(0x72, ReadReg(0x72)\|0x11)` in the source's "@ fix chip error code below here" slot — a chip-errata patch absent from the public v4.3.0.0 tree (Even's build carries a Goodix errata fix or a slightly newer internal revision) |
| `0x0002A8DC` | `GH3X2X_LoadNewRegConfigArr` — `gh_drv_config.c:776` | callee of the above with matching 4-arg ABI `(arr, len, chipIndex=0, agc*)`; the `0x2AEDC` "0x3000-windowed register write dispatcher" is the real-vs-virtual register split (`GH3X2X_GET_BIT_IS_SET(usRegAddr)`, virtual regs at 0x3000+) inside it |

Match standard: control-flow + constants + log-string topology, not byte-identity (the public
source was not recompiled; the R1 app was built with Even's toolchain, build stamp Jul 9 2026).

## License assessment

- **Demo/driver source (S3/S4):** redistributable under the Goodix 5-clause license in
  `gh3x2x/LICENSE`. Clause 4 (Goodix-IC-only use) is satisfied in context — the code operates the
  GH3x2x sensor IC inside the ring; a host-side openCFW redistribution should be reviewed against
  clause 4 before relying on it (the ring does contain the Goodix IC, so the use case fits).
  Re-attribution pointer: `coredevices/pebbleos-nonfree @ gh3x2x/demo_code/`, Goodix GH3X2X
  democode v1.6 / algo-call v0.5 / DrvLib v4.3.0.0 / Virtual_Reg v3.4 / config
  `gh3x2x-v2.23_7ecd2a`, license `gh3x2x/LICENSE` (Goodix 5-clause). Note CoreDevices carries
  local patches (commits `dca93b6981` "patch demo code", `13c77dacb3` "update library"); the
  pristine Goodix origin is the v4.3.0.0 (2024-12-27) release behind the same changelog.
- **Algorithm libraries (S1) and allocator (S2):** binary-only in the public mirror; license
  clause 5 prohibits reverse engineering of binary forms; no source is publicly available.
  Unchanged: blocked.
- **ats3089 V4200 copy:** no license grant; presumptive leak; not evidence, unblocks nothing.

## Verdict

- **Re-attributable (layer-level): 51 entries** (S3 23 + S4 28, 8,404 bytes) → Goodix GH3X2X
  democode/driver v1.6/AC v0.5/v4.3.0.0 at `coredevices/pebbleos-nonfree:gh3x2x/demo_code/`
  (Goodix 5-clause license). Function-level identity is proven for the 8 bodies in the match
  table; the remaining ~43 entries in S3/S4 should be mapped per-entry against the same source
  files before any ledger flip, and the ledger should record the clause-4 review.
- **Stay blocked: 448 entries** (S1 241 + S2 47 + S5 160) — closed algorithm libraries,
  binary-only allocator, and the unresolved closure/stub residue.

## Addendum: per-entry mapping completed (2026-08)

The recommended per-entry mapping pass is complete:
[`GOODIX-DEMO-DRIVER-MAPPING-2026-08.md`](GOODIX-DEMO-DRIVER-MAPPING-2026-08.md) maps all 499
entries across two passes and verifies 168 MATCHED bodies against the pinned upstream snapshot
`coredevices/pebbleos-nonfree @ 2c0034a2` — including the entire soft-AGC module, the
algo-call layer, and the driver/demo/kernel strata. The ownership ledger now routes those 168
entries to provider family `goodix_gh3x2x_democode_v1_6_drvlib_v4_3_0_0` with disposition
`use_pinned_upstream`, and six Even/Bravechip-authored glue bodies to
`r1_goodix_provider_adapter`. The remaining 325 entries stay
`vendor_source_required_not_redistributable`: 243 closed algorithm-library (binary-only,
license clause 5), 53 `goodix_mem` allocator/apparatus, and 29 unresolved residues
(non-unique stubs, HRNet accessor residues for an absent net, and closed-lib-closure helpers
whose origin is unprovable from public material).

A residual re-audit of those 29 entries (same snapshot, same match standard; see the mapping
doc's "Residual re-audit 2026-08-14" section) flipped six more entries to the democode
provider — `goodix_hba_init_func`, `goodix_hba_config_get_arr`, `get_knWeightsArr_addr`,
`GhDrvConfigManagerGetCurFunctionSupprort`, `Gh3x2x_UserHandleCurrentInfo`, and
`Gh2x2xUploadDataToMaster` — and confirmed the closed-lib identity of `goodix_hba_init`
(stays gated). New totals: 174 MATCHED, 319 gated (243 S1, 53 S2, 23 unresolved).
