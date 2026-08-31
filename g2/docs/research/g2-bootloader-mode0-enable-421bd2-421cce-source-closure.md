# G2 bootloader mode-zero enable source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The complete authenticated mode-zero enable service at
`[0x00421BD2,0x00421CCE)` now compiles from maintained clean-room C at its
exact stock address. Apple clang 21 and Homebrew clang 22.1.8 reproduce all
252 installed bytes exactly.

The service requires the controller-table mode-zero seam and returns status 7
without side effects when it is unavailable. An already-active row-two client
refreshes the bounded timeout from the published state, republishes the stack
cell inside the critical section and runs cleanup without querying or changing
the mode. A new client queries the current state, inherits a live timeout,
applies control request 3 with byte value 1 for table mode one or request 2
with a null argument for table mode zero, and publishes the active flag when
needed. Incompatible state/table-mode pairs return status 3 without setting
the bitmap. Compatible paths set the low-byte-selected row-two bit, publish
the timeout while active, restore the saved interrupt mask and perform bounded
cleanup.

`runtime_mode0_enable_421bd2.c` is 6,901 bytes with SHA-256
`c1b1a9415c9f4604e554c881edbb1df8bb81b6ee499585f3e817410d746785a4`.
The installed 252-byte body has SHA-256
`beaa4d231ad6eca158c9b2aac09a55b69258e213980ac1ce2cd704a33d1344f5`;
the authenticated unrelocated body has SHA-256
`c33fb26dfd3d62285e53e575c0564e6c42ef229f33e4851a264a5f66c0859d11`.
Nine strict calls bind bitmap test/update, two critical-state saves, state
query, two control requests and two source-owned cleanup calls. Six focused
tests pin the body and `0xB51C` successor halfword, exercise missing-controller,
existing-client refresh, idle control/publication and incompatible-state
behavior, and compile with both reviewed Cortex-M55 toolchains.

Canonical accounting becomes 17,467 source-owned, 16,528 generated patch, 16
alignment, and 129,829 retained official bytes, including 362 cave bytes and
1,880 exact in-place bytes across 222 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,586,257-byte flash plan has SHA-256
`a7a6aa289b102cc7ac7ca622fb20fca60774cc2ca884447b4a0ed3e499fdd875`
with 6,590 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. Offline behavior and installed bytes are
closed, but live interrupt timing, controller/register effects, shared
bitmap/state ownership, polling and physical mode-zero behavior require
authorized hardware evidence. That evidence is unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
retained executable body begins at `0x00421CCE`.
