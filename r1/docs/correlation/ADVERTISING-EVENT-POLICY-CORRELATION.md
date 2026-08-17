# Advertising-event policy correlation

The R1 advertising callback at `0x0007CBC8..<0x0007CC54` is a 140-byte
function with SHA-256
`623c35b360ba9ee09bb2077d2c5adc11a57cd3152c68763071bf66d935562d81`.
Ghidra's function inventory omitted the entry because it sits inside an
unrelated noncontiguous bounding range, so the exact body is admitted as a
manual provenance supplement.

There are no direct branch callers. The Thumb pointer `0x0007CBC9` at flash
address `0x00048AC4` registers the callback with the Nordic advertising setup.
Its final tail branch at `0x0007CC48` targets the already bounded R1 status
publisher wrapper at `0x0005E1CC`.

The callback has three status-producing cases:

| Provider event | Published active flag | Published mode | Diagnostic |
| --- | --- | --- | --- |
| `0` | false | `0` | none |
| `3` | true | `1` | `Fast advertising.` |
| `4` | true | `2` | `Slow advertising.` |

All other event values return without publishing or logging. The adjacent
structured and plain-text strings at `0x0007CC5C`, `0x0007CC74`, `0x0007CC88`,
and `0x0007CCA0` independently identify the fast and slow cases.

`r1_advertising_event_plan_build` implements only this pure product mapping.
It neither starts/stops advertising nor reproduces Nordic advertising, the
structured logger, or status transport. Those effects remain typed provider
composition boundaries.

Reproduce the exact extent/hash, registration pointer, tail target, strings,
and log-literal checks with:

```sh
python3 tools/evidence/summarize_r1_advertising_event_policy.py
```
