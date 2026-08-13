# G2 RTC driver source and dependency closure

Status: fail-closed closure of stock 2.2.6.10
`driver\rtc\drv_rtc.c`, including its production replacement.

## Result

The retained path anchors the complete 130-byte `DRV_RtcSetTime` body at
`[0x0047EE78,0x0047EEFA)`. Its 22-byte alignment and diagnostic literal pool
extends the physical object to `0x0047EF10`, for 152 bytes total. The only
caller is the exterior BL at `0x0044A20C`. All 56 instructions, seven body
calls, five literal pointers, the adjacent RTC initializer and getter, and the
absence of interior calls or stored entry pointers are pinned.

The wrapper maps application fields into a 40-byte Ambiq RTC structure. It
adds 2000 to the input year, computes weekday, fixes the century flag to one
and hundredths to zero, calls the RTC setter, returns zero on success, and
logs then returns one for invalid input.

## Exact third-party identities

The two functional calls are now source-identified:

- `0x004D3CF8` is AmbiqSuite
  `utils/am_util_time.c::am_util_time_computeDayofWeek`. Its exact month table,
  input validation, weekday formula, and shipped leap predicate
  `year % 4 == 0 && (year % 100 != 0 || year % 400 != 0)` match stock.
- `0x004D3ADC` is Apollo510
  `mcu/apollo510/hal/mcu/am_hal_rtc.c::am_hal_rtc_time_set`. Stock also pins
  its validator and decimal-to-BCD helper, register packing, write-enable
  sequence, and status convention.

The selected source-equivalent replay is AmbiqSuite SDK 5.1.0 revision
`release_sdk5p1p0-366b80e084`, public commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. The exact 5.1 source blobs are
`e7b85936…` for `am_util_time.c` and `11c25ce3…` for `am_hal_rtc.c`; sizes,
SHA-256 values, and the corresponding 5.0.0 candidates are recorded in
`g2-drv-rtc-upstream-source.tsv`.

The executable portions used here are unchanged between public 5.0.0 commit
`392042e3…` and 5.1.0; those revisions differ in comments and revision
markers for these files. This object therefore verifies exact source identity
but is not a new version discriminator. The independent stock
`am_hal_sysctrl_sleep` two-WFI behavior remains the proof selecting the 5.1.0
lineage. Because the stock firmware predates the public import, its exact
private pre-release generating commit remains unavailable.

The other five calls are EasyLogger diagnostics at the already selected
2.2.99-equivalent commit `a596b264…`; they add no RTC behavior.

## OpenCFW state

This functional gap is already closed in production. The overlay redirects
the exact 130-byte stock body to `open_cfw_rtc_time_set` in
`components/apollo_main/core_overlay/rtc_time_set.c`. That source incorporates
the calendar utility, HAL validation, BCD conversion, and RTC register writes,
and existing host tests exercise success, invalid dates, the anomalous century
behavior, MMIO order, diagnostics, and overlay placement. Remaining RTC risk
is Apollo510 hardware validation, not opaque third-party logic.

## Reproduction

```sh
make drv-rtc-closure
```

The target authenticates the stock image, manifests, provider bodies, selected
upstream identities, and production route without performing hardware writes.
