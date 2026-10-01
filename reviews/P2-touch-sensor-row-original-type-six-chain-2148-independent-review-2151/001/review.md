# Independent review 2151: Original type-6 sensor chain

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-row-original-type-six-chain-2148/001` remains unaccepted.

The isolated 120-fixture replay matches the frozen candidate byte for byte. Original 4BA8 through 5BA2 and 5A0A execute; only 50A0 and 4FEE are intercepted. In valid active type-6 cases, the original type dispatcher reaches the original type-6 body, following the original cap and difference operations.

The trace assertions check capped/difference values, item flags and aggregate bit, guarded call order, R0 result, and SP restoration. The query controller changes row validity and supplies query status; assertions are limited to those controlled inputs and tested configuration.

Limit: Acquisition/query behavior at 50A0 and 4FEE remains controlled; type-2/3 paths, arbitrary configurations, aliases, concurrency and physical behavior are not established.
Limit: Bounded composition evidence only; no canonical admission or C implementation.
