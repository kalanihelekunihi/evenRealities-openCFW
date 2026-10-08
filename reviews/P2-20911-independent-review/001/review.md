# P2-20911 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the locked image (SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`). The extracted 8 bytes at 0x78EDF4..0x78EDFC are `04 00 01 00 00 00 00 00`; candidate and fresh `data.json` hashes match (`9ea883e8b665a1003c611973f09c2803b5f43b9833c66a88283607d9185e57af`). The recorded pointer literal at 0x47D9C0 resolves to 0x78EDF4. Map 21306 contains the corresponding PC-relative LDR at 0x47D874 (`LDR R0, [PC,#328]`), whose aligned PC target is 0x47D9C0.

The map describes the 8-byte template load/store in the message-builder entry, including zero initial bytes 4..7 and later builder writes at bytes 4, 5, and 6. This supports the mapped use only; additional consumers and pointed-to ownership are not established. The candidate stays partial/unaccepted, and no source or gate files were changed.
