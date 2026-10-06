# Independent review P2-18461

Status: partial, unaccepted. No source or gate changes.

I independently extracted the 16-byte interval `0x460118..0x460128` from the pinned image (SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`). Fresh bytes and four little-endian words match the candidate exactly: `0x000F4240` (1,000,000), `0x200746CC`, `0x200746C8`, and `0x20002928`. I verified the cited PC-relative references in selected maps: classifier maps 18850/18852/18854 point to the divisor; maps 18856/18860 point to the two global addresses; map 18858 points to the fixed table address. The preceding function return at `0x460116` and next code entry at `0x460128` support the stated extent.

The literal bytes and local reference provenance are confirmed. This does not establish the pointee layout, table contents, global ownership, or broader image coverage. No executable semantics are assigned to these words.
