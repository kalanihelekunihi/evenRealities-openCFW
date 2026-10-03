# Independent review 2915

**PASS_SCOPED**; `accepted` remains false.

The source image hash matches inventory; body [42B014,42B068) digest and candidate output hashes match the receipt. Isolated replay passed all 864 fixtures (8 R0 values × 6 R1 values × 3 initial marker bytes × 3 independently injected successive MMIO words × 2 PRIMASK values). Original instructions execute without function interception. The read hook supplies three distinct possible words at each target read; exact ordered reads/writes and R0–R3 values are checked, along with PC, SP, LR and PRIMASK. Marker and MMIO effects match the decoded gates, including conditional flag store and ordered bit16/bit3/bit6 clears. High-registers, NZCV, actual peripheral behavior, arbitrary aliasing, and physical hardware are explicitly outside the fixture scope.

Candidate receipt SHA-256: `054afa3f9dc1be448d4e6253d87118b9653826633a99f9a61dd23216754352f8`.
