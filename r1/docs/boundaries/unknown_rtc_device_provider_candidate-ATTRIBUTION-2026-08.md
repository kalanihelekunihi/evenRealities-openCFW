# Attribution re-examination: unknown_rtc_device_provider_candidate (2026-08)

## Family

`unknown_rtc_device_provider_candidate` — 10 functions, 608 executable bytes, application image
(base 0x27000):

| Extent | Bytes | Role |
|---|---:|---|
| `0x00050DAA..<0x00050DB5` | 12 | `sys rtc` ops-table slot 7; forwards to registry dispatcher slot 0x20 |
| `0x00050DB6..<0x00050DBF` | 10 | `sys rtc` ops-table slot 4; forwards via 0x40-byte request block to slot 0x14 |
| `0x00050DE0..<0x00050DEB` | 12 | shared tail: `dispatcher_0x85D46(*rtc_dev, 0, arg)` |
| `0x00056274..<0x000562DF` | 108 | 8 Hz tick handler: epoch accumulation + per-record alarm dispatch |
| `0x000562E0..<0x00056315` | 54 | epoch→8-field calendar adapter over toolchain `gmtime` |
| `0x00056318..<0x0005638D` | 118 | named-record open: nrfx RTC init (prescaler 4095) + start |
| `0x0005639C..<0x000563BF` | 36 | epoch + subsecond snapshot |
| `0x000563F8..<0x0005643F` | 72 | named 44-byte calendar-record write |
| `0x00056444..<0x00056497` | 84 | named callback binding (record +0x3C) |
| `0x0005649C..<0x00056501` | 102 | named-record epoch/tick-divider initialization |

## Methods

- Ghidra decompilation (`r1/research/decompilation/application/decompiler-output.c`) for the seven
  decoded bodies; fresh Capstone (Thumb) disassembly of the three Ghidra-missed bodies
  (`0x56274`, `0x56318`, `0x5639C`) from the byte-exact rebuilt image
  (`r1/research/decompilation/rebuild/rebuilt-application.bin`, sha256 per `manifest.json`).
- rodata pointer scanning of the rebuilt image for ops tables, handler pointers, and device-name
  strings; full printable-string census for vendor fingerprints.
- Authenticated GitHub code search (`gh search code`) for 12+ rare strings/device names.
- Real upstream source fetches (URLs below) with structural comparison; cross-repo G2 evidence.

## New structural evidence (this examination)

- The `sys rtc` ops table is at flash `0x00099C8C`: nine words
  `{0x50D87, 0x50D61, 0x50D7F, 0x50D83, 0x50DB7, 0x50D65, 0x50D8B, 0x50DAB, NULL}`. Slots
  `0x50DAA`/`0x50DB6` re-dispatch through the blocked generic registry by name
  (`find("sys rtc")` cached at `0x50DC0`), i.e. they are application glue over the registry, not
  an independent library.
- `open_by_name` (`0x56318`) scans a 256-entry table of 88-byte records at `0x20007384` with
  `(i+1) & 0xFF` wrap and `strcmp` name match; on first open it copies an 8-byte const
  `nrfx_rtc_config_t` from `0x0009A638` (`{prescaler=0, irq_priority=6}`), overrides prescaler to
  `0xFFF` (32768/4096 = 8 Hz), and calls `nrfx_rtc_init/tick_set/enable` with handler `0x56275`.
- Tick handler (`0x56274`): counts 0..7 at `record+2`; on the 8th tick increments the epoch at
  `record+4` and applies the signed int16 UTC offset in minutes ×60 via
  `rsb r1, r1, r1, lsl #4` (×15) then `add.w r0, r0, r1, lsl #2` (×4). It then converts the epoch
  via `FUN_000562E0` and walks all 256 records, comparing calendar second/minute against record
  `+8`/`+0xC` and invoking the callback at record `+0x3C` with the current hour (`uxtb`).
- Snapshot (`0x5639C`): stores epoch at `out+0x2C` and a 64-bit millisecond value
  `epoch*1000 + tick` at `out+0x38`, computed as `rsb r1, r3, r1, lsl #7` (×125) then
  `add.w r0, r0, r1, lsl #3` (×8).
- The epoch→calendar adapter `FUN_000562E0` calls toolchain `gmtime` (`0x276C8`, ledger
  `arm_toolchain_runtime`) and copies `tm_sec/min/hour/mday/mon+1/year+1900/wday/yday+1` into an
  8-word struct. No private Gregorian arithmetic exists in this family; the application's private
  converters belong to the separate `unknown_time_calendar_provider_candidate` family
  (dual month tables at `0x99C5C`/`0x99C74`).

## Hypotheses tested

1. **Classic embedded calendar (vendor "rtc.c" Gregorian conversion, sakamoto, Howard Hinnant
   date algorithms, μC/Clk, Nordic app_timer calendar, Zephyr time utils)** — REJECTED
   structurally: the family contains no calendar arithmetic at all; conversion delegates to the
   attributed toolchain `gmtime`. Nothing to attribute.
2. **Nordic nRF5 SDK** — REJECTED for the wrapper layer (only the 180-byte `nrfx_rtc_init` body
   matches and is already admitted). Nordic SDK has no named-record registry layer.
3. **RT-Thread** — REJECTED against fetched v4.0.3 `components/drivers/rtc/rtc.c`
   (raw.githubusercontent.com/RT-Thread/rt-thread/v4.0.3/...): uses `rt_device_find("rtc")` +
   `rt_device_control(device, RT_DEVICE_CTRL_RTC_SET_TIME, &now)`, `localtime`/`mktime`, negative
   errnos, no named 256-entry alarm record table. Registry-side ABI mismatch with v4.0.3
   `src/device.c` was already verified in GENERIC-DEVICE-REGISTRY-BOUNDARY.md.
4. **MR library (Mac-Rsh/mr-library, master `source/device.c`)** — REJECTED: tree-structured
   devices with inline fixed-length names, descriptor map, parent/child lists, reference counts,
   negative error codes (`MR_ENOTFOUND=-3`, `MR_EEXIST=-5`, `MR_EINVAL=-7`). The R1 registry uses
   name/ops pointers, a flat singly-linked list, and positive status codes.
5. **BabyOS (notrynohigh/BabyOS `bos/core/b_device.c`)** — REJECTED: devices are compile-time
   static tables generated by the `B_DEVICE_REG` X-macro in `b_device_list.h`; there is no runtime
   strcmp linked-list registration.
6. **armink open-source ecosystem** — REJECTED: the image does carry armink's FlashDB/FAL
   (`third_party\DB\FlashDB`, `fal_flash_device_find`, `device_table[i]->ops.read`) and CmBacktrace
   (`Firmware name: %s, hardware version: %s...`, `Fault on thread %s`), all attributed elsewhere,
   but armink publishes no named-device registry or RTC framework; MultiTimer is an unnamed
   linked-list soft timer.
7. **Vendor wearable SDKs (Goodix, GoMore, HRS3300/PAH800x, Realtek, Bluetrum, Jieli)** —
   REJECTED: Goodix public demo-SDK mirror contains zero RTC/registry code (prior verified); all
   in-image Goodix/GoMore code is confined to separately attributed sensor-algorithm families;
   Jieli/Bluetrum SDKs target their own audio SoCs, not nRF52840+S140; Realtek Bee SDK has no
   public source. No string or structure overlap with any of these.
8. **First-party "B210 platform" middleware** — SUPPORTED by five independent
   lines of evidence:
   - Vendor build-tree layout: `platform\threads\thread_manager.c`,
     `platform\services\eAT\at_system.c`, `platform\ble\app_ble_init.c` are built from
     `product/B210/app/_build/B210_Application`, while genuine third-party code sits under
     `third_party\` (FlashDB). The platform tree is the vendor's own by its own layout.
   - The sibling G2 (s200) product shares the identical `platform\threads\thread_manager.c`;
     `g2/docs/research/g2-thread-manager-dependency-boundary.md` closed that object as
     first-party code after attributing all 117 external calls to EasyLogger,
     CMSIS-FreeRTOS, littlefs, and other named providers.
   - The R1 ring image carries cross-product platform strings (`glasses_touch_close_deferred_cb`)
     showing one in-house platform serving glasses and ring products.
   - Authenticated GitHub code search (2026-08-14): `"sys rtc"`, `"vnfc_rect_adc"`,
     `"device_stacmd"`, `"touch_rdy_out"` match only this repository and its mirror
     (AM-Guru/SybilSight); `"lisent register fail"`, `"unregister not find obj"`,
     `"eAT core init"`, `"thread manager start"`, `"device_module_application_init"` return zero
     public hits.
   - The family's positive status codes {0,2,4,17} interlock gap-free with the generic-registry
     codes {1,2,3,5,6,7,9} and software-TWI codes {4,8,10,11,12} into one enum 0..12 — single
     authorship across the interlocked B210 platform families.
   - The sibling-family report
     `unknown_shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md` identifies the
     platform vendor as Wuxi Bravechip Technologies ("ChipletRing" / BCL603M) via the firmware
     identity string `603MV1.9.3` and a byte-exact GATT base-UUID match to Bravechip's public
     ChipletRing-APPSDK; the B210 tree is that platform's product tree.

## Verdict

**NO ATTRIBUTION — the family remains proprietary and implementation-blocked.** With high
confidence this is first-party B210/Bravechip platform code (no public source, no license),
not an unidentified open-source library; the "find the upstream" route is exhausted: concrete
rejections against RT-Thread, MR library, BabyOS, armink ecosystem, Nordic, Zephyr, and the
vendor wearable SDKs above, plus negative authenticated code-host and 59-blob cross-firmware
fingerprint searches (2026-08-13, per GENERIC-DEVICE-REGISTRY-BOUNDARY.md). The only remaining
unblock route is source/license acquisition from the platform vendor (Bravechip, per the
ChipletRing-APPSDK contact route) or the ODM. The ledger disposition
`investigate_before_implementing` stands; no clean-room reimplementation is authorized by this
report.
