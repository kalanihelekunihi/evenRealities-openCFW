# Independent review — P2-21355

Status: partial; accepted: false.

Fresh extraction passed for the exact 88-byte data interval. The regenerated `bytes.json` matches the candidate. I decoded each consecutive 8-byte little-endian slot as binary64 and confirmed the raw encodings are:

- 0x00483908: `000000000000f07f` (binary64 bit pattern `7ff0000000000000`)
- 0x00483910: `ffffffffffffefff` (binary64 bit pattern `ffefffffffffffff`)
- 0x00483918: `0000000000000000` (binary64 bit pattern `0000000000000000`)
- 0x00483920: `fb799f501344d33f` (binary64 bit pattern `3fd34413509f79fb`)
- 0x00483928: `b3c8608b288ac63f` (binary64 bit pattern `3fc68a288b60c8b3`)
- 0x00483930: `61436f63a787d23f` (binary64 bit pattern `3fd287a7636f4361`)
- 0x00483938: `71a379094f930a40` (binary64 bit pattern `400a934f0979a371`)
- 0x00483940: `1655b5bbb16b0240` (binary64 bit pattern `40026bb1bbb55516`)
- 0x00483948: `ef39fafe422ee6bf` (binary64 bit pattern `bfe62e42fefa39ef`)
- 0x00483950: `2d431cebe2361a3f` (binary64 bit pattern `3f1a36e2eb1c432d`)
- 0x00483958: `0000000080842e41` (binary64 bit pattern `412e848000000000`)

The PC-relative reference records in maps 21744, 21746, and 21748 cover these eleven slot addresses across the three maps; the coverage is a consumer-reference check, not proof of exclusive ownership. The data range is non-code. The displayed values are the encodings themselves; no external protocol or whole-image ownership claim is made.
