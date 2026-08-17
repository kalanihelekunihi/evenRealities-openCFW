# Factory optical diagnostic correlation

## Outcome

Four factory-only optical text callbacks that curated Ghidra scripts created after the main
function export are now represented by transparent C. They decode fixed records into typed plans;
OpenR1 does not reproduce the stock variadic logger or expose a factory command route.

| Recovered extent | Bytes | SHA-256 | Behavior |
| --- | ---: | --- | --- |
| `0x0004F30C..<0x0004F318` | 12 | `0259e93eb88c7b1d9f0176253dbc7b2a3ff8cda374a3f00d8e9d5fcaa6fbbb25` | load three HR bytes and tail-call the `heartrate:%d` logger |
| `0x0004F378..<0x0004F38C` | 20 | `767dda28f5c3c94973e906431fee73c1422172792767e15c855b5e2436e3d97e` | load four little-endian HRV UInt16 values and call the `hrv:%d,%d,%d,%d` logger |
| `0x0004F914..<0x0004F91C` | 8 | `6a6347282d4680a2eb2ba0733ae4c105fa3286d91a2808aec2bb6297760a8f73` | load one SpO2 byte and tail-call the `spo2:%d` logger |
| `0x0004F980..<0x0004F9A0` | 32 | `c6a9fffa7708f030ec5e0d14b35998fe6efcec519bccf386713c30eb3a220b4a` | divide a little-endian UInt16 by 100, write the quotient back, and split it into decimal tens/ones for `temp:%d.%d` |

Each body has an independent entry and a complete tail-call boundary immediately before its
format string. `R1OpticalResultEvidence.java` identifies the HR, HRV, and SpO2 entries as factory text
callbacks; `R1FactoryRoute.java` and `R1Functions.java` retain the temperature entry.

## Clean implementation

`r1_factory_heart_rate_diagnostic_plan` requires the three bytes the stock callback loads. It
preserves all three register arguments even though the recovered format consumes only the first.
`r1_factory_hrv_diagnostic_plan` requires and decodes four little-endian UInt16 values.
`r1_factory_spo2_diagnostic_plan` requires one byte. `r1_factory_temperature_diagnostic_plan`
requires a two-byte little-endian value, reports the exact truncating `/ 100` replacement value,
and reports the quotient's tens and ones digits. The plan marks the stock record write as requested
but does not mutate its const input.

Tests cover fixed lengths, all loaded HR/HRV/SpO2 values, little-endian decoding, truncation, decimal split,
the temperature write intent, null arguments, and wrong lengths. The verifier pins all three stock
bodies and their product-owned ledger names.

These helpers emit no text, read no sensor, access no private SRAM, publish no event, enable no
measurement, create no BLE/factory command, and perform no record mutation. Their only output is a
caller-owned typed plan.
