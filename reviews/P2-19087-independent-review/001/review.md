# P2-19087 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46921C–0x46928C (112 bytes; 40 instructions), with candidate instruction/reference records matching exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Checked the 32-byte frame layout: the original R0 word is stored at SP+16, while diagnostic SP+0/SP+4 are local slots. The initial byte guard and later fresh global byte reads are distinct. The zero arm writes byte 1 before calling the predicate; the low byte is then freshly loaded from the saved input word, and the later child result is tested as a full word. No lock/state meaning or child contract is inferred.
