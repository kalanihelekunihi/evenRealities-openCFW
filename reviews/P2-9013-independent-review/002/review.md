# P2-9013 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- The corrected independent replay ran 24 original-instruction cases and passed exact 440-byte descriptor and 100-byte adjacent-area comparisons, including untouched bytes.
- The fresh replay explicitly treats other+60 as a published flash-table pointer and keeps callback slot +88 distinct. Final R0/R1/R2/R3, R4-R6, SP, PC, and PRIMASK assertions passed.

Limitations:

- Synthetic SRAM only; no concurrency or physical claim.
