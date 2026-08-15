# Attribution re-examination: `unknown_generic_device_registry_candidate` (2026-08-14)

Supplements [`GENERIC-DEVICE-REGISTRY-BOUNDARY.md`](GENERIC-DEVICE-REGISTRY-BOUNDARY.md).
That boundary doc remains authoritative for admission state; this file records the
2026-08 attribution pass only. No ledger CSVs, generator scripts, or source were modified.

## Family under test

- `provider_family`: `unknown_generic_device_registry_candidate`,
  `source_disposition`: `investigate_before_implementing`.
- 40 functions / 1,514 executable bytes. Address clusters:
  - request-block helpers: `0x000509BC..0x00050F81`, `0x0005D1EA..0x0005D241`,
    `0x00087AF8`, `0x0009338C`, `0x00096FB0`, `0x0006F90E`, `0x00077214`;
  - flash-through-registry erase helpers: `0x0005B2F8`, `0x0005E1FC`;
  - subscriber/name-hash cluster: `0x0005D8CC..0x0005DC05` (incl. BKDR hash
    `0x0005D8CC`, node alloc `0x0005D94A`, insert `0x0005DB14`);
  - module-enabled scan: `0x000734E8`;
  - intrusive offset-list helpers: `0x00077E30`, `0x00077E3C`;
  - core registry: `0x00085CBA..<0x00085DC2` (find `0x00085CE0`, register
    `0x00085D58`, seven ops dispatchers);
  - registry mutex guards: `0x00097730`, `0x00097748`.

## Methods

1. Read the existing boundary doc and all 40 ledger rows/evidence strings.
2. Read the decompiled bodies of all family functions in
   `r1/research/decompilation/application/decompiler-output.c`; cross-checked callers in
   `call-graph.csv` and string labels in `symbols.csv`.
3. Extracted full log/path strings from `r1/research/decompilation/rebuild/rebuilt-application.bin`.
4. Authenticated GitHub code search (`gh api search/code`, account kalanihelekunihi,
   2026-08-13/14) and Sourcegraph global stream search for every distinctive fingerprint.
5. Fetched upstream sources of concrete candidate frameworks and compared structure.

## Body analysis highlights (decompilation quotes)

Find-by-name (`0x00085CE0`) — global singly linked list, `strcmp` (FUN_000277fe) walk:

```c
puVar2 = (undefined4 *)*DAT_00085d04;
while (puVar2 != 0) {
  iVar1 = FUN_000277fe(*puVar2, param_1);   /* strcmp(record->name, name) */
  if (iVar1 == 0) break;
  puVar2 = (undefined4 *)puVar2[5];          /* next @ +0x14 */
}
return puVar2;
```

Register (`0x00085D58`) — rejects null record, duplicate name, null name or null ops
table; appends at list tail; returns `1` on success, `0` on rejection.

Dispatcher shape (example `0x00085D2C`, ops slot `+0x10`):

```c
if (param_1 == 0) return 1;                            /* null record */
cb = *(code **)(*(int *)(param_1 + 4) + 0x10);         /* ops table @ +0x04 */
if (cb != 0) return cb();                              /* pass-through */
return 2;                                              /* per-slot missing-op status */
```

Missing-operation statuses across the seven dispatchers are `{5,5,6,2,3,7,9}` (slots
`0x00,0x08,0x0C,0x10,0x14,0x18,0x20`); they interlock gap-free with the software-TWI
adapter codes `{4,8,10,11,12}` into one positive status enum `0..12` (single authorship).

Subscriber registry (`0x0005DB14`): pool-allocated `0x1C`-byte nodes, name copied with a
**7-character cap** at node `+8`, current-task handle at `+4` (`FUN_0009879c` reads a
dereferenced global, i.e. the RTOS current-TCB accessor), callback at `+0x18`, guarded by
mutex helpers `0x00097730`/`0x00097748` (which wrap `FUN_0007d488`/`FUN_0007d536` —
flag-tagged-pointer lock/unlock with negative errno-style returns `0xFFFFFFFx`).

Name hash (`0x0005D8CC`): classic BKDR with seed 131 (`h = h*0x83 + byte`). BKDR/131 is
ubiquitous (blog-copy code); it carries no attribution weight alone. No direct callers
appear in `call-graph.csv` (indirect or dead reference).

Request-block helpers (`0x000509BC`, `0x0005D1EA`, `0x0005D21E`, `0x0009338C`,
`0x00087AF8`, `0x00096FB0`, `0x00050DF0/0x00050F34/0x00050F5C`) fill a static per-user
request block `{u8 cmd (often 0xAE), u16 reg, void *buf, u16 len, ...}` and dispatch
through registry ops slots `+0x10` (read) / `+0x14` (write) on the device record.

`0x000734E8` ("module-enabled scan") iterates a flash-resident record array, skips
records with `!(flags@+0x12 & 1)`, and logs `[RING]sync_store_one_class, name:%s, re:%d`
through the product log sink.

## New fingerprints extracted this pass

Full strings recovered from the rebuilt image (file offsets, `strings -t x`):

- Build-source paths (Windows separators, an ODM `platform\` tree):
  `..\..\..\platform\ble\app_ble_init.c`,
  `..\..\..\platform\services\eAT\at_system.c`,
  `..\..\..\platform\threads\thread_manager.c`,
  `..\..\..\third_party\DB\FlashDB\src\fdb_tsdb.c`.
  The `platform\` tree (with a `services\eAT` AT-command service and a
  `threads\thread_manager`) is distinct from `third_party\` and matches no public SDK —
  corroboration for a proprietary platform layer, but it does not name the vendor.
- Log strings in/near the interlocked subscriber/sensor-stream code:
  `[RING]register not find obj:%s`, `[RING]unregister not find obj:%s`,
  `[RING]only support 1 ord`, `[RING]lisent register fail` ("lisent" = misspelled
  "listener"), `[RING]sync_store_one_class, name:%s, re:%d`.
- Co-resident vendor strings (context, already attributed elsewhere):
  Goodix `Gh3x2x*` demo symbols, `Gh3x2x_Virtual_Reg_v3.4`,
  `pGGH(M)3X2X_DEMO_v1.6_AC_v0.5`, `GH_SPO2_pre_pv_v2.1.10.0`,
  `product/B210/app/_build/B210_Application`.

## Code-host search results (2026-08-13/14, authenticated GitHub; Sourcegraph global)

| Query | Hits | Result |
|---|---:|---|
| `"device_stacmd"` | 25 | all this repo + `AM-Guru/SybilSight` mirror |
| `"touch_rdy_out"` | 11 | same |
| `"mcu_reset_irq"` | 9 | same |
| `"vnfc_rect_adc"` | 8 | same |
| `"acc_int_1" "ppg_int" "ppg_led_en"` | 5 | same |
| `"touch_ldo_en" "ppg_reset_en"` | 6 | same |
| `"register not find obj"` | 0 | — |
| `"unregister not find obj"` | 0 | — |
| `"sync_store_one_class"` | 0 | — (`"store_one_class"` hits unrelated) |
| `"only support 1 ord"` | 4 | unrelated (Hyperledger genConfig.go "Only support 1 org", CafeMarcheDB) |
| `filename:thread_manager.c platform` | — | no matching `platform\threads` tree |
| `"app_ble_init.c"` + `"eAT"` | — | generic name; no `platform\ble` + `services\eAT` combination |
| Sourcegraph `"register not find obj"` | matchCount 0 | — |
| Sourcegraph `device_stacmd` | 0 | — |

Gitee code search could not be executed: `search.gitee.com`/`so.gitee.com` is a
JS-only SPA requiring a login session; no credentials available. That route remains open.

## Hypotheses tested this pass (upstream sources fetched and compared)

1. **Goodix GH3x2x demo SDK** (the ring's PPG sensor vendor; `Gh3x2x*` demo code is
   co-resident). Tested against the two public copies:
   [`coredevices/pebbleos-nonfree` `gh3x2x/` tree](https://github.com/coredevices/pebbleos-nonfree)
   and [`linhui200699/ats3089` `SensorAlgoHR_GH3x2x_V4200`](https://github.com/linhui200699/ats3089).
   Repo-scoped code search: `"sys rtc"` → 0, `device_register` → 0. The demo SDK is a
   sensor driver + algorithm-call frame; it contains no name-based board device registry,
   no `device_flash`/`i2c_n`/`sys rtc` records, no positive-status ops dispatch.
   **REJECTED** (structural).
2. **BabyOS** (`notrynohigh/BabyOS`, MIT). Fetched
   [`bos/core/b_device.c`](https://raw.githubusercontent.com/notrynohigh/BabyOS/master/bos/core/b_device.c):
   compile-time integer-indexed static tables (`bDriverNumberTable[B_REG_DEV_NUMBER]`),
   devices addressed by index, not by name; no linked list, no `strcmp` register/find, no
   9-slot ops table, error scheme `B_DEVICE_FUNC_NULL`/`-1`. **REJECTED** (structural).
3. **Bouffalo Lab `bouffalo_sdk` LHAL device model**. Fetched
   [`drivers/lhal/config/bl602/device_table.c`](https://raw.githubusercontent.com/bouffalolab/bouffalo_sdk/master/drivers/lhal/config/bl602/device_table.c):
   `const` flash table `bl602_device_table[]` walked by `bflb_device_get_by_name`
   (`strcmp` over a static array); no runtime registration, no ops vtable, no status
   enum. **REJECTED** (structural).
4. **RT-Thread 4.0.x, Zephyr, Nordic SDK, FlashDB/FAL, vendor-cache packs** —
   rejected in the prior pass (see boundary doc "Candidates rejected"); re-confirmed
   consistent with the bodies above (linked-list `strcmp` registry, positive status enum
   `0..12`, nine-word ops table, 7-char subscriber name cap match none of them).

## Verdict

**(c) NO ATTRIBUTION — the family remains proprietary/blocked
(`investigate_before_implementing`).**

The prior conclusion stands and is strengthened:

- Eight independent string fingerprints (device names, log messages) are globally unique
  to this firmware across authenticated GitHub code search and Sourcegraph global search;
  the only copies on the internet are this repository and its mirror.
- The embedded build paths (`platform\services\eAT\at_system.c`,
  `platform\threads\thread_manager.c`, `platform\ble\app_ble_init.c`) show a private ODM
  `platform\` source tree that no public SDK on either code host contains.
- Every plausible public framework with a name-based device registry (RT-Thread, Zephyr,
  Nordic, BabyOS, Bouffalo LHAL, Goodix GH3x2x demo SDK) differs structurally in registry
  container, lookup, ops-table width, or error scheme.

The single-authorship interlock with the software-TWI, RTC-device, time/calendar, and
sensor-stream families (shared positive status enum `0..12`, runtime registration,
`sys rtc` / `i2c_n` naming) is unchanged: these families most likely form one
proprietary platform layer inside the B210 product tree and share one provenance fate.

## Remaining evidence routes (unchanged priority)

1. Authenticated Gitee code search for `device_stacmd`, `sys rtc`, `register not find
   obj`, `sync_store_one_class` (requires a Gitee login; not executable from here).
2. Acquisition of the platform SDK (the `platform\` tree with `services\eAT`) from the
   now-named vendor, Wuxi Bravechip Technologies (public business contact per the
   `BravechipSpace/ChipletRing-APPSDK` README: xiaojian.cui@bravechip.com), or via Even
   Realities / the ring ODM. Forensic fallback: analysis of the Bravechip ring OTA hex
   files shipped in the APPSDK (`2.4.4.81.hex16` etc.) for shared platform code.
   Public-route exhaustion, checked 2026-08-14: the APPSDK itself is phone-side only
   (`IOS/library`, `IOS/example`, `Android`, `Doc`; grep of all
   `*.h`/`*.m`/`*.c`/`*.java`/`*.md`/`*.txt` for `sensor_stream`, `soft_twi`, `sw_i2c`,
   `rtc_device`, `BCL603`, `603M` — zero hits); the BravechipSpace org contains only that
   repo plus a react fork; the second Bravechip-based ring product (`thuhci/OpenRing`,
   Tsinghua τ-Ring, `ChipletRing1.0.81.aar`) also ships no firmware source; bravechip.com's
   download list offers app SDKs/notes/datasheets only (ring firmware pre-loaded, closed);
   `Mentra-Community/MentraOS` `R1.kt` independently carries the same BAE8 UUIDs
   (corroboration of the platform identification, not a source route).
3. Any future third-party firmware dump reusing the same platform (the cross-firmware
   blob scan of 2026-08-13 was negative for all Even Realities images on hand).

This report does not authorize any implementation, signing, rollback, protection,
diagnostic, or deployment action.
