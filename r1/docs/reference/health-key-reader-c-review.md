# R1 cached and flash-backed authorization key reader in C

Stock `0x6ad28` now has an ordinary C provider in `native_health_key_reader.c`. It reads the shared authorization/identity cache-valid byte. A nonzero byte selects the cached key pointer; otherwise it calls the existing C FAL/CRC key loader. A zero low status returns minus two without copying. Success copies exactly 64 bytes and returns 64, regardless of the caller's length argument.

The scatter decoder confirms the cold pointer at `0x20006e34` targets `0xc0664`. That target is a 64-character printable data string followed by NUL. The C resource and relocated pointer match the authenticated data; no executable stock bytes are introduced. The cache flag retains its existing shared owner. Explicit R2/R3 metadata seeds preserve the direct reader boundary; authorization passes zero seeds.

The [receipt](health-key-reader-c-review.json) records REA instruction evidence, compiled objects and verification:

- 320 direct stock/C pairs execute the real C key loader and CRC implementation. Cases cover four cache flags, ignored lengths, valid/invalid CRC, successful/failed flash-read status, lazy binding and missing partition/device combinations. Both success and failure occur.
- 692 lifecycle startup/reset/event pairs execute C authorization, key reader, storage recovery and profile handling. Both cached and flash-backed authorization paths are covered. The flash fixture resets its transaction phase for each new key-header read, allowing authorization and previous-state restoration to share the partition.
- Three defective variants are rejected: using the ready byte as the cache flag, testing the full 64-bit loader result and honoring the ignored length.

Flash callbacks, FAL lookups, logs and engine boundaries remain modeled. The actual stock memory mover executes in replay; this is not a fully source-only subset link. Accepted partial body reads that inherit scratch contents, private-stack aliases and physical hardware execution remain outside this proof. No byte identity is required or claimed.

The normal source report is `build/sources-goal-r1-health-key-reader-final/report.json`: 727 compiled units, no failures or duplicate strong symbols, 178 application imports and 34 bootloader imports. The key-reader import resolves. One unit was added, the authorization and lifecycle objects changed, and 724 objects remain unchanged from the previous checkpoint. Both manifests pass `make sources-check`. Engine parameter setting and initialization remain unfinished.
