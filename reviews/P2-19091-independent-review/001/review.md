# P2-19091 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46931C–0x469388 (108 bytes; 40 instructions), and candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the SP+16 input-byte reload, low-byte R5 comparison, and unequal route’s child arguments including SP+16 and an extra SP+0 value of 4. The full child result is retained and tested; nonzero diagnostics pass it in R3. The shared epilogue discards the saved-input slot and restores R4/R5/PC while retaining the live R0 path result. The child may write through the supplied pointer, so the input is not treated as immutable.
