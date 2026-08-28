# G2 bootloader stage-one status source candidate

The next sequential frontier after the retained qsort wrapper is a complete
five-function subgraph at `[0x00423D20,0x00423DCE)`. It contains 168 executable
bytes and one six-byte alignment/literal island. The exact clean-room target
assembly in `research/admission/bootloader_stage_one_423d20/` reproduces all
174 authenticated bytes after its nine typed call relocations are applied at
the stock address. Its resulting SHA-256 is
`40a472fa5f161c713a218060464481a0f2722dea60bff8b8a6a51253264481bc`.

## Closed behavior and ABI

The entry at `0x00423D20` is the stage-one Thumb seam already called by the
guarded teardown service. It runs both local status predicates, clears bits 4
and 0 at `0xE0000E80`, waits on that register, then calls the source-owned
debug-disable service. The lower status helper returns four if either wait
predicate fails; on success it delays 500 units and returns zero. The two
predicate leaves normalize retained-provider success (`0`) to boolean one.

The exact relocation graph is:

- four local calls among the five maintained functions;
- three typed calls to retained status-change provider `0x0041D21C`;
- one call to the BSD-3-Clause source-owned debug-disable provider
  `0x00422468`;
- one duration-500 call to retained delay provider `0x0041D1C0`.

The maintained header records every function and provider ABI. The separate
MIT host model exercises success, both predicate failures, status propagation,
debug return behavior, register masking, address derivation, and delay policy
without dereferencing target MMIO.

## Provider and admission boundary

The local assembly, header, and model remain an exact MIT-licensed clean-room
candidate. An equivalent MIT clean-room C admission landed
concurrently in `runtime_hw_control_services_423d20.c`; the current analyzer
now verifies its five exact production bodies and no longer reports this range
as opaque or unrouted. Debug-disable is already source-owned under
BSD-3-Clause-compatible provenance. The two retained providers are
attributable to first-party Even bootloader services, but their maintained
source and binary redistribution authority remain unresolved. They stay typed
external seams and their official bytes are not copied or relicensed here.

Source ownership of the calling functions is now closed, while standalone
binary redistribution remains fail-closed until both retained providers are
source-closed or accepted under documented authority. The stage-two successor
at `0x00423DD0` and provider-free state mapper at `0x00423E14` are also
source-owned concurrently; the next production source gap begins at
`0x00423E40`. No overlay, package manifest, hardware, signing, or flashing path
was changed by this isolated reconciliation.
