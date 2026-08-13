# PMIC charge-event policy correlation

## Decision

The 402-byte function `0x00096AD0..<0x00096C62` is R1 product orchestration around
separately owned YHM2710, ST25DVxxKC, timer/event, and logging providers. Its exact body SHA-256
is `a079977932ae1d297bb451311bc998e001d9b3ae13efe0ff2769f14bc00ef67a`; direct callsites are
`0x000463DE`, `0x00047F68`, and `0x00047F82`. It is admitted as `r1_product_specific` /
`clean_room_behavior_only`.

The clean implementation is `r1_pmic_plan_charge_event` in
`../src/r1_battery.c`. It is a pure planner and packet
template builder. It performs no live PMIC write, NFC operation, timer mutation, logging, or
internal-event publication.

## Recovered status template

For normalized charging or full state and event `0x01`, the function clears a 24-byte working
buffer and supplies it to the existing dock-mailbox receive/response path. Only the first 23 bytes
are eligible for the existing dock control reply. The recovered layout is:

| Offset | Bytes | Meaning |
| ---: | ---: | --- |
| 0 | 1 | zero |
| 1...2 | 2 | fixed `01 02` |
| 3 | 1 | battery percentage |
| 4 | 1 | charge in bits 1...0; six-bit whole temperature in bits 7...2 |
| 5...6 | 2 | battery millivolts, little-endian |
| 7...8 | 2 | NFC rectifier millivolts, little-endian |
| 9 | 1 | raw power-state flags |
| 10 | 1 | PMIC readiness/status flag |
| 11...12 | 2 | zero/reserved |
| 13...22 | 10 | ASCII `2.2.6.0009` |
| 23 | 1 | zero working-buffer tail |

The stock raw charge encoding is `0` not charging, `1` charging, and `2` full. The public clean
API maps those values from `r1_charge_state` rather than leaking the stock private enum. The
temperature field is exactly `(unsigned_milliunits / 1000) & 0x3F`; the mask behavior, including
wrap above 63, is retained.

## Recovered thermal policy

The whole-value field selects only an R1 action plan:

- zero leaves the existing target unchanged;
- 1 through 14 selects exact Float32 word `0x40808312`;
- 15 through 44 selects exact Float32 word `0x4160F5C3`; and
- 45 through 63 requests raw register/value pair `02=F8`.

The low and middle actions are suppressed when the current target word is already equal. The raw
high-band action is not suppressed. Physical units and undocumented YHM register meanings remain
unassigned.

Event `0x5A` suppresses the function's initial work cancellation. A not-charging transition still
performs its later unconditional cancellation and returns a single abstract transition action.
All callback installation, shared-power release, Nordic/CMSIS event publication, and scheduling
needed to execute that transition remain external.

## Provider boundary and verification

The following are deliberately not recreated:

- YHM2710 register/state transport and target application;
- ST25DVxxKC mailbox reads/writes, supplied by the pinned official ST component;
- Nordic/CMSIS timers, work queues, and events; and
- logging and live dock transport.

Host tests exhaust all 65,536 UInt16 temperature inputs, both target equality branches, charge
state mapping, packet byte order and reserved bytes, the `0x5A` cancellation exception, and invalid
input immutability. Sanitized host and freestanding Cortex-M4 builds compile the same planner.
The planner is retained at nonzero address `0x00036DE8` in the verified unsigned Nordic SDK image.
That image has 94,804 bytes text, 236 bytes data, and 132,544 bytes BSS; its standalone HEX and BIN
SHA-256 values are `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`
and `421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

Reproduce the evidence gate with:

```sh
python3 tools/evidence/summarize_r1_pmic_charge_event.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
