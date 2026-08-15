# RTC-device provider boundary

## Result

Nine exact functions totaling 798 executable bytes form the recovered RTC-device boundary. Five
entries were omitted by Ghidra and are restored as manual exact-extent supplements. The complete
split is:

- one 180-byte `nrfx_rtc_init` body attributable to Nordic nRF5 SDK 17.1.0;
- one 44-byte fixed R1 record/operation-table registration wrapper, retained only as direct typed
  configuration; and
- seven generic named-record, epoch, calendar, and callback functions whose source/version/license
  remain unidentified.

The seven unresolved bodies are classified as `unknown_rtc_device_provider_candidate` with
`investigate_before_implementing`. They are implementation-blocked and are not translated into
local C. Nordic owns the low-level RTC driver; OpenR1 may reproduce only separately admitted R1
configuration and must keep the generic device layer abstract until its implementation ownership
is established.

`tools/evidence/summarize_r1_rtc_device_boundary.py` checks every body against the rebuilt
application image. It is static and read-only, exposes no live clock mutation or callback
registration, and has no signing/deployment path.

## Exact map

| Extent | Bytes | Recovered role | Disposition |
|---|---:|---|---|
| `0x00056274..<0x000562E0` | 108 | one-second epoch update and matching calendar-callback dispatch | unidentified RTC provider candidate |
| `0x000562E0..<0x00056316` | 54 | epoch-to-eight-field calendar adapter | unidentified RTC provider candidate |
| `0x00056318..<0x0005638E` | 118 | named-record lookup and Nordic RTC start | unidentified RTC provider candidate |
| `0x0005639C..<0x000563C0` | 36 | epoch/subsecond snapshot | unidentified RTC provider candidate |
| `0x000563C4..<0x000563F0` | 44 | fixed record and operation-table registration | R1 configuration-only direct typed binding |
| `0x000563F8..<0x00056440` | 72 | named 44-byte calendar record copy | unidentified RTC provider candidate |
| `0x00056444..<0x00056498` | 84 | named callback binding | unidentified RTC provider candidate |
| `0x0005649C..<0x00056502` | 102 | named-record epoch/tick-divider initialization | unidentified RTC provider candidate |
| `0x0007AD6C..<0x0007AE20` | 180 | `nrfx_rtc_init` | compile Nordic SDK provider source |

The callback at `0x00056274` is also installed as the handler argument passed to Nordic
`nrfx_rtc_init`. The registration wrapper at `0x000563C4` appears in the recovered application
initcall table and calls the separately blocked generic registry at `0x00085D58`.

## Recovered timing and state

The record-open path constructs a Nordic RTC configuration with prescaler 4,095, enables tick
events, and starts the instance. A 32,768 Hz RTC divided by `4,095 + 1` produces eight ticks per
second. The callback counts values zero through seven, advances its epoch counter once on the
eighth tick, converts the epoch to calendar fields, and compares the current minute/hour against a
stored calendar record before calling its bound callback.

The state roots are `0x2000737C` and `0x20007384`. Recovered fields include a signed epoch offset or
calendar adjustment, an eight-tick divider, an epoch-seconds counter, a named record, a 44-byte
calendar structure, an `nrfx_rtc_t` instance descriptor, a callback pointer, and an embedded
generic-registry record/operation table. These field roles are compatibility evidence, not an
assertion of original private type or symbol names.

The epoch-to-calendar helper calls the toolchain time conversion at `0x000276C8`, copies second,
minute, hour, day, month, year, weekday, and year-day fields, adds 1 to month/year-day, and adds
1,900 to year. The snapshot path returns the current epoch plus a subsecond value derived from the
eight-tick divider. The generic status values and named-record API remain uninterpreted beyond the
observed semantics.

## Sharpened fingerprint evidence

The provenance investigation added the following structural detail. None of it changes the
admission state; the family remains `investigate_before_implementing`. (The ownership-ledger
candidate family accounts 10 functions / 608 executable bytes under its own counting; the
nine-function / 798-byte split above additionally covers the Nordic `nrfx_rtc_init` body and the
R1 configuration-only wrapper, and its phrasing is pinned by the verifier.)

- Eight-hertz epoch accumulation: open at `0x00056318` builds an `nrfx_rtc_config_t` with
  prescaler 4095 (32768/4096 = 8 Hz), copies an eight-byte const config containing the
  tick-handler pointer, and calls `nrfx_rtc_init` / tick-enable / enable. The tick handler at
  `0x00056274` counts 0..7 and increments the epoch on the eighth tick, applying the signed int16
  UTC offset in minutes multiplied by 60.
- A 256-entry named-record table of 88-byte records is iterated with `(r + 1) & 0xFF` and a
  `strcmp` name lookup. Each record carries an opened flag at `+4`, an embedded `nrfx_rtc_t` at
  `+0x34`, per-record alarm second/minute compares with callback dispatch, and an embedded
  registry record `{name @ +0x40, ops @ +0x44, next @ +0x54}` registered into the (blocked)
  generic registry at `0x00085D58`. Custom positive status codes `0/2/4/17` match the registry's
  positive-status scheme.
- Leaked build evidence: the device name `sys rtc` is registered alongside `watchdog`,
  `i2c_0..5`, `device_flash`, and `vnfc_rect_adc`; `__FILE__` paths include
  `platform\threads\thread_manager.c` and `platform\services\eAT\at_system.c`, and the build path
  is `product/B210/app/_build/B210_Application` — a proprietary `platform/` tree, with B210 being
  Even Realities' board codename.
- All callees are already attributed (toolchain `gmtime`/`strcmp`/`memmove`, Nordic
  `nrfx_rtc_*`) or separately blocked (generic registry, time/calendar) — proving dependency, not
  ownership.

## Candidates rejected

- Nordic SDK: no named-record layer; only the 180-byte `nrfx_rtc_init` body matches and is
  already admitted.
- RT-Thread: `rt_object` inline names, negative errnos, and no 256-entry alarm records.
- Zephyr: static devices, no runtime named-record registration of this shape.
- Goodix demo SDK: zero RTC/registry code in the public mirror.

## Next evidence step

Mine other Even Realities images sharing this platform (G1/G2 OTA payloads, charging-dock MCU
image) for the same code with richer `__FILE__`/assert strings.

## Cross-family interlock

The software-TWI, generic device-registry, RTC-device, time/calendar, and sensor-stream families
interlock: shared positive status enum, runtime registration of the `sys rtc` record into
`0x00085D58`, and the `sys rtc` / `i2c_n` naming. They most likely form one proprietary platform
layer inside Even Realities' B210 product tree and therefore share one provenance fate.

## Source-admission decision

The low-level initializer has function-local control flow, register/configuration behavior, and
logging structure matching Nordic SDK 17.1.0 `modules/nrfx/drivers/src/nrfx_rtc.c`; OpenR1 uses
that provider rather than recreating it. No exact attributable source was established for the
seven surrounding generic device functions. Their proximity to Nordic code and use of
`nrfx_rtc_*` calls prove a provider dependency, not ownership of the wrapper layer.

OpenR1 therefore:

- compiles Nordic's RTC driver when this hardware service is enabled;
- retains only the fixed R1 record binding through a direct typed interface;
- keeps calendar conversion, named lookup, callback storage/dispatch, and epoch mutation behind an
  abstract provider until source rights are resolved; and
- continues to inject abstract time/calendar values into already implemented health/activity
  behavior rather than cloning this unidentified layer.

This boundary does not authorize a raw clock setter, internal callback-registration command,
rollback bypass, signing bypass, or deployment action.

## Attribution re-examination 2026-08

A second provenance pass re-disassembled the three Ghidra-missed bodies from the rebuilt image,
recovered the `sys rtc` ops table at flash `0x00099C8C` and the const nrfx config at
`0x0009A638`, and tested concrete upstream candidates against fetched sources (RT-Thread v4.0.3
rtc.c, Mac-Rsh mr-library device.c, BabyOS b_device.c, armink ecosystem, Nordic, plus Goodix /
GoMore / HRS3300 / PAH800x / Realtek / Bluetrum / Jieli vendor SDKs). All were structurally
rejected; authenticated code-host searches for the family's rare strings return only this
repository and its mirror. The evidence converges on first-party B210 platform authorship
(Bravechip "ChipletRing", shared with the G2 `platform\threads\thread_manager.c` object already
closed as first-party). Verdict: NO ATTRIBUTION — the family remains
`investigate_before_implementing`. Full report:
[`unknown_rtc_device_provider_candidate-ATTRIBUTION-2026-08.md`](unknown_rtc_device_provider_candidate-ATTRIBUTION-2026-08.md).

## Reduction 2026-08

Under the owner-authorized full reduction (2026-08-14, see
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)), the ten ledger entries of
`unknown_rtc_device_provider_candidate` (the seven generic bodies above plus
the three ops-table veneers at `0x00050DAA..<0x00050DEB`) are reconstructed
from the recovered decompilation evidence as independently compiled C in
[`../../reconstructed/rtc_device/`](../../reconstructed/rtc_device/).  The
reconstruction is not vendor source; it carries per-function provenance
banners, and its contract, reconstruction decisions, divergences (including
the recovered slot-0-only loop-condition quirk), and host-test mapping are
documented in
[`../correlation/RTC-DEVICE-REDUCTION-CORRELATION.md`](../correlation/RTC-DEVICE-REDUCTION-CORRELATION.md).
The ledger disposition for the ten entries is now
`clean_room_reimplementation_owner_authorized`.  This document remains the
provenance record of why no upstream source was admitted; the Nordic
`nrfx_rtc_init` body and the R1 registration wrapper keep their existing
routes.  The generic-registry dependency of the ops veneers was fail-closed
when this section was written; the 2026-08 registry reduction has since
landed, and the host tests now bind the veneers to the reconstructed
registry dispatchers (slots `0x20`/`0x14`) through `rtc_device_bind_registry`.
