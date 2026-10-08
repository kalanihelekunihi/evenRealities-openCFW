# P2-19095 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x469388–0x469400 (120 bytes; 47 instructions), and candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the 24-byte frame and saved input slots, null guard, fresh predicate mask reads, and distinct diagnostic overwrites of SP0/SP4/SP8. The ADR-produced values 0x469578 and 0x46957C are addresses selected using a temporary low-byte test of R4; the subsequent secondary diagnostic reuses the low-byte test, then the code truncates R4 in place at 0x4693FA. The ADR references are address calculations, not dereferences.
