# G2 NVDB product-mode recovery

Status: complete binary census and host/Thumb-qualified clean-room candidate;
not production-routed.

The retained first-party `service_nvdb_product_mode.c` object is exactly
`[0x004ABD90,0x004ABEC8)`, 312 bytes, SHA-256
`ff1ab9f69ab28b170f754280b7afa0073010217748706b238c21b3cc717addb4`.
Six linked bodies contribute 270 bytes; their concatenated SHA-256 is
`1bfe7d97d0352877f2563deaee8402758c6d79f816a9de19916bad5c46918584`.
The remaining 42 bytes are alignment and owned literals. Two stored Thumb
pointers root the default and migration entries, 54 direct calls root the
remaining API surface, and 18 calls leave or remain within the object. No
stored or branched strict-interior ingress survives.

The four-byte record at `0x200038F0` is `{version, mode, crc16}`. Boot bytes
are `01000000`; initializing CRC-16/CCITT-FALSE over the first two bytes stores
`0x2E3E`. `_nvdbUpdataProdMd` reads `nvProdMode` into a temporary record and
rewrites current defaults after a missing read or mismatched CRC only when the
stored version is zero. A version-1 mismatch is intentionally left alone.
`set_product_mode` changes SRAM only; the updater forces version 1, recomputes
CRC, and writes four bytes. The separate read API imports all four persistent
bytes into SRAM without validating them and returns the imported mode.

`components/apollo_main/core_overlay/nvdb_product_mode.c` independently
recreates all six entries. Host tests cover the CRC, RAM-only set/get,
persistence, read import, and every migration branch; freestanding Thumb
compilation exposes exactly six global text symbols. The exact product source
and historical commit remain unresolved. Production routing, placement,
diagnostics, redirects, and package validation remain deferred, so this work
adds zero ownership bytes and performs no hardware access.
