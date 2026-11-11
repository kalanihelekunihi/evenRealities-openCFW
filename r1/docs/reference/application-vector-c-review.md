# R1 application vector table in C

The locked 2.2.6.0009 application at `r1/blobs/official/r1-2.2.6.0009/application.bin`
(SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`)
has 128 vector words beginning at `0x27000`. `native_context_vectors.c` now
defines all 128 words in C: 54 nonzero slots, 74 reserved zero slots and 25
stock default-handler slots. A comparison of assigned indices and default
classifications against the locked binary passed. The source-linked initial
MSP is now `0x20040000`, the linker RAM top, rather than the stock
`0x2003beb8`: the relinked `.bss` ends at `0x2003c570` and would overlap the
old pointer by 1,720 bytes. The vector's C unit reserves 8 KiB for the MSP
in `.stack`; the linker places its lower limit at `0x2003e000`, leaving
6,800 bytes between static data and that limit.

The source table is placed in `.isr_vector`; the recovered application linker
script puts that section first in FLASH and aliases the SDK's single-word
`__isr_vector` declaration to the typed `r1_application_vectors` table. The
strict link map places the 512-byte table at `0x27000`. SVC, PendSV and the
RTC/SysTick and peripheral handlers reference existing C or authenticated
upstream providers. DebugMon and the 25 stock default IRQs retain terminal
loops in C.

The current `build/sources-r1-stack-reserved-20261111/report.json` compiles
963 application and 82 bootloader units. The strict application receipt at
`build/r1-link-stack-reserved-20261111/report.json` validates the 512-byte
vector, RAM top, stack reservation, static-data boundary and zero archive
members; the bootloader also links.
An old-MSP negative candidate under `build/r1-stack-negative-20261111/`
links at the GNU level but fails the strict image gate because its vector
points into `.bss`.

The earlier 951-unit build at
`build/r1-c-startup-final-20261110/report.json` compiled 869 application and
82 bootloader units, with no failures or duplicate strong symbols. Its
historical strict application receipt at
`build/r1-c-startup-final-20261110/app-link/report.json` confirms
the vector's size and address; its final link fails with 56 missing references
and 215,320 bytes of FLASH overflow.

Stock SWI2 at `0x32730` tests the protocol-service thread word at
`0x20006570`, then calls `osThreadFlagsSet(thread, 1)` when it exists.
`native_protocol_control.c` now supplies that handler using the existing
source-owned service-thread state and flag-set routine.

Five stock fault vectors call the CmBacktrace fault adapter. Their later
[C source adapters](application-fault-vectors-c-review.md) now preserve the
architectural LR/SP handoff. Static flash/RAM placement and reset copying now
pass the strict source link; runtime stack depth, hardware startup and byte
identity are still unverified.

The four CmBacktrace boundary names in `openr1_sdk.ld` now alias its existing
GNU stack and FLASH bounds. CmBacktrace takes the addresses of these symbols.
This closes the missing linker names; the current link checks the RAM bounds.
