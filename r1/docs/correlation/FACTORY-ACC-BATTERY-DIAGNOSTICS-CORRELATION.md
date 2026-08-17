# Factory accelerometer and battery diagnostics correlation

## Decision

The explicit Ghidra seeds at `0x0004ED64` and `0x0004EE18` are independent
R1 factory diagnostic adapters, not code owned by the broad noncontiguous
function ranges that happen to contain their addresses.

| Adapter | Executable extent | Bytes | SHA-256 | Complete envelope |
| --- | --- | ---: | --- | --- |
| accelerometer result callback | `0x0004ED64..<0x0004EDAC` | 72 | `c2ee443870c8d5c7e1426d03d974cb57f49984144cec1e066203fe15a62ecbdf` | `0x0004ED64..<0x0004EDDC`, 120 bytes, `590e953ab4c6f02a3f30ebdc8b7aee9d85df5773d4bf4d47ab5a3b6d39efbdbc` |
| `AT^BAT_ADC` handler | `0x0004EE18..<0x0004EE38` | 32 | `9e5e60affb55774064cbe965e53c75d58cc6cac278660b2a70ad6df47b52446a` | `0x0004EE18..<0x0004EE64`, 76 bytes, `839287d11a6963f9d812a5d3b8c5379649f37fca0f9e724f26974ce1f50bbae2` |

Neither function has a direct branch caller. The stream registration stores
Thumb pointer `0x0004ED65` at `0x0004ED58` beside listener `"at"` and topic
`"acc"`. The factory command table record at `0x000C4230` pairs the
`"AT^BAT_ADC"` name pointer with handler Thumb pointer `0x0004EE19`.

## Accelerometer record

The callback receives a fixed 182-byte result record. Bytes `0...179` are 30
packed XYZ triplets, each three signed little-endian Int16 values at a
six-byte stride. The UInt16 at offset 180 is the populated-record count. The
stock loop consumes only indices divisible by five, so a full record emits
indices `0`, `5`, `10`, `15`, `20`, and `25`, followed by the fixed separator
line.

`r1_factory_acc_diagnostic_plan_decode` preserves those indices and signed
axes in a six-element typed plan and records the unconditional terminator
intent. It requires the exact fixed record size and rejects counts above 30;
that guard prevents the stock callback's out-of-bounds access and UInt8 loop
wrap on malformed provider data. Zero populated records still request the
terminator, matching the unconditional tail call.

## Battery snapshot

The `AT^BAT_ADC` handler calls the cached battery-millivolt accessor at
`0x00091290`, the percentage accessor at `0x00091270`, and the persisted
battery-type getter at `0x0007BB44`, in that order. It formats those three
values in the same order and returns one. `r1_factory_battery_diagnostic_plan_build`
accepts the already-obtained UInt16/UInt8/UInt8 values, preserves them without
inventing validation, and records the fixed handler return value.

## Boundary

The clean helpers emit no text, register no stream, read no accelerometer or
battery hardware, access no private SRAM or persistence, and expose neither a
factory command router nor a live command. Sensor-stream execution, battery
accessors, eAT formatting/fan-out, and command registration remain external.

Tests cover all six decimated indices, signed axes, zero/full/malformed counts,
exact record length, raw battery-value preservation, the fixed success value,
and null arguments.

## Verification

```sh
python3 tools/evidence/summarize_r1_factory_acc_battery_diagnostics.py
```

The evidence script pins both executable/envelope hashes, both zero direct-call
sets, callback and command-table Thumb pointers, exact strings, and every
local accessor/formatter callsite.
