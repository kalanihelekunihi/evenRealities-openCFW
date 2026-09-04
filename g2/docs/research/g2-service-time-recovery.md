# G2 time-service object and dependency recovery

Status date: 2026-08-11  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Retained path: `platform\service\time\service_time.c`

## Result

The complete object is `[0x00449ED4,0x0044A43C)`: eleven primary functions /
1,308 body bytes plus a 76-byte trailing pool, for 1,384 physical bytes. It
starts immediately after the closed CMSIS-FreeRTOS object and ends exactly at
the separately identified IAR `strlen` body. This adjacency does not indicate
shared ownership: the time service makes zero direct CMSIS-FreeRTOS calls and
contains no IAR implementation body.

The original retained-path census found two functions / 438 bytes. One missed
epoch-to-calendar body and eight discovered but unanchored helpers expand the
complete inventory to eleven functions. The closure pins 45 body calls, 64
direct BL entry sites, six stored Thumb pointers, both raw path references,
the pool and both neighboring boundaries.

## Calendar contract

The first eight functions implement G2 calendar and RTC policy:

- two Unix-seconds-to-calendar conversions, one fixed to 24-hour output and
  one respecting the configured 12/24-hour mode;
- calendar-to-Unix conversion and two small wrappers;
- current calendar and current Unix-time getters over the first-party RTC
  adapter; and
- a small refresh wrapper.

The authenticated literal pool fixes the conversion epoch and units:

| Field | Value |
|---|---:|
| Unix seconds at 2000-01-01 | `946684800` (`0x386D4380`) |
| Seconds per day | `86400` (`0x15180`) |
| Days from 1970-01-01 to 2000-01-01 | `10957` |
| Timezone unit | 900 seconds / 15 minutes |
| Calendar record size | 40 bytes |

The two exact service identities are `SVC_SystemTimeSync` at `0x0044A1FE`
and `RPC_SystemTimeSync` at `0x0044A2B2`. The latter builds a 16-byte peer
message and registers its callback; the final function clears that pending
timeout after refreshing local state.

One external BL at `0x00554914` enters `0x00449F22`, a compiler-produced
alternate label inside the first calendar converter. It reuses caller-prepared
state and the converter tail, so it is recorded as an alternate interior entry
rather than double-counted as another body. Six aligned stored pointers select
the RPC sync entry or lifecycle callback; no indirect call occurs in the
object itself.

## Dependency origin and version

All 34 external direct calls partition into:

- ten EasyLogger diagnostic calls at the admitted 2.2.99-compatible selected
  core `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`;
- eight calls to bounded/source-recreated IAR `memcpy`, aligned-copy, and
  `memset` entries; and
- sixteen first-party calls for RTC access, role/format policy, peer transport,
  and timeout registration.

The calendar arithmetic uses conventional Gregorian/Unix constants but has no
linked library call, retained upstream path, or distinguishing public-source
fingerprint. It is therefore assigned to the retained G2 source rather than
speculatively attributed to a libc or time utility. No third-party definition,
new family, or version discriminator is embedded.

The RTC providers are first-party wrappers over the already selected Apollo510
RTC boundary. This object does not add a direct Ambiq HAL call and cannot narrow
the selected AmbiqSuite lineage or recover a private generating commit.

## OpenCFW boundary

The complete 1,308-byte stock body is production-routed through eleven
selector-isolated clean-room C leaves. They compile to 1,658 Apple-profile
bytes and 1,648 Linux-profile bytes under 27 strict relocations; the 76-byte
diagnostic/literal pool remains retained. The source implements the exact
40-byte calendar and 16-byte peer-message ABIs, Gregorian conversion,
hundredths rounding, configured 12/24-hour display, signed quarter-hour
timezone adjustment, RTC refresh, role-gated synchronization, and the
30-second callback/retry lifecycle. Diagnostic-only EasyLogger calls are
deliberately omitted.

Host tests cover pre-2000 clamping, leap-day conversion, epoch round trips,
midnight/afternoon 12-hour formatting, timezone direction, RTC get/set,
peer-role gating, the 16-byte transport payload, delayed retry, and immediate
callback retry. Both canonical toolchain profiles compile and route every
entry into the complete fixed-size firmware image. Live RTC behavior, peer
transport interoperability, scheduler timing/concurrency, and bilateral time
synchronization remain blocked by unavailable physical evidence; no hardware
operation was attempted.

## Reproduction

Run:

```sh
make service-time-closure
```

`tools/analyze_g2_service_time.py` authenticates the stock image and manifests,
re-decodes all 497 instructions, validates the epoch constants and exact
symbols, replays primary/alternate/stored ingress, accounts for every provider
edge, verifies the CMSIS/IAR neighboring boundaries, and fail-closes on source,
relocation, routing, component, manifest, or package drift. The target also
runs the host oracle and final-frontier gate. It performs no signing, flashing,
erase, or hardware operation.
