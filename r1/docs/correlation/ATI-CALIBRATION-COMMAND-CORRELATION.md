# ATI calibration command correlation

## Disposition

The function at `0x0006210C` is the R1 product handler for legacy opcode `0x91`. Its 416
executable bytes implement bounded ATI/touch-calibration command policy, not the IQS7211E
controller implementation. It is therefore classified `r1_product_specific` /
`clean_room_behavior_only` and represented in openR1 by the side-effect-free
`r1_ati_calibration_plan_command` planner.

The IQS7211E device operations use the admitted provider boundary. Nordic/CMSIS queue and event
operations, logging, the legacy response transport, and live calibration state remain external.

## Exact body and entry path

Ghidra assigns two executable ranges to the function:

| Range | Bytes | Role |
| --- | ---: | --- |
| `0x0006210C..<0x00062132` | 38 | setup, bounds check, and table branch |
| `0x0006213E..<0x000622B8` | 378 | eleven subcommands and common response path |

The ranges total 416 executable bytes. Concatenating them in that order has SHA-256
`843951c84bc7b1def3a71058540210ee6eab68aacd2d20eb17e1e3e772664f98`. The intervening
12-byte table at `0x00062132` is separately pinned as
`06233a5362758496b1b5b900`. The sole direct callsite is `0x0004E3EE`, inside the already
recovered legacy dispatcher whose opcode table maps `0x91` to this handler.

## Recovered policy

The handler reads the subcommand from frame offset 3 and arguments from offsets 4 and 5. Unknown
subcommands take the ordinary response path with status 5. Event-bearing subcommands cover the
exact power-of-two masks `0x40` through `0x800`.

| Subcommand | Product policy |
| ---: | --- |
| 0 | set the trackpad raw-print level from argument 0 |
| 1 | post event bit `0x40` |
| 2 | post event bit `0x80` |
| 3 | queue configuration words `(1, 1)` with argument 0, then post `0x100` |
| 4 | queue configuration words `(2, 2)` with both arguments, then post `0x200` |
| 5 | queue configuration words `(3, 1)` with argument 0, then post `0x400` |
| 6 | queue configuration words `(4, 1)` with Booleanized argument 0, then post `0x800` |
| 7 | return two calibration bytes with status 6; an unavailable provider yields `0xFF` and status 5 |
| 8 | open touch source `2` |
| 9 | close touch source `2` |
| 10 | return the provider-normalized ring size in argument byte 0 |

The stock image obtains the subcommand-7 values from `0x00072898`, sends configuration messages
through `0x00093514`, posts event flags through `0x00093504`, and emits responses through
`0x0008967C`. Source open/close route through `0x0008E7D0` and `0x0008E6A0`; ring-size lookup is
`0x0006A1CC`. These addresses establish the boundary but do not admit their implementations.

## Clean implementation

The local planner accepts already-normalized provider observations and returns one typed action,
the exact event flag, the two recovered configuration words, action arguments, response status,
and bounded response-byte updates. It never reads touch hardware, mutates calibration, posts an
RTOS flag, queues a message, logs, or transmits a response. An nRF5 integration layer may execute
the plan only through admitted IQS7211E and Nordic/CMSIS providers.

Tests cover all eleven subcommands, the unknown-subcommand path, Boolean normalization,
successful and unavailable calibration queries, response mutations, event masks, and invalid
arguments.

## Reproduce

```sh
python3 tools/summarize_r1_ati_calibration_command.py
python3 tools/build_r1_source_ownership.py --check
make -C openR1 test
make -C openR1 sanitize
make -C openR1 arm-objects
python3 tools/verify_openr1.py
```
