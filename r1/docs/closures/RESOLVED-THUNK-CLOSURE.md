# Resolved branch-thunk closure

Eight formerly unclassified application entries are single-instruction Thumb-2 `B.W` thunks to
functions whose ownership is already accepted. They add no independent algorithm or state. Their
ownership and implementation disposition therefore follow their exact destination; openR1 does
not create duplicate C bodies for them.

| Thunk | Destination | Accepted boundary | Direct caller | SHA-256 |
| --- | --- | --- | --- | --- |
| `0x00029D58..<0x00029D5C` | `0x0002B91C` | Goodix GH3X2X provider candidate | `0x0002AD60` | `5369da3475924b136084c9ea7d7ffb227e82b82fa688514febeb529840b738cf` |
| `0x0006F8F6..<0x0006F8FA` | `0x000509B0` | R1 Goodix board-line adapter | `0x0002D986` | `6504c3dd834dceb1308723768c59882aee98a92e1871097b5c98ddaae7bd3112` |
| `0x0008A7F0..<0x0008A7F4` | `0x0005A9F8` | activity daily-cache metadata refresh | `0x0009270E` | `48e55172c73a11cb770e7959a8d4ba7921479309f764a1d1f700b6046ca2d189` |
| `0x0008D534..<0x0008D538` | `0x0005AD08` | heart-rate daily-cache metadata refresh | `0x000926FE` | `d3819a08a80b6d96fb3e412bc1f6aa997ffa620983e0d8c86cda507ce3bf710b` |
| `0x0008D884..<0x0008D888` | `0x0005AF44` | HRV daily-cache metadata refresh | `0x00092716` | `9834b354a6e6496ecf5dbc2a67e3ed20a8d90c9d82d8815425ab5bd0716354f9` |
| `0x0008E54E..<0x0008E552` | `0x0005BB14` | SpO2 daily-cache metadata refresh | `0x00092702` | `dffa470e88d4e39089f6b1a385e5117912651154a49205fe0f6a1964e9f08085` |
| `0x0008E558..<0x0008E55C` | `0x0005BCD4` | stress daily-cache metadata refresh | `0x0009270A` | `36abc19673406800e8abfb0abf1bdd904e19ff2badfb0af3e9a6655f7bcac8aa` |
| `0x0008E69C..<0x0008E6A0` | `0x0005BE64` | temperature daily-cache metadata refresh | `0x00092706` | `0dca46584331f0e760693db166f54c36f4559b0a2a1c99548e31cbabadd065cb` |

The closure is 8 functions / 32 bytes. The first thunk remains inside the licensed Goodix gate;
the second is only an alias of an admitted R1 board adapter; and the six health/activity thunks are
aliases of already implemented product-owned metadata operations. No third-party implementation
is copied or reconstructed.

The exact image, instruction encodings, destinations, hashes, and callers are checked by:

```sh
python3 tools/evidence/summarize_r1_resolved_thunks.py
```
