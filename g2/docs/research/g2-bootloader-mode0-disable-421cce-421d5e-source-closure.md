# G2 bootloader mode-zero disable and cleanup source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated two-function cluster at
`[0x00421CCE,0x00421D5E)` now compiles from maintained clean-room C at its
exact stock addresses. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
144 installed bytes exactly.

The disable leaf idempotently returns success when the selected low-byte
row-two client bit is absent. Otherwise it clears the bit in the critical
section and, only after the final row-two client leaves, applies control
request 4 with byte value 1, clears the mode-zero active byte at `0x2002719B`,
and clears the published state pointer at `0x20027040`. The cleanup leaf
short-circuits while inactive; an active path polls the byte at `0x2002719C`,
then inside the critical section sets completion byte `0x2002719E`, clears the
polled byte and clears state pointer `0x20027044`.

`runtime_mode0_disable_421cce.c` is 5,439 bytes with SHA-256
`5c40b78e55e7cfb57542a460120f109b20ed308a29c24ab91853fc3d1d453613`.
The installed 90-byte disable body has SHA-256
`3dac14d8bed9201a8c8e9147d2216bb399ccb35b33642840d4ad49ad3a691c6e`
and unrelocated SHA-256
`38233a55ad4a104cbf7b1f215f1179122b0ec875a1c17c8cab35366e8907daa6`.
The installed 54-byte cleanup body has SHA-256
`4b8c76a46e4a846d4c3320718698134d79310d3b4c6a4dc3cb5b0602ab00ba20`
and unrelocated SHA-256
`bf5376c2296cbc5c62a32a5788877e96171768a87a634d710b3d3bd75d730fef`.
Seven strict calls bind source-owned bitmap test/update/nonempty and poll,
critical-save, and retained control. Five focused tests pin both bodies,
literals and the `0xB57C` successor, exercise idempotent and last-client
disable plus inactive/active cleanup, and compile both reviewed profiles.

Canonical accounting becomes 17,611 source-owned, 16,528 generated patch, 16
alignment, and 129,685 retained official bytes, including 362 cave bytes and
2,024 exact in-place bytes across 224 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,587,696-byte flash plan has SHA-256
`c715ec177e33e23be701f1f2c24683c717a22beef84be5b49dd419926368ca43`
with 6,592 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, controller/register effects, shared
bitmap/state ownership, polling and physical mode-zero shutdown require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x00421D5E`.
