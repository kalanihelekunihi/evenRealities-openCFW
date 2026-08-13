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
