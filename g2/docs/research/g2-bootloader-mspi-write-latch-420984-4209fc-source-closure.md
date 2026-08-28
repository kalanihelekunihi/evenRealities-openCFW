# G2 bootloader MX25U25643G write-latch source closure

The complete authenticated write-enable and write-disable functions are now
routed to compilable clean-room C. The write-enable body
`[0x00420984,0x004209BE)` is 58 bytes with SHA-256
`e675df17f3a419b27b088cd7cd0c5785537fe730f597f894ba648e3a76afa3e5`;
the write-disable body `[0x004209C4,0x004209FC)` is 56 bytes with SHA-256
`f29c57daa25ee3108fe92b65e0076a21ac49af5ded9c735c33624e26e4400cd2`.
Halfword-aligned image scans pin four write-enable callers at `0x004208C6`,
`0x00420A66`, `0x00420B62`, and `0x00420CFA`, and three write-disable callers
at `0x0042094C`, `0x00420AB8`, and `0x00420B8C`.

Both wrappers submit the source-routed write transfer with zero address,
length, data, and option fields. Write-enable uses command `0x06`; write-disable
uses command `0x04`. Success returns zero without logging. Failure returns the
raw transport status and preserves the exact stock diagnostic level, line,
format, file, tag, and function tuple. Host tests pin the complete descriptor,
both status paths, and both diagnostic records. The 12-byte predecessor pool
`[0x00420978,0x00420984)`, six-byte inter-function pool
`[0x004209BE,0x004209C4)`, and 12-byte successor pool
`[0x004209FC,0x00420A08)` remain authenticated non-executable compatibility
data.

Apple Clang 21.0.0 emits relocation-free 72-byte leaves at `0x00437754` and
`0x0043779C`, with SHA-256
`e55a89dcef578fc6fa07e7935d8c0edf4f2d76cceef420b1a50b1468ea90fa76`
and `398b8c96a5d637a6bf6a1d977c0dcd0b1dee70594c4dbc2c7e44ec70b7b7d99c`.
Linux Clang 22.1.8 emits relocation-free 72-byte leaves at `0x00437744` and
`0x0043778C`, with SHA-256
`a4ba52e8c812bf575c8672771c9fefbf13819b2e2da41f735f715fe35d0ebe8f`
and `fe292013720adb0a8ee85ee63074492f6759c709d7a285674a97589c824a7150`.
Canonical and Linux providers are 161,764 / 161,748 bytes with SHA-256
`c9d14e63c54b3813bb527691b429f287a8eebfcce83b3bc9a0df03c87df8237e`
and `165152971c636da8bf7fb939b44093681017f7b797e84bc0d68d4a10e11ee70d`.
The unsigned canonical package is 4,743,342 bytes with SHA-256
`f0fa1999e7992a0a20ea3897185447b060ae3510e38e2ba3560c8651a9f69d7c`.

No hardware operation was performed. Live write-enable-latch, MSPI,
external-flash, XIP, error, and cold-boot behavior remain explicitly blocked
by the absence of an authorized responsive right-temple G2; the left temple
must remain stock. The sector-erase function beginning at `0x00420A08` was
subsequently source-closed; the next executable frontier is the program
service at `0x00420B0C`. This remains a historical increment rather than a
functional-completeness claim.
