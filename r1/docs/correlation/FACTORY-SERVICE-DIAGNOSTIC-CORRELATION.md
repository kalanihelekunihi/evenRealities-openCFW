# Factory service diagnostic correlation

## Outcome

Three additional factory-service handlers omitted from the main Ghidra function export now have
transparent typed C replacements. Two are log-only record adapters; one posts the fixed system-task
event used to restart the periodic factory timer.

| Recovered extent | Bytes | SHA-256 | Behavior |
| --- | ---: | --- | --- |
| `0x0004EDDC..<0x0004EDF8` | 28 | `4fdaec6c5dea91d292fb47b10e5c3770dd7762128fbcfec819374c504301bd89` | obtain and log UInt32 all-kcal, UInt16 steps, and UInt16 active-kcal |
| `0x0004F040..<0x0004F04C` | 12 | `adf55bcf1f3b579e6a6b1757fab7e176681320b0dee8f76b23d26c459b3f66c2` | post system-task event `4` and return success |
| `0x0004F1C4..<0x0004F1F4` | 48 | `c3e254d90368580d139606af0e0b2ae53c30608bfdfbf0ee806447be31e3404e` | obtain sensor count and two signed temperature values, then log their toward-zero average |

The activity layout follows the callback's exact stack loads: offsets `0`, `4`, and `6`. The
temperature layout is the packed five-byte result consumed at offsets `0`, `1`, and `3`; the two
signed values are in 0.001 °C units. The stock average adds the sign correction before its
arithmetic divide by two, which is equivalent to C's signed division toward zero. Tests include a
negative odd sum to pin that rounding rule.

`r1_factory_activity_diagnostic_plan_decode` and
`r1_factory_temperature_pair_diagnostic_plan_decode` decode caller-owned bytes without invoking
the producer or logger. `r1_factory_periodic_timer_restart_plan_build` records the fixed event-4
intent without posting it.

No helper reads hardware, accesses the stock factory object, emits text, starts a timer, publishes
an event, exposes an internal publisher, or creates a factory/BLE command route.
