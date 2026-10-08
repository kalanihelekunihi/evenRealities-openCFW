# P2-19109 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x469580–0x4695FE (126 bytes, 44 instructions); candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the 32-byte frame and full selector-two gate, with three distinct fresh reads of the global byte across the diagnostic paths and later byte guard. The SP0/SP4/SP8 diagnostic writes overlap caller argument slots but leave saved R4–R6 intact. The code explicitly writes the global flag, then calls 0x43C0E4 with the observed address, 28, zero, and live R3. No fill behavior is inferred.
