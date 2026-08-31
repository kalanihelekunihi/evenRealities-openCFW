# G2 bootloader mode-one services source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated three-function cluster at
`[0x00421B08,0x00421BD2)` now compiles from maintained clean-room C at its
exact stock addresses. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
202 installed bytes exactly.

The enable leaf requires the controller-table mode-one seam, returns status 7
when unavailable, idempotently checks bitmap row 3, applies the low-nibble-A
control word through request 15, then marks the low-byte-selected client bit
inside the saved interrupt mask. The disable leaf clears that bit and applies
the authenticated disable word only when row 3 becomes empty. The cleanup leaf
polls the active flag through the source-owned bounded poll helper, then clears
the active byte at `0x2002719B` and state word at `0x20027040` inside the
critical section.

`runtime_mode1_services_421b08.c` is 6,203 bytes with SHA-256
`8077cacca6e4a7aa4124bab60ecc1f0f7bcb30bea417aee21e509a46f8819abe`.
The installed body SHA-256 values are
`891c88359e96db91d98fd0b159621ca6da87bc784c0e3280f4a625dcc1aad579`,
`0ec002b261917a95a5afe815494a62f850408c5de5b3a911e81fe3b1df23d06d`,
and `7bce9267762f0c94865d13a566fd4c0476bf127b1f1781e659016de79124461b`.
Eleven strict calls bind source-owned bitmap test/update/nonempty and poll,
critical-save, and the retained control provider. Five focused tests pin all
bodies, literal seams and successor; exercise missing-controller, idempotent
enable, last-client disable, cleanup and both reviewed Cortex-M55 compilers.

Canonical accounting becomes 17,215 source-owned, 16,528 generated patch, 16
alignment, and 130,081 retained official bytes, including 362 cave bytes and
1,628 exact in-place bytes across 221 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,585,553-byte flash plan has SHA-256
`8a5e7cf810b4769885a52161425c6e7a8fd432295337936832f152f8217dabdd`
with 6,589 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, control-provider/register effects, shared
bitmap/state ownership, polling and physical mode-one behavior require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x00421BD2`.
