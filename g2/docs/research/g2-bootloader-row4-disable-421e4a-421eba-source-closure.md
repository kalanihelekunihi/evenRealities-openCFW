# G2 bootloader row-four disable and cleanup source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated two-function cluster at
`[0x00421E4A,0x00421EBA)` now compiles from maintained clean-room C at its
exact stock addresses. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
112 installed bytes exactly.

The disable leaf idempotently returns success when the low-byte-selected
row-four client is absent. Otherwise it clears that bit inside the critical
section and calls the retained row-four switch provider with zero only when
the row becomes empty. The cleanup leaf short-circuits while the active byte
at `0x2002719D` is clear; an active path polls that byte, then clears it and
the state pointer at `0x20027048` inside the critical section.

`runtime_row4_disable_421e4a.c` is 4,598 bytes with SHA-256
`14eaa91fb7cf00d172a0e2db35a1ac36ecfd1a1a34ad017c61f80eea752d35a1`.
The installed 66-byte disable body has SHA-256
`f4f21abad8199cfea2524c7335d809b7f624100c1e34b693c08025ae1fb40a2a`
and unrelocated SHA-256
`a43ee47c5b1ad0f8e9b376fffb60463b727beb41414216056fd652461e25aff4`.
The installed 46-byte cleanup body has SHA-256
`113121d1847a984448cf18c516a0fbab330809872367ea03a787d3ba61b95985`
and unrelocated SHA-256
`3fbd749d081830bf6b9a11c6cf44cb4fefc4452a15cf61e79cc783a4c7241fe8`.
Seven strict calls bind bitmap test/update/nonempty, poll, two critical-state
saves and the retained switch provider. Five focused tests pin both bodies,
literals and the `0xB5FE` successor; exercise absent/nonfinal/last-client
disable and inactive/active cleanup; and compile both reviewed profiles.

Canonical accounting becomes 17,959 source-owned, 16,528 generated patch, 16
alignment, and 129,337 retained official bytes, including 362 cave bytes and
2,372 exact in-place bytes across 227 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,589,830-byte flash plan has SHA-256
`fc0579d838469b9ad02a69ca81a7bfeff40087aceb2a2401bd93d4d235ae6361`
with 6,595 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, retained switch behavior, shared
bitmap/state ownership, polling and physical row-four shutdown require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x00421EBA`.
