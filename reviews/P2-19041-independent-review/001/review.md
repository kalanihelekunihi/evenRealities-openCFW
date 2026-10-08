# P2-19041 independent data review

Status: partial, unaccepted. No source or gate changes.

Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Fresh extraction at 0x468A30–0x468A40 matches all 16 candidate data bytes. The four aligned little-endian words and values in `words.json` match direct decoding of the locked flash. I independently checked all 34 listed consumer rows against the named maps’ PC-relative reference records and locked-image word bytes. This corroborates the listed consumers only; no exhaustive-consumer or pointee-ownership claim is made. The preceding POP-PC is at 0x468A2E and the next code entry is 0x468A40.
