# Independent review 2147: Original sensor difference chain

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-row-original-difference-chain-2144/001` remains unaccepted.

The isolated 120-fixture replay executes the original 4BA8 chain through the original cap (5C02/5BC0), query boundary, and 5920 difference store. Only 50A0, 4FEE, and 5BA2 are intercepted as specified. Results and call order match the candidate replay byte for byte.

The fixtures assert the capped sample and resulting item+4 halfword, guard-path zero, outer return value, and restored SP. Query status and row-validity mutation are controlled; assertions do not establish downstream child behavior.

Limit: Only the explicitly listed boundaries are controlled; lower-level sensing, arbitrary rows, aliasing, and concurrency remain open.
Limit: This is bounded trace composition, not full sensor or caller coverage.
Limit: No canonical admission or C implementation.
