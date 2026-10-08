# Independent review: P2-19219

Status: partial / unaccepted. No source or gate changes.

I independently extracted `[0x46A822, 0x46A848)` from the locked flash image and verified the SHA-256 of the 38-byte result: `85da82f9508fe8828b268ddee11c796db5718ea86eda1b469e42a1f929210866`. It begins with two zero alignment bytes and contains nine aligned little-endian words from `0x46A824` through `0x46A844`. The candidate data.bin and each word record match. The code region ends at `0x46A822`; references and the observed consumer set remain nonexhaustive, so this review makes no pointee-contract claim.
