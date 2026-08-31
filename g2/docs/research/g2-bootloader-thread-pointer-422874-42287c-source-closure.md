# G2 bootloader thread-pointer source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The authenticated eight-byte IAR-compatible runtime leaf at
`[0x00422874,0x0042287C)` now compiles from maintained MIT C at
its exact stock address. Its instruction body loads the adjacent source-owned
literal `0x20000518` and returns it; the complete body/literal SHA-256 is
`15e4706dbe2a251bc34a133f37c69c8ac3b76df463aa23f70fc4415b9a96621b`.
The sole direct caller is `0x0041ED04`. Both reviewed Cortex-M55 compilers
reproduce all eight bytes with no relocation.

`runtime_thread_pointer_422874.c` is 555 bytes with SHA-256
`d5f70fe3be26ea09ee61dfe5272cb781e894c2e357286a7dea5a0f36aa34fa79`.
Three focused tests pin body, caller and successor, verify the host runtime
anchor, and compile both profiles. Canonical accounting becomes 20,267
source-owned, 16,528 generated patch, 16 alignment, and 127,029 retained
official bytes, including 362 cave bytes and 4,680 exact in-place bytes across
255 source-owned functions and 201 patch sites. The 4,615,090-byte flash plan
has SHA-256
`b20ec5bf6f36bf5263858770e082a33890575642d11b27e69f418922da7b707e`
with 6,631 placed, two unresolved, five container-only and six protected
regions. Provider and unsigned-package hashes remain unchanged.

No hardware operation occurred. The meaning and lifecycle of the SRAM runtime
anchor require authorized Apollo510 evidence, unavailable because no
authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
executable body begins at `0x0042287C`.
