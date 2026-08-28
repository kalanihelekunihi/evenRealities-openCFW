# G2 bootloader Ambiq debug-service source closure

Three authenticated executable bodies at `[0x00422468,0x00422574)` now compile
from maintained BSD-3-Clause C at their exact stock addresses. Their behavior
and ordering match AmbiqSuite SDK 5.1.0 `am_hal_debug.c` at public commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`; that upstream file is 11,141
bytes with SHA-256
`08e762d766432a883e1cdc2f1de2851614864f1a02d64cff45ae046538a2f61d`.
Apple clang 21 and Homebrew clang 22.1.8 reproduce all 268 installed bytes
exactly. The preceding 56-byte and following 28-byte literal pools remain
separately authenticated official data.

The debug-disable entry reference-counts general debug users, clears the TPIU
enable and clock-selection fields only for the last user, releases trace and
debug-domain ownership, restores `PRIMASK`, and returns the power-release
status exactly as stock. The debug-power helper tracks whether the domain was
already powered before the first acquisition, enables it only when necessary,
returns status `3` while nested users remain, and disables only a domain it
originally acquired. The trace-disable entry reference-counts `TRCENA`, clears
`DCB->DEMCR.TRCENA` for the last user, and polls the register for up to 10
microseconds through the retained HAL status-change helper.

`runtime_debug_services_422468.c` is 8,253 bytes with SHA-256
`dc61d1697c5315dc6a710cd940f7a268895068858f80e89096b7c2a83c4eca0b`.
The 74-byte debug-disable body has SHA-256
`9814e1b60b7637ccba467334aa7b21c00499c3cf7cae113298c14382895a128c`
and unrelocated SHA-256
`fccc921fbcf5076d90a68b9a19cab34f8b22779999f57f1dcc308f53888959ea`.
The 124-byte power helper has SHA-256
`b7b01e46563d81bfb3fc99e96b55564bde5536b1fc5fa05f181d968b66b3d6c1`
and unrelocated SHA-256
`90a2c7394eb23338470616de86b9ff53522a75234096c4d192f6b6d87f6e7062`.
The 70-byte trace-disable body has SHA-256
`61f149cf2cde2cd012ae5681429719effeefa99fd267a9231880ba21d3253bdc`
and unrelocated SHA-256
`dec5bbd49b16463b5453f30c7bd409ec680ac439a05f312b4f7fe25390ac8198`.
Nine strict calls bind maintained critical-save plus retained power query,
enable, disable and register-poll providers; reviewed aliases preserve the two
same-cluster calls. Five focused tests pin all bodies, pools and two callers;
exercise nested and last-user power/trace/debug behavior, prior-domain
ownership and register polling; and compile both reviewed profiles.

Canonical accounting becomes 19,559 source-owned, 16,528 generated patch, 16
alignment, and 127,737 retained official bytes, including 362 cave bytes and
3,972 exact in-place bytes across 239 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,601,055-byte flash plan has SHA-256
`86eb2b27d03838ed63186d44aa8d1077aafd8767a5b381c36fadc1ce29ed66cf`
with 6,611 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. Live debug-domain power, MCUCTRL/DCB register
effects, trace pipeline quiescence, nesting across retained callers and timing
require authorized Apollo510 hardware evidence. That evidence is unavailable
because no authorized responsive right temple exists and the left temple must
remain stock. Firmware-wide functional completeness is not claimed; after the
authenticated 28-byte literal pool, the next executable body begins at
`0x00422590`.
