# Time/calendar provider boundary

## Outcome

Fourteen recovered functions form one coherent clock-backend, Unix/Gregorian conversion,
timezone, calendar-adapter, and local hour/bucket cluster. Their behavior and exact bodies are
known, but their source ownership is not. They are now isolated as
`unknown_time_calendar_provider_candidate / investigate_before_implementing` rather than left as
anonymous functions or incorrectly declared R1-owned.

OpenR1 does not recreate these bodies. It accepts firmware timestamps, local-day starts, UTC
offsets, hours, and ten-minute bucket indexes through typed caller/provider inputs. In particular,
`r1_activity_consume_delta_event` keeps the bucket resolver abstract. This preserves functional
integration while respecting the requirement to use attributable third-party source if the stock
cluster came from another codebase.

## Exact boundary

| Range | Bytes | Recovered role | SHA-256 |
|---|---:|---|---|
| `0x0005A7BC..<0x0005A8A0` | 228 | Unix seconds to broken-down Gregorian time | `ac4d22d58eb42e36457e68f4b787ccab86ea1a70f840da8c71ddd1c4fe4783ea` |
| `0x0005A8AC..<0x0005A984` | 216 | broken-down Gregorian time to Unix seconds | `c46cb078d69f911a7f4ede4bbd0d0c12ba87b44535d05c615ec3bd44c564af78` |
| `0x0005A990..<0x0005A9B0` | 32 | registered clock-backend snapshot | `c49cbf15c91b3d21c6903b0c9c92d5c2d598c08fcfdd8a032ad85c6ebf9b6a62` |
| `0x0005AC74..<0x0005ACA6` | 50 | local ten-minute activity bucket | `8258898551d51a347e2dc9b680fdcd15334a7d92fcfc67700ba4e952ba2eff79` |
| `0x0005ACA6..<0x0005ACC4` | 30 | local hour | `db2097db7d8c2d10a00813bc7a975efb3d86cc2c3015450f731f54e5adec3c02` |
| `0x0008AD40..<0x0008AD5C` | 28 | local timestamp accessor | `4e3cc9f66d44e4d5151bd11d0193c4c29defd429cad08d6c1b98428b9dae3213` |
| `0x0008AD64..<0x0008AD90` | 44 | local-day start calculator | `014d0d12283782cc42835fcacc42f5da85f00ec083fffffe8cf8d9e6dc5884ef` |
| `0x0008AD98..<0x0008AD9E` | 6 | time-status accessor | `83bf9b6c537471a134b89fdc8be3c871e03df2082c405ecdfaacfaceafedb021` |
| `0x0008ADA4..<0x0008ADAE` | 10 | clock-backend timestamp thunk | `571d07446347362a5115a6a056aecaeef7c5098efd08f2c2aa54a5b85fe8c63f` |
| `0x0008ADB4..<0x0008ADBC` | 8 | signed UTC-offset accessor | `602c8c71b053148eff399239231d18cc077a6d08376289d9e4b489579c05cbcb` |
| `0x0008AE58..<0x0008AEA4` | 76 | calendar-to-UTC adapter | `32b98c5ff754c88c235bede78d917bc7ec7613efbf5328ac53f691d3fc6a7bd7` |
| `0x0008AEA4..<0x0008AEAC` | 8 | time-update flag setter | `e18ee6b3245d02a7240a6dab0254bc5b1818da0263db5fa9871088e533237371` |
| `0x0008AEB0..<0x0008AF38` | 136 | registered clock-backend update adapter | `fe763046ecf9d9a8c09fbf0644ec1bcbd7089faf1d76f669f83dfb18339a0587` |
| `0x0008AF40..<0x0008AF8A` | 74 | UTC-to-calendar adapter | `8442de58aab46b780dbd062ac008e8d7d045982de4f38a484206b3d14feb2b3d` |

## Recovered semantics

- The conversion epoch is 1970-01-01 and every day is 86,400 seconds; leap years use the usual
  divisible-by-4, century, and divisible-by-400 rules.
- The broken-down structure carries second, minute, hour, day, zero-based month, year offset from
  1900, weekday, day-of-year, and a zero tail field.
- The public calendar adapter exposes year, one-based month, day, hour, minute, second, and weekday.
- UTC conversion applies a signed offset in minutes. Local-hour and activity-bucket helpers sample
  the current offset, convert the timestamp, and return hour or `hour*6 + minute/10`.
- Local-day start derives the offset-adjusted day boundary from the current backend timestamp.
- The time-update adapter uses a registered backend operation table and preserves its one-shot
  backend synchronization state. Those indirect operations are not replaced by guessed code.

## Source-admission result

The pinned Nordic nRF5 SDK 17.1.0 tree has no matching calendar implementation. Primary-source
comparisons against [U-Boot's RTC date conversion](https://android.googlesource.com/platform/external/u-boot/+/refs/heads/android-tv-s-beta3/drivers/rtc/date.c)
and [musl's seconds-to-`tm` implementation](https://fuchsia.googlesource.com/zircon/+/13ee3dc5e4c46bf127977ad28645c47442ec517d/third_party/ulib/musl/src/time/__secs_to_tm.c)
show only generic Gregorian concepts, not a function-local source match. Generic constants such as
1970, 365/366, and 86,400 cannot establish authorship, version, or license.

Admission therefore requires one of:

1. an attributable source/version/license match for these exact bodies; or
2. an explicit clean provider replacement selected independently of the stock implementation.

Until then, the boundary remains abstract and implementation-blocked. It has no relationship to
firmware signing, rollback, boot validation, ACLs, or protection state.
