# G2 bootloader bitmap-client service source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated five-function cluster at
`[0x00421978,0x00421B08)` now compiles from maintained clean-room C at its
exact stock addresses. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
400 installed bytes exactly.

The 184-byte entry selects controller zero or one for a missing configuration,
queries `0x00427160`, validates explicit mode-zero/mode-one configurations,
enters a critical section, rejects active bitmap row 6 with status 3, and on
success publishes the 12-byte configuration at `0x20027004`, current instance
at `0x20027038`, and readiness byte at `0x2002719A`. Missing required
controllers return 7; query failures return before interrupt masking.

The four following helpers idempotently set and clear low-byte-selected bits
in bitmap rows zero and one. Mutation occurs only inside the saved interrupt
mask through the source-owned validated bitmap update helper. Row-one set also
requires the authenticated controller seam at `0x20000088` and returns 7 when
it is absent; row-one clear remains available for cleanup.

`runtime_bitmap_clients_421978.c` is 10,083 bytes with SHA-256
`d11a2f975a5d3edb5039a60b812dacebcac1a8b4ecc67002be9ed1f1b71c3a0e`.
The five installed body SHA-256 values are respectively
`14c0af33cbe710b3f3272f9ce0731f82c27f5ddf4c7586f8169264621335eb57`,
`55df16968e7cebea48cb197fa9e91b0534c3420fd587d2e362ee3f14e5f2ad12`,
`61afcf0355e0f2fdc9095ff5311cea9e3e52749acc277a981788ccd6f0833473`,
`0b01e6b1f407cd164536ca7c894b0cb48dcf7c2497814eb3187860633f189a4c`,
and `9aea3a0a0c095098f5c43b3cb3b34fb1565983cda5769771928650d440ef58d5`.
Sixteen strict call relocations bind query, critical-save, source-owned bitmap
count/test/update, and source-owned copy providers. Seven focused tests pin
the complete bodies, literals and successor; exercise query routes, validation,
busy/failure publication rules, low-byte narrowing, idempotence and guarded
row-one behavior; and compile with both reviewed Cortex-M55 toolchains.

Canonical accounting becomes 17,013 source-owned, 16,528 generated patch, 16
alignment, and 130,283 retained official bytes, including 362 cave bytes and
1,426 exact in-place bytes across 218 source-owned functions and 201 patch
sites. Apple/Linux providers and unsigned packages remain byte-identical at
their prior pinned identities. The 4,583,419-byte flash plan has SHA-256
`35e18ba118c505f5e13ad1f498e39a1d81b228128f594a03f761c5a557b6e270`
with 6,586 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but interrupt timing, controller/register behavior, shared bitmap and
publication ownership, and physical client behavior require authorized
hardware evidence. That evidence is unavailable because no authorized
responsive right temple exists and the left temple must remain stock.
Firmware-wide functional completeness is not claimed; the next retained
executable body begins at `0x00421B08`.
