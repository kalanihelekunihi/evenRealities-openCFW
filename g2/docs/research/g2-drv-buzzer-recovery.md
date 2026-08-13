# G2 buzzer-driver recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`driver\buzzer\drv_buzzer.c` owns 17 linked bodies and four non-code regions
in the physically bounded object `[0x005026BC,0x00502D58)`. The bodies total
1,520 bytes, SHA-256
`485d4b4858a0fcb6ab2a502d430cbcea4cb6d12796f18fe15a1d10573b8ef1e5`.
The 172 non-code bytes contain alignment, a `100.0f` constant, the main
literal pool, and final alignment. The complete 1,692-byte object has SHA-256
`bb0e91e073997cef46149ad62602af99d31c53100384029a6677232485b42c7d`.

The final `DRV_BuzzerStop` body follows the object's main literal pool; the
next translation unit begins at `0x00502D58`. Treating the pool as the end of
the object would therefore omit a real, externally called driver API.

## Executable closure

Thirty-five direct `BL` sites land on exact object entries: 17 are internal
and 18 are exterior. The object contains 88 direct calls in total. The only
stored function pointer is literal cell `0x00502D14`, which holds Thumb entry
`0x005029FD` for the one-shot timer callback. There are no `B.W` entry or
strict-interior targets and no legitimate stored strict-interior pointer.

Eleven raw four-byte windows equal interior addresses, but every source
offset is odd. They are overlapping instruction or packed-data bytes, not
aligned pointers or executable ingress. The analyzer pins their complete
site/value list and digest.

Five function names are exact retained diagnostic strings:
`_buzzerPlayVoice`, `_buzzerPlayStart`, `DRV_BuzzerInit`,
`DRV_BuzzerPlayAfterQueue`, and `DRV_BuzzerPlayNote`. Other names in the
function map are descriptive or explicitly qualified historical semantic
labels. They are not claimed as recovered source symbols.

## Voice-script and pitch tables

The predefined voice table is `[0x006C1E2C,0x006C1FEE)`: nine records of 50
bytes, SHA-256
`183d6370260fc192ce25b57b40b8d0768bd4362e842a6bc826c45d7b16939d41`.
Each record uses this compact format:

- byte 0: repeat count;
- byte 1: inter-repeat delay in ten-millisecond units;
- byte 2 onward: `(note, tone, beat)` byte triples;
- note zero: terminator.

The nine records contain respectively 1, 14, 12, 1, 2, 1, 7, 7, and 1
nonzero triples. `DRV_BuzzerPlayAfterQueue` accepts only indices below nine,
stops any current script, selects `table + type * 50`, and starts that record.

Two adjacent 28-byte tables at `0x0076B014` and `0x0076B030` provide the low
and high bytes of 28 sixteen-bit PWM reload values. Their individual SHA-256
values are `170e9c388fe4150ab5db7805770daadfb54635fd08eb2452b81d6ba194db589a`
and `7d17fc20e450b7a9c76fc8bf99c4062634fff0281dd2326623e29ad92feb9ebd`.
The interpreter indexes them as `tone * 7 + note - 1`. Notes below eight are
converted to frequency with `1,000,000 / (0xFFFF - reload)`; note values of
eight or greater produce silence. Beat duration is `beat * 62` milliseconds.

## Runtime contract

`DRV_BuzzerInit` configures output for 1 kHz and 30 percent duty, then creates
a one-shot OS timer using callback `0x005029FD`. The literal `0x05B8D800`
establishes a 96 MHz peripheral-clock basis. PWM duty conversion uses the
owned `100.0f` constant and computes the inverted duty fraction.

The state used by scripted playback is:

- timer handle at `0x20074504`;
- active voice pointer at `0x20074500`;
- byte cursor at `0x20074FB5`;
- repeat count at `0x20074FB4`;
- 16-bit repeat interval at `0x20074F2E`;
- eight-byte single-note scratch script at `0x20074128`.

The timer callback queues input-thread event 2. `DRV_BuzzerPlay` queues event
1 carrying the requested predefined type; the input thread later calls
`DRV_BuzzerPlayAfterQueue`. `DRV_BuzzerPlayNote` constructs a one-repeat
scratch script, stops existing playback, and starts the scratch record.
`DRV_BuzzerStart` and `DRV_BuzzerStop` expose direct frequency/duty output and
stop/release behavior outside the scripted queue.

## Reconstruction boundary

No authenticated historical source or license for this first-party driver is
available. Historical decompilation is used only as naming corroboration and
is neither an implementation source nor a provenance authority. Consequently
there is no reconstructed candidate, the driver is absent from
`components/apollo_main/core_overlay/overlay.json`, and it claims zero package
ownership bytes.

`tools/analyze_g2_drv_buzzer.py` pins the official image, all 17 bodies, the
owned non-code, literal/string contract, both reload tables, all nine voice
records, direct calls, stored callback, and qualified raw overlaps. The next
safe step is a clean-room candidate with explicit PWM/GPIO, resource-control,
RTOS-timer, and input-thread seams; that work is deliberately not inferred
from this binary audit alone.
