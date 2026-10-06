# P2-15885 independent review

Fresh replay exactly reproduces the saved draft ledger: 12 function records totaling 1,324 bytes, one 480-byte table record, and 11 candidate review references. The function IDs are distinct and code ranges do not overlap. Pinned source and pseudocode hashes are checked, as are the table rows and raw image bytes. Call targets are classified only by whether their addresses fall inside the scoped queue interval.

The review references are candidate leads, not admission decisions or exact verdict bindings. The ledger does not establish complete function coverage, semantic completeness, image ownership, or physical register behavior. Status remains partial and unaccepted.
