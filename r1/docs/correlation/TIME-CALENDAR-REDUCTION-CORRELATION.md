# Time/calendar reduction correlation (owner-authorized, 2026-08)

## Decision

Under the "Owner-authorized full reduction (2026-08-14)" section of
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), the sixteen-function
family `unknown_time_calendar_provider_candidate` is reduced from the
recovered decompilation evidence to compilable C at
[`../../reconstructed/time_calendar/`](../../reconstructed/time_calendar/).
The reconstruction is not vendor source and is never presented as such;
every file carries the provenance banner.  The ledger disposition for the
sixteen entries becomes `clean_room_reimplementation_owner_authorized` when
the integrator wave re-pins it.  The boundary doc
[`../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md`](../boundaries/TIME-CALENDAR-PROVIDER-BOUNDARY.md)
remains the provenance record of why no upstream source could be admitted.
The 2026-08-14 "Route decision" in that doc replaced openR1's *need* for the
family (toolchain `gmtime`, no calendar→epoch consumer, R1-owned clock
production); this reduction covers the family itself, and the two tracks are
reconciled by the integrator.

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Evidence extraction path

- Ghidra bodies: `research/decompilation/application/decompiler-output.c`
  (all sixteen entries present).
- Every body was cross-checked against fresh Thumb disassembly from the
  byte-exact rebuilt image (`research/decompilation/rebuild/rebuilt-application.bin`)
  with GNU `arm-none-eabi-objdump` (`-M force-thumb`, VMA adjusted to the
  `0x00027000` load base).  The disassembly resolved every literal pool the
  decompiler left as `DAT_` symbols and corrected two Ghidra renderings
  (dead stack initializations in `0x0008AD08`; the `-flag & backend`
  instruction pair in `0x0005A990`).
- Recovered data read directly from the image: the two identical private
  24-byte dual month tables at `0x00099C5C` (forward converter) and
  `0x00099C74` (inverse converter), bytes
  `1f 1c 1f 1e 1f 1e 1f 1f 1e 1f 1e 1f` (non-leap) then
  `1f 1d 1f 1e 1f 1e 1f 1f 1e 1f 1e 1f` (leap).  These are evidence-derived
  data, embedded as C arrays; they are not authored content.
- Callee attribution (`research/decompilation/application/functions.csv`
  plus the RTC-device correlation): `0x0002754A` = toolchain signed 64-bit
  division (`__aeabi_ldivmod`-family; quotient r0:r1, remainder r2:r3),
  `0x000277AA` = `memset(dst, 0, n)` thunk, `0x0005A7BC`/`0x0005A8AC` =
  this family's own converters.  All state roots are family-local globals:
  time state `0x20016AC4`, registration/sync root `0x20006820` (snapshot
  sub-record at `+0x0C` = `0x2000682C`), static fallback broken-down buffer
  `0x20016AE4`.

## Recovered layout

Time state root (`0x20016AC4`): `+0x08` signed int16 UTC offset in minutes,
`+0x0A` registered flag, `+0x0B` time-update/status byte, `+0x0C..+0x1F`
20-byte packed-datetime cache block invalidated as one memset:
`+0x10` uint32 cached local-day start (UTC epoch), `+0x14` uint16 year,
`+0x16` month (1-based), `+0x17` day, `+0x18` hour, `+0x19` minute,
`+0x1A` second, `+0x1B` weekday, `+0x1C` cache-valid byte.

Registration/sync root (`0x20006820`): `+0x00` one-shot sync-pending flag,
`+0x04` preserved pre-update backend timestamp, `+0x08` backend operations
record used by the timestamp thunk and local-timestamp accessor,
`+0x0C` snapshot registered flag, `+0x10` snapshot backend operations
record, `+0x14` backend context pointer.  Backend operations record:
`+0x08` get-timestamp (one context argument), `+0x10` update
(epoch, offset, context).

Broken-down time: nine 32-bit words — second, minute, hour, day of month,
zero-based month, year offset from 1900, weekday (Sunday = 0), zero-based
day-of-year, zero tail.  Public packed datetime (8 bytes): uint16 full
year, then one-based month, day, hour, minute, second, weekday.  The
reconstruction static-asserts every recovered offset for the 32-bit target
ABI only.

## Per-function contract and reconstruction decisions

| Stock extent | Bytes | Reconstructed symbol | Contract |
| --- | ---: | --- | --- |
| `0x0005A7BC..<0x0005A8A0` | 228 | `time_calendar_unix_to_broken_down` | unsigned epoch → nine-word struct; iterative 1970 year walk with leap-year early break (day 365 stays in a leap year); month-subtraction walk over the private table with `uxtb` counter; `wday = (days + 4) % 7`; NULL output falls back to one shared static buffer; returns the filled struct |
| `0x0005A8AC..<0x0005A984` | 216 | `time_calendar_broken_down_to_unix` | hard validation, -1 on failure: NULL, `tm_year ∉ [70,129]` (1970-2029), `mon > 11`, `mday ∉ [1,31]`, `hour > 23`, `min/sec > 59`; day-of-month is NOT checked against month length (recovered laxity); day sum + 86400/3600/60 composition |
| `0x0005A990..<0x0005A9B0` | 32 | `time_calendar_backend_snapshot` | returns 0 unless registered flag and snapshot backend are both non-zero (stock: `negs`/`tst` pair `(-flag) & backend`); stores backend and context through individually optional outputs, returns 1 |
| `0x0005AC74..<0x0005ACA6` | 50 | `time_calendar_activity_bucket` | `(hour * 6 + minute / 10) & 0xFF` of the offset-adjusted local time; conversion result ignored (zeroed record ⇒ 0) |
| `0x0005ACA6..<0x0005ACC4` | 30 | `time_calendar_local_hour` | local hour byte of the offset-adjusted time; 0 on failure |
| `0x0008AC28..<0x0008ACF2` | 202 | `time_calendar_local_datetime_fill` | no-op unless registered and out non-NULL; local = timestamp + offset·60 as signed 64-bit; date cache reconverted (via the 32-bit-wrapped local epoch) only when the local-day start changes; time fields recomputed per call from the signed remainder with UNSIGNED division (recovered quirk); copies the two packed cache words out |
| `0x0008AD08..<0x0008AD3C` | 52 | `time_calendar_backend_calendar_lookup` | 0 unless registered and out non-NULL; snapshot must succeed with non-NULL backend and get op; converts `get(context)` with the current offset |
| `0x0008AD40..<0x0008AD5C` | 28 | `time_calendar_local_timestamp` | `get(NULL) + offset·60`, 32-bit wrap |
| `0x0008AD64..<0x0008AD90` | 44 | `time_calendar_local_day_start` | signed 64-bit truncating day division of `timestamp + offset·60`; returns `quotient·86400 − offset·60` with the recovered borrow-free high word |
| `0x0008AD98..<0x0008AD9E` | 6 | `time_calendar_status` | state byte `+0x0B` |
| `0x0008ADA4..<0x0008ADAE` | 10 | `time_calendar_backend_timestamp` | tail call `get(NULL)` through the `+0x08` record (recovered: constant 0 context, not the bound one) |
| `0x0008ADB4..<0x0008ADBC` | 8 | `time_calendar_utc_offset` | sign-extended int16 offset in minutes |
| `0x0008AE58..<0x0008AEA4` | 76 | `time_calendar_to_utc` | packed datetime → inverse converter (byte-to-word subtractions wrap into validation failures); -1 maps to 0; success returns `epoch − offset·60` |
| `0x0008AEA4..<0x0008AEAC` | 8 | `time_calendar_set_time_update_flag` | state byte `+0x0B` = 1 |
| `0x0008AEB0..<0x0008AF38` | 136 | `time_calendar_backend_update` | requires registered flag, snapshot backend, and update op; a changed offset (full 32-bit compare, int16 store) invalidates the cache BEFORE the backend call on both result paths; while `sync_pending != 1` samples `get(context)` once; calls `update(epoch, offset, context)`; on a nonzero result invalidates the cache again and, iff it sampled, stores the pre-update timestamp and sets `sync_pending = 1`; returns the backend result |
| `0x0008AF40..<0x0008AF8A` | 74 | `time_calendar_utc_to_calendar` | `epoch + offset·60` with 32-bit wrap, forward conversion, packs the 8-byte datetime; 0 on NULL out |

## Divergences from the stock binary (all deliberate)

1. **Explicit backend binding.**  Stock reaches the clock backend through
   shared globals written by the (out-of-family) generic-registry
   registration path and dereferences them unchecked; several bodies fault
   when unbound.  The reconstruction binds the backend operations table and
   context through `time_calendar_bind_backend` (which raises the two
   recovered registered flags) and every backend-dependent path fails
   explicitly with the family's recovered failure value (0) when unbound.
2. **NULL guards.**  Stock already checks the packed-datetime out pointers
   (`0x0008AC28`, `0x0008AD08`, `0x0008AF40`), the calendar input
   (`0x0008AE58`), and the inverse-converter input (-1).  The
   reconstruction adds the same failure-value returns for a NULL module
   pointer everywhere; the forward converter's epoch input is passed by
   value (stock took a pointer it dereferenced unchecked — observable
   behavior for every defined input is unchanged).
3. **Snapshot condition rendered as a boolean test.**  Stock's
   `negs`/`tst` pair computes `(-flag) & backend != 0`; for flag values
   above 1 that is a bitmask test, not a conjunction.  The flag is written
   only with 1 by every observed path, so the reconstruction uses
   `flag == 0 || backend == NULL`, observably identical on every
   stock-reachable state.
4. **The 64-bit helpers are C arithmetic.**  Stock calls the toolchain
   signed `ldivmod` and unsigned 32×32→64 multiply; the reconstruction
   expresses the identical operations in C (including the truncating
   division, the unsigned division of the signed remainder, and the
   borrow-free high word) and relies on the same toolchain runtime on
   target.
5. **No libc.**  The 20-byte cache invalidation (stock `memset` thunk) is a
   local byte loop over the recovered field span (`reserved_0c`..end, which
   is exactly `+0x0C..+0x1F` on the 32-bit target ABI), matching the r1
   freestanding no-`string.h` convention.

Preserved exactly: the 1970 epoch and 86400-second day, the Gregorian
leap rule including the leap-year day-365 early break, the `(days+4)%7`
weekday, the `uxtb` month-walk counter, the 1970-2029 validation window
and its exact bounds, the day-of-month laxity, both private month tables,
the signed-minute offset applied as `offset·60` with 32-bit wrap in the
adapters and as signed 64-bit in the day-boundary paths, the
signed-remainder/unsigned-division time-of-day quirk, the cache
invalidation span and ordering (including invalidation on offset change
before a failing update), the one-shot sync-state preservation, the
NULL-context thunk versus bound-context snapshot split, and the int16
truncation of a stored offset against the full 32-bit comparison.

## "Docs describe intent, binary does less" notes

- The boundary doc's "registered clock-backend lookup" (`0x0008AD08`)
  reads, in the binary, as: registered-flag check → snapshot → backend get
  op → UTC-to-calendar adapter.  There is no registry search; the
  "lookup" is the two-slot registration record read.  Reconstructed as
  such.
- The cached datetime fill's "cache" is only a day-granularity date cache;
  the time-of-day is always recomputed.  Documented above.
- The inverse converter's "1970-2029 hard-validation bound" is the only
  range policy in the binary; nothing validates February 29 or 31-day
  months.  Preserved, not fixed.

## Host test mapping (`tests/test_reconstructed_time_calendar.c`)

- `test_time_calendar_unix_to_broken_down`: civil-time vectors (leap 2000
  including the day-365 early break, 2016, non-leap 2100, 30/31-day
  months, year rollover, `0xFFFFFFFF` wraparound to 2106-02-07 06:28:15),
  the shared static fallback buffer, and a host-`gmtime` cross-check sweep.
- `test_time_calendar_broken_down_to_unix`: epoch/frontier values
  (0 and 2029-12-31 23:59:59 = 1893455999), leap dates, round-trip sweep,
  every validation boundary (NULL, year 69/130, month 12, day 0/32,
  hour 24, minute/second 60), and the recovered 1970-02-31 laxity.
- `test_time_calendar_backend_snapshot`: unregistered failure with
  untouched outputs, bound success, optional outputs, unbind.
- `test_time_calendar_utc_to_calendar` / `test_time_calendar_to_utc`:
  zero/±offset conversions including the recovered negative-offset 32-bit
  wrap to 2106, civil vectors, failure mapping to 0, and a round-trip
  sweep.
- `test_time_calendar_local_hour_and_bucket`: bucket boundaries
  (09:59 → 59, 10:00 → 60, 23:59 → 143), ± offsets, and the wrapped-epoch
  bucket.
- `test_time_calendar_backend_accessors`: thunk (NULL context pinned),
  local timestamp, UTC-offset accessor, status accessor/flag setter, and
  local-day starts under 0/+120/−300 minute offsets.
- `test_time_calendar_backend_calendar_lookup`: unregistered/NULL/no-get
  failures, bound success with the bound context, offset rollover.
- `test_time_calendar_local_datetime_fill`: untouched output when
  unregistered, packed-word values, same-day cache hold, next-day
  reconversion, and the recovered negative-local-epoch quirk (date from
  the 32-bit-wrapped epoch, hour 85 from the unsigned-divided signed
  remainder).
- `test_time_calendar_backend_update`: unregistered/no-update failures,
  success path (offset store, double cache invalidation, one-shot
  pre-update timestamp), one-shot non-overwrite, failed update with
  changed offset (offset and invalidation still applied, sync state
  untouched), int16 offset truncation against the full 32-bit argument,
  and the no-get-op sample-0 path.

## Integration state

The module carries no dependency outside its own state: the only external
seam is the bound clock backend (`get`/`update` operations plus context),
which on target is the interlocked generic-registry/RTC-device path — both
families are reduced in the same owner-authorized wave and the integrator
wires the binding.  The host harness compiles the unit with the strict r1
flags and with ASan/UBSan, and the freestanding Cortex-M4 object gate
(`clang --target=armv7em-none-eabi -mcpu=cortex-m4 -ffreestanding
-fno-builtin`, exact r1 Makefile flags) builds it cleanly; the 32-bit
layout static asserts engage under that target. The source-built Zephyr target
now adopts `time_calendar_unix_to_broken_down` for its local `struct tm` query
and health local-day boundary calculation. Its epoch source remains the
product-owned phone-synchronized monotonic clock; the generic-registry and
RTC-device backends are not activated. Nothing here exposes a raw clock setter,
a dispatch command, or any security-relevant behavior. The legacy Nordic SDK
target retains its independently admitted toolchain-`gmtime` replacement.

The immutable byte pins in `tools/verify_openr1.py`
(`time_calendar_boundary_expected`, the sixteen-entry provider count, and
the boundary-doc markers) continue to pin the stock extents against the
rebuilt image; the integrator wave updates the disposition expectations
when the ledger rows flip to
`clean_room_reimplementation_owner_authorized`.
