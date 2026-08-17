# Withheld-provider re-attribution audit — GoMore / YHM2710 / GXT310 / QMA6100 (2026-08)

> Historical attribution audit. All four implementation gates were superseded by owner-authorized
> transparent-C reductions: all 362 GoMore entries, all 44 YHM2710 entries, all eight GXT310
> entries, and all 17 QMA6100 provider/adapter entries now compile locally. The source-lineage and
> license findings below remain evidence; no unlicensed package is used as production source.

## Scope and rule

Final re-attribution audit of the four ledger families withheld as
`vendor_source_required_not_redistributable` (or equivalent): 362
`gomore_health_algorithm_candidate`, 36 `yhmicros_yhm2710_candidate`, 5
`gxcas_gxt310_candidate`, and 3 `qst_qma6100_v1_0_lineage_unlicensed` functions.
The question per family: does any *publicly available* source match at the code
level (constants, structure, naming, strings), or at least document the hardware
publicly (datasheet/register map)? Generic algorithmic similarity (e.g. RMSSD
HRV math, Cole-Kripke actigraphy) does not authorize attribution and was not
treated as evidence. No ledger CSVs, generator scripts, existing boundary docs,
or source code were modified; this report is the only new artifact.

Tools used: GitHub authenticated code/repo search (`gh`), Gitee/web search,
direct retrieval of vendor archives, and body-level comparison against
`r1/research/decompilation/application/decompiler-output.c` and
`r1/research/decompilation/rebuild/rebuilt-application.bin` (base `0x27000`).

---

## 1. GoMore health-algorithm cluster (362 functions)

### Hypotheses tested

- **H1 — Public GoMore Inc. source (GitHub/Gitee/official SDK): NO MATCH.**
  GoMore Inc. (Taipei, a.k.a. Bomdic/博晶醫電) is a licensing-only algorithm
  vendor (OnePlus Watch, CISS partnerships; gomore.me). `github.com/gomore` is an
  unrelated Clojure/web shop (ring-gzip-middleware etc.), not the health company.
  No official public SDK, no source, no licensed headers exist on any code host
  searched (GitHub code/repo search for `gomore` API names; web/Gitee searches).
- **H2 — Bravechip `ChipletRing-APPSDK` bundles native GoMore material: NEGATIVE.**
  Full recursive tree of `github.com/BravechipSpace/ChipletRing-APPSDK` (HEAD,
  2026-08) contains only app-side wrappers: `Android/.../GoMoreSleepActivity.java`
  (imports `com.lm.sdk.mode.GoMoreSleep`, `IGoMoreListener` from Bravechip's
  closed `LmAPI` AAR) and iOS `GoMore*Config_Dialog.swift` /
  `GoMoreFunction_Module.swift`. No C/C++ source, no headers, no `.a`/`.so`
  GoMore artifacts anywhere in the repo. The Bravechip org has only one other
  repo (a `react` fork). It confirms Bravechip *ships* GoMore on its rings
  (release note "合并gomore睡眠") but contributes no provider source pointer.
- **H3 — Third-party firmware leaks of the GoMore embedded SDK: FOUND (unlicensed).**
  `github.com/zhengzhengchuang/umeox_JL701n_128_lvgl_watch` and its sibling
  `..._hw_v1.1` (Jieli BR28 smartwatch SDK dumps, repo license: none) ship
  GoMore's embedded SDK under `code/sdk/`:
  - `apps/common/ui/lv_watch/comm_func/GoMoreLib.h` — a GoMore HAL header
    (include guard `__GoMoreAlgoHal__`) declaring `setAuthParameters`,
    `getWellnessVersion`, `getReleaseVersion`, `getPreviousDataSize`,
    `getMemSizeHealthFrame`, `healthIndexInitUser`, `updateIndex`,
    `stopHealthSession`, `switchMode`, `setSleepConfig`/`getSleepConfig`,
    `startSleepPeriod`, `endSleepPeriod`, `getEmbeddedSleepSummary`,
    `gomore_pkey_get`, `gomore_device_id_get`.
  - `GoMoreLibStruct.h` (guard `__GoMoreAlgoHalStruct__`) — the `IndexIO` /
    auth struct layouts; `gomore_func.c` — integration glue calling
    `healthIndexInitUser(sdkMem, rtc_current_time, userInfo, prevData)` and
    `updateIndex(&mInput)` exactly as the R1 diagnostics imply.
  - `cpu/br28/liba/gomore/libgomore.a` (944,618 bytes) — GoMore's compiled
    library with full DWARF debug info. Embedded build paths name the SDK
    `D:\Code\HermesGM_Edge\HermesGM_Edge_Umeox_qw02\HermesGM_Edge\edge\src\...`
    (clang 4.0.1, Jieli `pi32v2` target — not Cortex-M). Source module names
    include `GoMoreLib_APP.c`, `aesDec.c`/`aesEnc.c`, `sdkAuth.h`
    (`SdkAuthInfo { is_authed, expire_date, pKey, deviceId, devIdLen }`),
    `goodixWrapper.c` (`SWITCH_MODE_PPG_HR`, `SWITCH_MODE_SLEEP_STAGE`),
    `moduleAccDet.c`, `moduleActType.c` (`ACT_TYPE_WALK/RUN/...`),
    `moduleChronotype.c`, `moduleEngyExpenditure.c`, `moduleWellnessSummary.c`,
    `moduleFFT.c`, etc.
- **H4 — Generic open implementations (RMSSD/Cole-Kripke): NOT PURSUED as
  attribution.** The R1 GoMore bodies are provider-neural/IIR/graph code pinned
  by existing audits; no public code shares their constants/structure.

### Code-level cross-check

R1 image strings name the same API surface as the leaked header, verbatim:
`gomore setAuthParameters failed:%d`, `gomore setAuth failed: %d`,
`gomore healthIndexInitUser failed:%d`, `gomore updateIndex failed:%d, ts:%d`,
`gomore store pKey crc32 not match`, plus `[sdkAuth]=%d` / `[sdkAuth]=%f` —
matching the SDK's `sdkAuth.h` module. This confirms the R1 cluster is GoMore's
"HermesGM_Edge" SDK integrated per its public HAL. However: the artifact is
**binary-only, unlicensed, and compiled for Jieli pi32v2**, so no
instruction-level or source-level attribution is possible, and no
redistribution right exists. The header/struct files are still the best public
documentation of the provider ABI (auth struct, `IndexIO`, sleep config) for a
future licensed-provider negotiation.

### Verdict — GoMore: REMAINS BLOCKED

No lawfully usable public source exists. Concrete (unlicensed) provider
pointer recorded: `zhengzhengchuang/umeox_JL701n_128_lvgl_watch[_hw_v1.1]`,
`code/sdk/apps/common/ui/lv_watch/comm_func/GoMoreLib.h`,
`GoMoreLibStruct.h`, `gomore_func.c`, and `code/sdk/cpu/br28/liba/gomore/libgomore.a`
(SDK internal name `HermesGM_Edge`). These are correlation/ABI-documentation
evidence only, identical in kind to the QST snapshot policy: they do not admit
the 362 functions.

---

## 2. YHMICROS YHM2710 (36 functions)

### Hypotheses tested

- **H1 — Public driver code: NO MATCH.** GitHub code/repo search for
  `yhm2710`, `YHM2710`, `yhmicros` returns only this project's own documents
  (and a mirror). Gitee/web searches (Chinese and English) return no driver,
  register map, or example code.
- **H2 — Public datasheet: NOT FOUND.** yhmicros.com lists YHM2710 only as a
  marketing entry ("500mA Linear Charger" on the smart-watch solutions page;
  product page `productw.asp?id=44` exposes Datasheet/Application-Note links
  behind a sample-request flow with no downloadable document retrievable from
  this workspace). No distributor (LCSC etc.) hosts a datasheet PDF. The prior
  boundary note stands: similarly named HM2710 material is a different part.
- **H3 — Transport documented elsewhere: NEGATIVE.** The recovered
  `device_stacmd` single-wire state-command framing (P1.11/P1.14 clock/data,
  P1.01 status, no slave-address phase, `[r,00,00]` read phases) matches no
  published protocol description; the chip-ID `0xA0` check and register-2
  `0xA8`/`0x28` writes appear in no public document.

### Verdict — YHM2710: REMAINS BLOCKED

No public code and no public register documentation. Not even a datasheet
pointer could be authenticated; the vendor product page is the only public
reference. The conservative gate and the clean-room R1 resource split
(`YHM2710-I2C5-RESOURCE-BOUNDARY.md`) stand unchanged.

---

## 3. GXCAS GXT310 (5 functions in the original audit; 8 in the completed closure)

### What changed since the 2026-08-11 review

The official GXCAS archive that previously timed out is now retrievable:

- URL: `https://www.gxcas.com/uploads/files/202510/GXT310_STM32驱动程序V1.0_202506_20251013111351.zip`
  (catalog entry `GXT310-STM32 driver-V1.0`, gxcas.com download page).
- Retrieved 2026-08-14: HTTP 200, 2,683 bytes, SHA-256
  `cdd4e53adf27c3c1843dccb09a88a782b94e3dd6b918c6046cfcb30f6633da05`.
- Contents: `gxt310.c` (6,072 bytes) and `gxt310.h` only. **No license file,
  no copyright header, no redistribution terms.**

### Content vs. the R1 bodies

The archive is a minimal STM32 StdPeriph bit-bang-I2C demo: `IIC_Start/Stop/
Wait_Ack/Ack/NAck/Send_Byte/Read_Byte` on GPIOB.6/7 with `delay_us`,
`GXT310_Read_Register(w_addr, point_reg, r_addr)` (pointer write, repeated
read of two bytes), `GXT310_Write_Register(w_addr, point_reg, data1, data2)`,
and `GET_GXT310_TEMP()` reading register `0x00` and scaling by `0.0078125`
(1/128 °C/LSB). `gxt310.h` defines only `GXT310_W_ADDR 0x90` — matching the R1
`GXT310X0 (0x90)` channel (the second R1 channel `GXT310X2 (0x94)` is not in
the demo). There is no mode-switch or one-shot logic in the demo at all.

The five originally gated R1 bodies (`0x00050F9C` enable orchestration with `[RING] TEMP`
logging and the sensor registry; `0x0006F804/0x0006F81E` mode-switch thunks;
`0x0006F818/0x0006F832` one-shot bodies), plus the subsequently recovered shared read,
mode, and one-shot bodies at `0x0006F600`, `0x0006F648`, and `0x0006F738`, are built on the R1 runtime-vtable
software-TWI framework — a completely different structure, platform HAL, and
abstraction level from the StdPeriph demo. **No code-level identity exists.**
The archive also postdates the R1 image (2025-06/2025-10 vs. the older stock
firmware), so even compatibility would not prove it was the stock source.

### Historical verdict — GXT310: PARTIAL DOCUMENTATION POINTER

The vendor's own demo publicly documents the wire behavior: 7-bit address
`0x48` (`0x90` write / `0x91` read), pointer-register read/write protocol,
16-bit big-endian temperature at register `0x00`, scale `0.0078125 °C/LSB`.
That is a register-behavior pointer, not a source admission: the archive has
no license, does not match the R1 bodies, and does not cover the R1
mode-switch/one-shot operations. This attribution finding does not admit the vendor archive;
the later owner-authorized clean-room policy independently reconstructed all eight functions.

---

## 4. QST QMA6100 (3 functions)

### Re-verification of the pinned correlation snapshot

The previously pinned public snapshot is still live and was re-fetched:
`github.com/stephenshizl/code-learning` @ `3903bd7d632c0aa6b101e623b1fd27c84184208e`,
path `调试素材/.../comm_demo/qma6100/qma6100.cpp` (+ `qma6100.h`). Header
identification block: `@author Yangzhiqiang@qst`, `@version V1.0`,
`@date 2020-5-27`. The header defines `QMA6100_DEVICE_ID 0xfa`,
`QMA6100_I2C_SLAVE_ADDR 0x12` / `ADDR2 0x13`, `QMA6100_CHIP_ID 0x00`,
`QMA6100_REG_RANGE 0x0f`, and range enums `2G=0x01, 4G=0x02, 8G=0x04,
16G=0x08, 32G=0x0f`. The snapshot carries **no license**.

### Body-level comparison of the three gated functions

| R1 body | Snapshot counterpart | Result |
| --- | --- | --- |
| `0x00086E34` `qma6100_chip_id` (18 B): `readreg(0x00, &id, 1); return id` | `qma6100_chip_id()`: same read of reg `0x00` with one retry + logging | Subset match (logging/retry compiled out); trivially generic alone |
| `0x00087188` `qma6100_set_range` (56 B) | `qma6100_set_range()` | **Exact semantic identity**: comparisons in the same order (`0x02→2048`, `0x04→1024`, `0x08→512`, `0x0f→256`, else `4096` LSB/g), then `writereg(0x0f, range)` |
| `0x000871C4` `qma6100_soft_reset` (138 B) | `qma6100_soft_reset()` | Same registers and magic values (`0x36←0xB6`, clear, `0x11←0x80` poll, `0x33←0x08` OTP-load then poll `0x33==0x05`), same ~100-iteration retry bound; **different** write/poll ordering and delay values (R1: delay 100 after clear, re-write `0x11=0x80` inside the poll, delay 2/10; snapshot: delay 2, write once, delay 5) — a later/different QST revision, not this exact snapshot |

String-level identity reinforces lineage: the R1 image contains the snapshot's
verbatim error strings `qma6100_read_fifo state error` and
`qma6100_read_fifo depth(%d) error`. The R1 identity adapter (`0x00086E68`)
also embeds the two slave addresses as the literal halfword `0x00001312`
(bytes `0x12, 0x13` — verified in the rebuilt image), matching the snapshot's
`{QMA6100_I2C_SLAVE_ADDR, QMA6100_I2C_SLAVE_ADDR2}` search order.

### Installed-part identity evidence

The R1 acceptance rule is `chip_id == 0xFA || (chip_id >> 4) == 0x9`. `0xFA`
is the QMA6100 (non-P) device ID per the QST header. `0x9x` is exactly the
QMA6100P identification rule, now publicly documented in RIOT's
datasheet-derived driver: `QMA6100P_CHIP_ID_MASK 0xF0` / `..._VAL 0x90`,
"Bits[7:4] = 0x9 (fixed). Bits[3:0] factory-set, software must ignore"
(`drivers/qma6100p/include/qma6100p_regs.h`, RIOT-OS/RIOT master,
LGPL-2.1-only). The stock driver therefore covers both QMA6100 and QMA6100P
silicon; the product probe treats QMA6100 as the third, normally-absent
fallback behind LIS2DW12/BMA456W.

### Licensed public drivers — tested as attribution candidates

- **RIOT-OS `drivers/qma6100p`** (2026, LGPL-2.1-only): full public register
  map including `SW_RESET (0x36) = 0xB6` and `NVM (0x33)`. Its `_soft_reset`
  is structurally different from the R1 body: no `0x11←0x80` poll, no
  `0x33←0x08` write, and it polls an NVM bitmask (`LOAD_DONE|RDY`) per
  datasheet §6.3 rather than equality `== 0x05`. Independent authorship — NOT a
  match.
- **espressif/qma6100p** (IDF Component Registry v2.0.1, esp-iot-solution
  family, Apache-2.0): same address pair `0x12/0x13` and the same
  datasheet-determined range/sensitivity table; ESP-IDF I2C structure unrelated
  to the R1 bodies — NOT a match.
- **meshtastic/QMA6100P_Arduino_Library** (SparkFun KX13x port): unrelated
  structure — NOT a match.

The shared constants (range encodings `1/2/4/8/0x0f`, sensitivities
`4096/2048/1024/512/256` LSB/g, reset `0x36/0xB6`) are properties of the chip's
datasheet register map, common to every driver; code-level identity exists only
with the **unlicensed** QST V1.0-lineage snapshot.

### Verdict — QMA6100: REMAINS BLOCKED (lineage confirmed and sharpened)

The three bodies' origin in QST's evaluation driver is now established at the
constant, structure, string, and slave-address level, and the family name
`qst_qma6100_v1_0_lineage_unlicensed` is accurate. No *licensed* public driver
matches the bodies, so no re-attribution is possible. New documentation
pointers: the complete QMA6100P register map (including the reset/NVM sequence
and the 0x9x chip-ID rule) is publicly available under LGPL-2.1 in
RIOT-OS/RIOT `drivers/qma6100p/` and under Apache-2.0 in Espressif's
`espressif/qma6100p` component, and the QMA6100/QMA6100P datasheets are
publicly mirrored (datasheet4u, LCSC). A future datasheet-derived rewrite is a
policy decision outside this audit; the ledger gate stands.

---

## Summary table

| Family | Functions | Public source found | Licensed | Code-level match | Verdict |
| --- | ---: | --- | --- | --- | --- |
| GoMore `gomore_health_algorithm_candidate` | 362 | umeox JL701N SDK dump: `GoMoreLib.h`/`GoMoreLibStruct.h` + `libgomore.a` (`HermesGM_Edge`, pi32v2) | No | ABI/strings only (wrong ISA, binary-only) | REMAINS BLOCKED; unlicensed provider-ABI pointer recorded |
| YHMICROS `yhmicros_yhm2710_candidate` | 36 audited / 44 final | None (no code, no datasheet) | — | — | Historical gate superseded by owner-authorized transparent-C closure |
| GXCAS `gxcas_gxt310_candidate` | 5 audited / 8 final | Official `GXT310_STM32驱动程序V1.0` zip, SHA-256 `cdd4e53a…3da05` (retrieved 2026-08-14) | No (no license in archive) | No (STM32 StdPeriph demo ≠ R1 framework bodies; postdates R1) | Documentation pointer only; owner-authorized transparent-C closure uses no archive code |
| QST `qst_qma6100_v1_0_lineage_unlicensed` | 3 | QST V1.0 snapshot re-verified @ `3903bd7d`; licensed QMA6100P drivers (RIOT LGPL-2.1, Espressif Apache-2.0) | Snapshot: no; RIOT/Espressif: yes | Snapshot: yes (constants/structure/strings); licensed drivers: no | REMAINS BLOCKED; licensed register-map documentation pointers recorded |

Audit performed 2026-08-14. No project files other than this report were created
or modified.
