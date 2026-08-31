# G2 bootloader row-four enable source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated row-four enable transaction at
`[0x00421D5E,0x00421E4A)` now compiles from maintained clean-room C at its
exact stock address. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
236 installed bytes exactly.

An existing low-byte-selected row-four client refreshes the published timeout
inside the critical section and performs bounded cleanup. A new client
inherits a live timeout, rejects an unavailable ready seam with status 1, and
on the first row-four client enables the retained switch provider and applies
the retained configuration. Apply failure rolls the switch back and suppresses
bitmap mutation. A successful first-client path sets the active byte only when
neither active nor complete is already asserted. Compatible paths set the
row-four bit, publish the timeout while active, restore the interrupt mask and
perform cleanup.

`runtime_row4_enable_421d5e.c` is 6,621 bytes with SHA-256
`71b3c419411ca163c0dbfa037a65d057d7f5c8e2494dd04fa68587d8b6c41eeb`.
The installed 236-byte body has SHA-256
`680cf0628b0c3ed785836da7faeb3fcecf7ab51a02c90ed91c2c5b18442ef899`
and unrelocated SHA-256
`09cf993a663899cbbb105c84d248508c483ed1cdda6d27136130d39e680b8839`.
Ten strict calls bind bitmap test/count/update, two critical-state saves, two
cleanup calls, two switch calls and retained configuration apply. Six focused
tests pin the body, literals and `0xB51C` successor; cover existing-client,
not-ready, first-client success and apply rollback; and compile both profiles.

Canonical accounting becomes 17,847 source-owned, 16,528 generated patch, 16
alignment, and 129,449 retained official bytes, including 362 cave bytes and
2,260 exact in-place bytes across 225 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,588,397-byte flash plan has SHA-256
`b286aa443bba236715be039559aad7af48f61923b1033dea577b256a68efc0ed`
with 6,593 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, retained switch/apply behavior, shared
bitmap/state ownership, polling and physical row-four behavior require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x00421E4A`.
