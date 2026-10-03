# Independent review 2935

**PASS_SCOPED**; `accepted` remains false.

Source and decoded ITCM hashes match inventory; declared flash bodies and candidate artifact hashes match. Isolated replay passed all 720 fixtures. Original descending transition and rearm/delay/ITCM path execute without interception. The current-index profile is varied between the old/new profile value and its bitwise complement; the recorded extrapolation/saturation and flag-dependent timer model matches the exact 14-write ledger and rearm argument (50 for bounded extrapolation, 200 for saturation with flag clear, 2000 when flag set). 625 ITCM iterations, incoming R3 return, R4–R11/SP/PRIMASK are asserted. Rank/current-index direction, profiles at old/new indices, special indices, aliases/volatile mutation, full flags/register clobbers and physical hardware remain outside scope.

Candidate receipt SHA-256: `2c668a5b8c11839668106fb72ebae0d9300ae2542fbc42c443fd6adab31eda96`.
