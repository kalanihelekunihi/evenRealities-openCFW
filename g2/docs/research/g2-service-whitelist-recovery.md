# G2 `service_whitelist.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained path is
`platform\service\message_notify\service_whitelist.c`. Five path-bearing
functions and two adjacent pathless helpers form one closed seven-function
object at `[0x004D5930,0x004D6BA8)`. Function bodies contribute 4,310 bytes
with SHA-256
`dcf6b92f4d9d8ff841302754b9630848be3a517233babaec071a9f48194c7795`;
six alignment/literal regions contribute 418 bytes with SHA-256
`fd98d25dca58521e89889e939241d4b71e3efd7bf899a24c55d43388323cfed6`.
The complete 4,728-byte physical object has SHA-256
`7b35909883910abf830ae2274783a7a265c4ea1364fe3b88f7dda5956d4f07aa`.
The preceding bytes are the prior object's mode-string pool and an unrelated
Thumb prologue begins at `0x004D6BA8`, closing both boundaries.

Five exact function names survive as diagnostic strings. The two restored
semantic helpers are a seek-preserving file-size routine at `0x004D5930` and
a cached-CRC accessor at `0x004D6A20`. The exact byte ledger is pinned in
`tools/manifests/g2-service-whitelist-function-map.tsv`.

## Persistent layout and loading

`SVC_WhitelistManagerInit` clears the 8,002-byte state at `0x20054718`, loads
`user/notify_whitelist.json`, and prints the resulting configuration. The
state layout is:

| Offset | Meaning |
| ---: | --- |
| `0` bits 0..4 | call, message, iOS mail, calendar, and application enables |
| `1` | application count, capped at 100 |
| `2` | first application record |

Each application record is 80 bytes: a 64-byte identifier followed by a
16-byte display name. The parser reads `call_enable`, `msg_enable`,
`calendar_enable`, `ios_mail_enable`, and `enable`; only JSON Boolean true
sets a flag. Missing required nodes fail the load. The application array is
named `list`; malformed entries are skipped and a count above 100 is
truncated.

The filesystem loader preserves the stream position while measuring the file,
rejects non-positive sizes, and uses a shared buffer below 8,503 bytes or a
heap allocation otherwise. It NUL-terminates the bytes before JSON parsing.
On success it stores CRC-32 at `0x200749A4` and sets the valid byte at
`0x2007501B`; every failure clears the valid byte. The cached-CRC accessor
requires both a non-null output pointer and that valid byte. The manager's
retained maximum-buffer diagnostic is 8,003 bytes.

## Identifier policy

`SVC_IsOnWhitelistByIdentifier` returns three observed values:

| Value | Meaning |
| ---: | --- |
| `0` | invalid input |
| `1` | blocked |
| `2` | allowed |

Whitelist disablement is fail-open and returns allowed. Null identifiers and
identifiers of 64 bytes or more are invalid. `com.even.sg` and `com.even.g1`
are always allowed. When the application-enable bit and application count are
both nonzero, the function walks the 80-byte records and compares each stored
identifier with the input using the stored identifier's length; a match is
allowed. Otherwise it logs and returns blocked.

The two external identifier consumers are the Android notification path at
`0x0048E750` and another notification path at `0x004BF34A`. The CRC accessor
is consumed by the already-closed whitelist-check protobuf encoder at
`0x004D776E`. Initialization has two external calls at `0x0048E1F8` and
`0x0048E340`.

## Ingress and ownership

Across the image, nine `BL` encodings target exact entries: five external and
four within this object. The seven bodies contain 264 direct call sites. No
stored function pointer, direct branch, or `B.W` targets an entry or strict
interior. The only all-byte entry/interior numeric window is the unaligned
four-byte sequence at `0x0064CF9B`, inside packed data; it is not a pointer or
control-flow instruction. Real strict-interior ingress is therefore zero.

The historical source tree and license remain unavailable, so this closure is
binary evidence rather than source ownership. No clean-room candidate exists,
the object is absent from `overlay.json`, and OpenCFW claims zero production
bytes. The next retained-path target is chosen from the refreshed first-party
frontier rather than inferred from address adjacency.
