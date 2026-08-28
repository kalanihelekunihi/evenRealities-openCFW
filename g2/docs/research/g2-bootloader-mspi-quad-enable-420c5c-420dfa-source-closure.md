# G2 bootloader MX25U25643G QE service source closure

The authenticated Even G2 bootloader body `[0x00420C5C,0x00420DFA)` is 414
bytes with SHA-256
`ba6c3ac9d495b2fa232fbf70349bd0f4c588eb1699c69c92e5079fc6b03ec463`.
Its sole direct caller is the public driver initializer at `0x00420518`. The
14-byte successor pool `[0x00420DFA,0x00420E08)` has SHA-256
`8b41f058c64229c00d3a505f11715874ac3dcada1086d696f408e9365a2b3b6f`.

The recovered function rejects an unavailable MSPI handle with status 2,
performs an ignored ready wait, reads status register 2 with command `0x05`,
and returns raw transport failures. Bit 6 is the requested QE state. A matching
QE state is accepted only when protection bits `0x3C` are already clear.
Otherwise the function issues write-enable, sets or clears QE, clears the
protection bits, writes the byte with command `0x01`, performs another ignored
ready wait, and reads the register back. Verification mismatch maps to status
1. The low byte of a non-Boolean request is compared literally, an authenticated
quirk preserved by the clean-room C implementation.

Host tests pin the stock body, pool, caller, command/length tuples, exact update
mask, both ignored wait results, all raw-failure exits, diagnostic line/format
metadata, verification mapping, and Cortex-M55 freestanding compilation.

No signing, flashing, installation, reset, boot, or hardware operation occurred.
Live QE/status-register/write-latch/MSPI/external-flash/XIP and cold-boot
validation remains blocked because no authorized responsive right temple is
available and the authorized left temple must remain stock. The next executable
frontier begins at `0x00420E08`; firmware-wide completeness is not claimed.
