# Attribution re-examination: `unknown_time_calendar_provider_candidate` (2026-08)

## Scope

- Family: `unknown_time_calendar_provider_candidate`, disposition `investigate_before_implementing`.
- 16 functions, 1,422 bytes total, two address clusters:
  - `0x0005A7BC..<0x0005ACC4`: Unix↔Gregorian converters, backend snapshot, local hour / 10-minute bucket helpers.
  - `0x0008AC28..<0x0008AF8A`: clock-backend registry accessors, UTC-offset (signed int16 minutes) accessors, calendar adapters, packed-datetime cache fill.
- This report does not modify the ledger, generators, or sources. It re-tests upstream-origin hypotheses against real upstream code fetched in August 2026 and builds on `TIME-CALENDAR-PROVIDER-BOUNDARY.md` (which had rejected modern newlib, Zephyr, musl, u-boot, Mynewt, NuttX, BES, avr-libc/picolibc).

## Methods

1. Extracted the family list from `r1/docs/reference/FUNCTION-OWNERSHIP.csv` (16 rows).
2. Read the Ghidra bodies in `r1/research/decompilation/application/decompiler-output.c` (FUN_0005a7bc at line 51231, FUN_0005a8ac at 51288, adapters at 103666..104005) and cross-checked `FUN_0005a8ac` against `disassembly.s` at `0x0005a8ac` (bounds `0x46/0x3c`, `0xc`, `0x1f`, `0x18`, `0x3c`, `0x3c`; dual-table `ldrb` walk with `+0xc` leap row; final `sec + (days+mday-1)*86400 + hour*3600 + min*60` confirmed instruction-level).
3. Call topology from `call-graph.csv` (converters called only from the family's own adapters, confirming a private second implementation beside armlib `gmtime` at `0x000276C8`).
4. Fetched and compared actual upstream sources (URLs below); authenticated GitHub code search (`gh search code`) for distinctive fingerprints.

## Fingerprint of the stock converters

`FUN_0005a7bc` (secs→tm, 228 B): NULL result arg → static buffer at `0x20016AE4`; hour/min/sec decomposition; `tm_wday = (t/86400 + 4) % 7`; year loop from 1970 subtracting 365/366 with `((y&3)==0 && y%100!=0) || y%400==0`; month walk over a private 24-byte dual `uint8_t[2][12]` table (`0x00099C5C`) with `for (i=0; table[i] <= days; i++) days -= table[i];`; fills 9-word `struct tm` `{sec,min,hour,mday,mon,year-1900,wday,yday,0}`; returns the result pointer.

`FUN_0005a8ac` (tm→secs, 216 B): returns −1 unless `tm_year∈[70,129]` (1970–2029), `mon≤11`, `mday∈[1,31]`, `hour≤23`, `min,sec≤59`; day-count year loop from 1970; month accumulation over its own private copy of the dual table (`0x00099C74`); `sec + (days+mday-1)*86400 + hour*3600 + min*60`.

## Hypotheses tested (all with fetched primary sources)

| Candidate | Result | Key evidence |
|---|---|---|
| Old newlib `_mktm_r` (newlib ≤ 2.x, e.g. [newlib-nano-1.0 `newlib/libc/time/mktm_r.c`](https://github.com/32bitmicro/newlib-nano-1.0/blob/master/newlib/libc/time/mktm_r.c), itself "Adapted from tzcode maintained by Arthur David Olson") | **Compatible-interval match for FUN_0005a7bc only** | Identical weekday formula `(EPOCH_WDAY + days) % DAYSPERWEEK` (EPOCH_WDAY=4), identical month-walk loop shape and direction (`days >= ip[tm_mon]`), identical field derivation (`tm_year = y - YEAR_BASE`, `tm_yday = days`, `tm_mday = days + 1`), `tm_isdst = 0` on the gmtime path, returns `res`. Verified case analysis (days=365/366 in leap and non-leap years) shows outputs identical for all t ≥ 0. Differences: upstream `mon_lengths` is `int[2][12]` (stock: `uint8_t`), upstream handles negative times (stock: unsigned), upstream has no NULL→static fallback, and newlib's `mktime` is an iterative normalizer — nothing like FUN_0005a8ac. |
| FSF glibc 1.x `__tm_conv` lineage via ELKS ([`libc/time/tm_conv.c`](https://github.com/ghaerr/elks/blob/master/libc/time/tm_conv.c), "adapted from glibc", Copyright 1991,1993 FSF) | Partial | `static const char __mon_lengths[2][12]` (byte-width table, like stock), `(4 + days) % 7`, year loop, same month walk. Differences: `tm_isdst = -1` (stock 0), extra `offset` parameter, negative handling, returns void. |
| Pebble smartwatch FW ([`google/pebble src/fw/util/time/time.c`](https://github.com/google/pebble/blob/master/src/fw/util/time/time.c)) | Partial — closest single kin | `static const uint8_t s_mon_lengths[2][MONTHS_PER_YEAR]` — same element width as stock; identical year loop and month walk; `(EPOCH_WDAY + days) % DAYS_PER_WEEK`. Differences: extended `struct tm` (`tm_gmtoff`, `tm_zone`), timezone/DST logic, negative handling, no static fallback, and no mktime body in-tree (declared in `time.h`, resolved from toolchain). |
| RT-Thread [`components/libc/compilers/common/ctime.c`](https://raw.githubusercontent.com/RT-Thread/rt-thread/master/components/libc/compilers/common/ctime.c) | Partial | Same year loop (`for (i=1970;;++i){k=isleap?366:365; if(work>=k) work-=k; else break;}`) and `(4 + work) % 7`. Different month method (cumulative `short __spm[13]` + Feb-29 special case), NULL→EFAULT (no static fallback), `timegm` normalizes out-of-range fields instead of hard-validating. |
| Micrium/Silabs μC/Clk V3.10.00 ([weston-embedded/uC-Clk `Source/clk.c`](https://raw.githubusercontent.com/weston-embedded/uC-Clk/master/Source/clk.c)) | **No match** | Epoch 2000-01-01 (`Clk_TS_UTC_sec` "Clk epoch = 2000-01-01 00:00:00 UTC"), own `CLK_DATE_TIME` struct (not `struct tm`), year caches, different handlers. Only the universal `[2][12]` days-in-month table shape coincides. |
| Nut/OS ([crt/gmtime.c via ethernut.de API docs](https://www.ethernut.de/api/gmtime_8c_source.html)) | **No match** | 4-year-cycle division (`_FOUR_YEAR_SEC`), cumulative `_days/_lpdays` tables, `int` return, no year loop. |
| uClibc-ng ([`libc/misc/time/time.c`](https://raw.githubusercontent.com/wbx-github/uclibc-ng/master/libc/misc/time/time.c)) | **No match** | Manuel Novoa III adaptive algorithm (`_time_t2tm`, `rule_struct` TZ engine, `day_cor` table); wholly different architecture. |
| ALIENTEK-style `rtc.c` lineage incl. WCH ([openwch/ch32v307 `EVT/EXAM/RTC/RTC_Calendar/User/main.c`](https://raw.githubusercontent.com/openwch/ch32v307/main/EVT/EXAM/RTC/RTC_Calendar/User/main.c)) | Partial (year loop only) | Year loop `while(temp>=365){ if(Is_Leap_Year){ if(temp>=366) temp-=366; else break; } else temp-=365; temp1++; }` is structurally the stock loop, and the public 8-byte packed datetime (`year u16, mon, mday, hour, min, sec, week`, 1-based month — stock `FUN_0008af40` output layout) resembles `_calendar_obj`. But: single `mon_table[12]` + leap-February special case (not dual table), seconds-accumulating `RTC_Set` valid to **2099** (stock: days-accumulating, **2029**), weekday via `table_week` Zeller-style formula (stock: `(days+4)%7`), no `struct tm`. |
| Xilinx RTC PSU driver ([`embeddedsw .../rtcpsu/src/xrtcpsu.c`](https://raw.githubusercontent.com/Xilinx/embeddedsw/master/XilinxProcessorIPLib/drivers/rtcpsu/src/xrtcpsu.c)) | No match | Same general idiom (EPOCH_WDAY, year loop) but single `DaysInMonth[]` + Feb adjustment, own `XRtcPsu_DT` struct, no validation bounds; wrong ecosystem. |
| Arduino TimeLib `breakTime` | No match | `(time+4)%7` wday and year loop, but single `monthDays[]` + Feb case, `tmElements_t`, year offset from 1970 as uint8. |
| Boundary doc's prior rejections (modern newlib/Zephyr Hinnant, musl, u-boot, Mynewt, NuttX, BES, avr-libc/picolibc) | Confirmed; not re-litigated | — |

## Distinctive-fingerprint code searches (authenticated GitHub, 2026-08-14)

- `"tm_year > 129"`, `mktime 2029`, `RTC_Set 2029` → zero matches (consistent with the boundary doc's Sourcegraph zero). The 1970–2029 validation window appears unique to this firmware.
- `mon_lengths` census locates every public embedder of the dual-table idiom (unbound, gdal, MySQL/MariaDB tztime, ELKS, Pebble, Xen, f32c, SoftEther, OpenBSD strptime, tzcode) — none matches the stock bodies.
- Platform-vendor probes `"sys rtc"`, `eAT at_system`, `thread_manager.c`, `at_system.c` → only this repository and its mirrors, or unrelated projects. No public SDK carries the B210 `platform/` tree naming.

## Verdict

**(c) NO ATTRIBUTION — the family remains proprietary / implementation-blocked.**

The seconds→broken-down converter is a byte-table, static-fallback variant of the widely-copied glibc-1.x `__tm_conv`/old-newlib `_mktm_r` idiom, behaviorally identical to old newlib's `gmtime_r` path on its entire input domain; that idiom is available under permissive (BSD/MIT-class) licenses from multiple of the compared projects. However:

- no public source matches the exact stock bodies (table width, fused static-buffer fallback, no negative handling);
- the inverse converter with its 1970–2029 hard-validation policy has no public counterpart at all;
- the 12 registry/adapter/accessor functions interlock with the blocked generic device-registry, RTC-device, software-TWI, and sensor-stream families (`sys rtc` naming, shared positive status enum) and show the same proprietary B210 platform authorship.

Admission path therefore stays as recorded in `TIME-CALENDAR-PROVIDER-BOUNDARY.md`: either an exact attributable source appears (none found as of 2026-08), or an explicit clean provider replacement is selected independently. If route (2) is ever taken for the converter pair, old newlib's `_mktm_r`/`gmtime_r` (BSD-licensed) is a behaviorally verified functional equivalent for the seconds→tm direction — but adopting it would be a *replacement*, not an attribution of the stock code, and the mktime-direction validation policy (2029 bound, −1 contract) would still be vendor-specific behavior to be preserved deliberately, not cloned.

This report makes no change to admission state and authorizes no implementation.

## Acquisition route (2026-08-14 re-check)

With the public-source hypothesis space exhausted, route (c) — commercial acquisition — is
the only remaining attribution path, with a named counterparty. Request the platform
SDK/source (or a license statement) from Wuxi Bravechip Technologies (public business
contact per the `BravechipSpace/ChipletRing-APPSDK` README: xiaojian.cui@bravechip.com) or
through the ring ODM, covering the `platform\` tree including the calendar converters.
Forensic fallback: analyze the Bravechip ring OTA images shipped in the APPSDK
(`2.4.4.81.hex16`-style files, apparently obfuscated/encrypted) for shared platform code.

Public-source exhaustion evidence (2026-08-14), complementing the code-search results above:

- `BravechipSpace/ChipletRing-APPSDK` (fetched to `~/vendor-cache/chiplet-ring-appsdk`,
  default-branch HEAD) is phone-side only: `IOS/library`, `IOS/example`, `Android`, `Doc`.
  Grep of all `*.h`/`*.m`/`*.c`/`*.java`/`*.md`/`*.txt` for `sensor_stream`, `soft_twi`,
  `sw_i2c`, `rtc_device`, `BCL603`, `603M`: zero hits. No firmware-side source exists in
  Bravechip's public footprint.
- The BravechipSpace GitHub org contains only that repository plus a react fork.
- A second Bravechip-based ring product (`thuhci/OpenRing`, Tsinghua τ-Ring, depending on
  `ChipletRing1.0.81.aar`) also ships no firmware source.
- Bravechip's official site download list (bravechip.com) offers app SDKs, app notes, and
  datasheets only; the ring firmware is pre-loaded and closed.
- Gitee code search remains login-walled (the same blocker recorded in the
  generic-device-registry report).
- `Mentra-Community/MentraOS` `R1.kt` independently carries the same BAE8 UUIDs —
  corroboration of the platform identification, not a source route.
