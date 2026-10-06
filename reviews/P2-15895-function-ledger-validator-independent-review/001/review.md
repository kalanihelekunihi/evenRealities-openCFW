# P2-15895 independent review

The intended 18-case validator is candidate-function-ledger-validator-16298/001. Fresh replay confirms 20 function records and rejects all 18 mutations across the revision-001 queue and clock ledgers. It checks evidence and schema consistency, including image mapping, source bytes, instruction tiling, referenced direct calls, pseudocode/instruction hashes, identities, and status.

This older validator predates target-lock/path-root binding and independent review binding. It is not semantic validation or coverage/admission. No gate changes; status remains partial and unaccepted.
