# P2-20923 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the pinned image (SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`). The exact 80-byte extract at 0x47DC24..0x47DC74 matches candidate data; candidate and fresh JSON hashes are identical (`6b697cc2082f5daeaebb7ca679981c5914253c36b68d55bfcae3ab1a15eb6bb1`). The consumer scan verified all 20 aligned four-byte slots and retained 27 mapped PC-relative LDR/ADR consumer records, checking the relevant component receipt hashes.

The first 12 bytes decode as three zero-terminated byte sequences with four-byte storage: `r`, `a+`, and `N/A`. This is a byte-level description only, not proof of API names or ownership. The remaining 17 words are retained as literal values, including the record pointer, index pointer, buffer pointer, magic value, and comparison constant described in the report. Pointed-to ownership and whole-image coverage remain unproven. No source or gate files changed.
