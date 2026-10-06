# P2-15911 independent review

Fresh replay matches the failure cross-check: 432 raw failed candidates, with 121 bodies fully covered by candidate-byte evidence and 311 with no mapped candidate bytes. The 121 count is a byte-coverage classification only, not semantic recovery. The comparison respects discontiguous body spans and reconciles mapped plus unmapped bytes to each declared body size without double counting. Input hashes match.

These counts are discovery diagnostics, not a whole-firmware denominator or admission result. Candidate ownership, body completeness, and semantic meaning remain unresolved; no C or gate changes.
