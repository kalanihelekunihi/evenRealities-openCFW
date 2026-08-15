# Generic device-registry ownership boundary

## Result

Nine recovered functions implement the stock name-based device registry and its operation-table
dispatch. Their subsystem semantics are clear, but no attributable upstream project, vendor
version, or license has been established. They are therefore recorded as
`unknown_generic_device_registry_candidate` with disposition
`investigate_before_implementing`, not as R1-owned code.

openR1 does not reproduce this framework. Product adapters bind directly to admitted Nordic,
Bosch, ST, FlashDB/FAL, or abstract licensed-provider interfaces. This preserves required device
behavior without silently treating an unidentified framework as clean-room product code.

Six fixed two-wire record-binding wrappers are separately admitted as R1 configuration, not as
registry implementation. Their exact extents and direct-typed-binding replacement are documented
in [`BUS-REGISTRATION-CORRELATION.md`](../correlation/BUS-REGISTRATION-CORRELATION.md).
The four associated GPIO-driven bus engines are a distinct forty-function unidentified-provider
boundary. Their recovered behavior does not authorize reconstructing the registry or engine; see
[`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](SOFTWARE-TWI-PROVIDER-BOUNDARY.md).
One additional fixed RTC record-binding wrapper is admitted under the same configuration-only
rule, while its seven generic RTC-device operations remain separately source-gated; see
[`RTC-DEVICE-PROVIDER-BOUNDARY.md`](RTC-DEVICE-PROVIDER-BOUNDARY.md).

## Recovered layout

A registry record contains at least:

| Offset | Recovered role |
| ---: | --- |
| `0x00` | non-null device name |
| `0x04` | non-null operation-table pointer |
| `0x14` | next registry record |

`0x00085D58` rejects null records, duplicate names, missing names, or missing operation tables. It
appends a valid record to a global singly linked list, clears the record's next pointer, and returns
one on success. `0x00085CE0` walks the same list, compares the requested name against offset zero,
and returns the matching record or null.

Seven dispatchers validate the record, load its operation table from offset `0x04`, and invoke a
slot only when that slot is non-null. A null record returns `1`; a missing operation returns the
slot-specific status shown below. Arguments and return values are passed through to the selected
provider operation.

| Extent | Operation-table slot | Missing-operation status |
| --- | ---: | ---: |
| `0x00085D08..<0x00085D1A` | `0x00` | `5` |
| `0x00085D1A..<0x00085D2C` | `0x08` | `5` |
| `0x00085CBA..<0x00085CCC` | `0x0C` | `6` |
| `0x00085D2C..<0x00085D46` | `0x10` | `2` |
| `0x00085DA8..<0x00085DC2` | `0x14` | `3` |
| `0x00085CCC..<0x00085CDE` | `0x18` | `7` |
| `0x00085D46..<0x00085D58` | `0x20` | `9` |

The slot names are intentionally not guessed. Callers establish that the table is shared across
named ADC, bus, flash, motion, NFC, PMIC, and touch records, but caller use alone does not identify
the framework's author.

## Sharpened fingerprint evidence

The provenance investigation added the following detail. None of it changes the admission state;
the family remains `investigate_before_implementing`.

- The registry candidate family spans 40 functions / 1,514 executable bytes. The record layout is
  `{name* @ 0x00, ops* @ 0x04, priv @ 0x08..0x10, next @ 0x14}` in a global singly linked list.
  Register at `0x00085D58` performs a `strcmp` duplicate-name check and returns `0/1`; find at
  `0x00085CE0` walks the list with `strcmp`.
- The operation table is nine words wide. The seven dispatchers at
  `0x00085D08 / 0x00085D1A / 0x00085CBA / 0x00085D2C / 0x00085DA8 / 0x00085CCC / 0x00085D46`
  return per-slot positive small-integer missing-operation statuses `{5,5,6,2,3,7,9}` and `1` for
  a null record — the same positive-status scheme documented in the table above.
- Slots `0x10`/`0x14` carry a static request-block bus protocol:
  `{u8 cmd = 0xAE, u16 reg, buf, len, data, len2}`.
- A companion subscriber registry at `0x0005DB14` uses pool-allocated 0x1C-byte nodes, caps names
  at seven characters at offset `+8`, stores the current-task handle obtained through
  `xTaskGetCurrentTaskHandle` at `+4`, and relies on intrusive offset-based doubly-linked-list
  helpers at `0x00077E30`/`0x00077E3C`.
- The device-name string table at flash `0x000C06D4..0x000C07E4` contains: `device_flash`,
  `i2c_0`..`i2c_5`, `acc_int_1`, `touch_rdy_in/out`, `pmic_irq`, `device_stacmd(_irq)`,
  `nfc_gpo_irq`, `mcu_reset_irq`, `ppg_int`, `ppg_led_en`, `ship_mode_en`, `touch_ldo_en`,
  `ppg_reset_en`, `sys rtc`, `watchdog`.
- The registry's missing-operation codes `{1,2,3,5,6,7,9}` interlock gap-free with the
  software-TWI adapter codes `{4,8,10,11,12}` into one positive-integer status enum `0..12` — see
  [`SOFTWARE-TWI-PROVIDER-BOUNDARY.md`](SOFTWARE-TWI-PROVIDER-BOUNDARY.md). This is strong evidence
  of single authorship across both families.

## Candidates rejected

- RT-Thread device framework v4.0.x is concretely rejected on ABI grounds, verified against
  upstream v4.0.3 `device.c`: it uses `rt_object` container lookup rather than a `strcmp` walk,
  `RT_ASSERT`-guarded dispatchers, negative errnos, and a six-slot operations table with
  refcounting.
- Zephyr, the Nordic SDK, and FlashDB/FAL are rejected: none provide a global named-record
  registry with this record layout, nine-word vtable, or positive-status dispatch scheme.
- All vendor-cache packs are rejected for the same structural reasons.
- Code-host searches for `device_stacmd`, `mcu_reset_irq`, and `touch_rdy_out` return only this
  repository and its mirrors.

## Next evidence step

Run an authenticated gitee/GitHub code search for the exact rare device names, and check earlier
R1 firmware versions (v2.0.1.14..v2.0.8.20 in the research workspace) for debug builds carrying
framework-identifying log strings.

Cross-firmware fingerprint search performed 2026-08-13 (negative result): all 59 binary blobs in
the research workspace (`research/firmware/versions/*` v2.0.1.14..v2.0.8.20 including extracted
EM9305/codec/box/OTA images, `research/firmware/tagged/r1-ring/*` bootloaders, and this
repository's r1/g2 blob trees) were scanned for the 24-byte dual month table
(`1f 1c 1f 1e ... 1f`), the strings `dlCom`, `pre2exc`, `pv_v`, `device_stacmd`,
`mcu_reset_irq`, `touch_rdy_out`, `ship_mode_en`, `sys rtc`, `vnfc_rect_adc`,
`lisent register fail`, `sensor_algo_mem_fatal`, `unregister not find obj`,
`register not find obj`, `only support 1 ord`, and `reset timer,%s, tick`. No blob carries any
platform-layer fingerprint. The only `B210` occurrences are the `B210_DFU` build strings in the
two minimal tagged R1 bootloaders, which contain no registry/RTC/TWI framework code. The
sibling-image attribution route is therefore exhausted for the interlocked families; remaining
routes are authenticated code-host search and acquisition of a platform SDK through the ODM.

## Cross-family interlock

The software-TWI, generic device-registry, RTC-device, time/calendar, and sensor-stream families
interlock: shared positive status enum `0..12`, runtime registration of records (including the
RTC `sys rtc` record at `0x00085D58`), and the `i2c_n` device naming. They most likely form one
proprietary platform layer inside Even Realities' B210 product tree and therefore share one
provenance fate.

## Clean replacement policy

- Nordic SDK APIs own nRF52840 drivers and hardware primitives.
- Attributable Bosch, ST, FlashDB/FAL, tiny-AES, and other admitted sources own their respective
  provider implementations.
- R1-local code may contain only fixed product configuration, bounds, state policy, and narrow
  adapter glue already admitted in the ownership ledger.
- Proprietary or unidentified device operations remain behind disabled semantic provider
  interfaces until licensed source is supplied.
- The linked Nordic target must not acquire a clone of this global registry merely to match stock
  architecture; direct typed bindings are the cleaner functional equivalent.

This boundary does not authorize any signing, rollback, protection, diagnostic, or deployment
bypass.

## Attribution re-examination 2026-08

A second attribution pass (2026-08-14) re-analyzed the decompiled bodies, extracted new
fingerprints (ODM `platform\` build paths `platform\services\eAT\at_system.c`,
`platform\threads\thread_manager.c`, `platform\ble\app_ble_init.c`; log strings
`register not find obj`, `only support 1 ord`, `lisent register fail`,
`sync_store_one_class`), ran authenticated GitHub and Sourcegraph global code searches
(zero third-party matches for all eight fingerprints), and fetched/compared three new
candidates — Goodix GH3x2x demo SDK (public copies), BabyOS `b_device.c`, Bouffalo
`bflb_device` — all structurally rejected. Verdict: **no attribution; the family remains
proprietary/blocked**. Full report:
[`unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md`](unknown_generic_device_registry_candidate-ATTRIBUTION-2026-08.md).

Platform-vendor cross-reference (2026-08): the interlocked B210 platform middleware that owns
this family has been identified as Wuxi Bravechip Technologies' "ChipletRing" / BCL603M
smart-ring platform — firmware identity string `603MV1.9.3` and a byte-exact 128-bit GATT
base-UUID match to Bravechip's public `BravechipSpace/ChipletRing-APPSDK`. The platform is
closed-source; this names the commercial acquisition route that would unblock the family.
See `unknown_shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md`.

## Reduction 2026-08

Under the owner-authorized full reduction (2026-08-14, see
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)), the forty ledger entries of
`unknown_generic_device_registry_candidate` (the ops-table dispatchers, offset-list walkers, subscriber machinery, and static request-block client wrappers) are reconstructed
from the recovered decompilation evidence as independently compiled C in
[`../../reconstructed/generic_device_registry/`](../../reconstructed/generic_device_registry/).  The
reconstruction is not vendor source; it carries per-function provenance
banners, and its contract, reconstruction decisions, divergences, and
host-test mapping are documented in
[`../correlation/GENERIC-DEVICE-REGISTRY-REDUCTION-CORRELATION.md`](../correlation/GENERIC-DEVICE-REGISTRY-REDUCTION-CORRELATION.md).
The ledger disposition for the forty entries is now
`clean_room_reimplementation_owner_authorized`.  This document remains the
provenance record of why no upstream source was admitted.
