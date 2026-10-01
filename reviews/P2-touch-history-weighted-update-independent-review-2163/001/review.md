# Independent review 2163: weighted history update

**Result: PASS_SCOPED.** Candidate `analysis/touch-history-weighted-update-49e6-2160/001` remains unaccepted.

The exact 4FDE leaf implements wrapped `R0*R2 + R1*(256-R2)` followed by logical shift right 8. The separate 49E6 caller loads current values before processing, takes the weight from config bits 16–23, and uses bit 1 to gate updating history. On the enabled path, each weighted value is stored to history before current; the disabled path writes the saved values to current and leaves history unchanged. Saved registers and SP restore.

All pins matched, and the isolated 2,813-case replay is byte-identical to the candidate. The inputs use separate buffers, so aliasing/concurrent behavior and physical field semantics remain unproven. No canonical record changed.
