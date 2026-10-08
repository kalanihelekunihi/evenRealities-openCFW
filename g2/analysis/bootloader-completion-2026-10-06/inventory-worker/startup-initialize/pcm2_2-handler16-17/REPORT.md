# PCM2.2 selector 16 transition handler

The authenticated selector table maps selector 16 to Thumb target `0x42962d`
(function entry `0x42962c`). The locked function range is
`[0x42962c, 0x429700)`, 212 bytes, SHA-256
`2b4c090e8bf6f3a2913292d2a4c7b9e1c8ef90ea746d0575bdca6c8153cdca17`.
`verify.py` checks the selector-table mapping, corpus extent/hash, and
one-byte-short/one-byte-long negative controls. The verified disassembly is
in `handler16.disasm`.

`handler16.c` follows the fixed-address r0-r3 transition ABI, reconstructs
the target profile's cached VDDC, VDDF, core-active and temperature fields,
updates the selected low-voltage trim, and preserves the stack-overwritten
return ABI in r0/r1. The timer gate checks bit 0 of `0x400083e0`; timer-ready
checks bit 30 of `0x40008064`, as derived from the original `LSLS #31` and
`LSLS #1` instructions. Timer service, delay and clock calls resolve to the
frozen `final-candidate.elf` symbols; the addon imports symbols only and does
not modify that base ELF.

`comparison.json` passes 14 direct stock-instruction versus compiled-source
fixtures: eight timer-disabled cases with nonuniform profiles and varied
state indices, plus six timer-enabled state-2/7/26 cases with ready and
not-ready status. Results compare both return registers, state, ordered MMIO
writes, wait cycles, callee-saved registers, SP and PRIMASK. All 212 locked
instruction bytes were visited. The source side loads the frozen final source
segments and the handler addon, and traps on execution into the locked image
address range. The only controlled timing edge is the ROM cycle-wait service
at `0x40`; timer and clock helpers execute from the source ELF.

`comparison-walker-selector16.json` also runs the actual locked temperature
walker (`0x42a43a`) and selector (`0x42a2b4`) with the compiled source walker
and selector. It authenticates the complete 27-entry table at `0x20000158`
(108 bytes, SHA-256 `81c33f127f9fe57795f236e7316cbfb32ff43cd576ba1b5256b3d7bf7b4dee21`)
and the 28-byte temperature matrix at `0x433498` (SHA-256
`d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8`). For
current state 6 to target state 5, the matrix yields base sequence 25; the
temperature crossing resolves selector 16. Both stock and source walkers
call the handler with `[5, 6, 3, 1]` and return `[r0=16, r1=1]`, preserving the
walker's saved-r2/r3 stack behavior. The source binds only callback-table slot
16 to the compiled handler; the remaining entries retain their authenticated
installed target values. This fixture establishes the selector16 call chain
for this transition, without claiming it was observed in the existing
`stock-root-targets.json` root trace (which reports selectors 14 and 18).
The walker test visits 80/130 walker bytes, 152/390 selector bytes, and
202/212 handler bytes on this single path; the direct handler matrix covers
the full handler extent. Offline emulator results are not a whole-firmware
source-completeness or hardware claim.
The initial void-source-walker attempt returned the handler's r0 and failed
the original walker ABI comparison; that counterexample is preserved in
`comparison-walker-abi.failure.json`. The source wrapper now returns the
selector ID and original r3 value recovered from the locked stack behavior.

The relocated standalone candidate is `/tmp/opencfw-root-pcm22-relocated/candidate.elf`,
SHA-256 `5996889d3156e75c175ab012c9166a0ffccc6192534c33d8a9ee8b0a09f5b3c5`.
`comparison-relocated-direct.json` passes the 14 direct fixtures and executes
all 212/212 locked handler bytes against that candidate's native selector16
implementation. Before fixture state is seeded, the source machine executes
`opencfw_boot_install_initialized_data`; no selector-table slot is manually
rebound. The installed 1371-byte source data normalizes to the stock decoder
output hash `e3bea7ccd46bc324829152b5b5a9069aecce5db243876273084d29bd7d47b843`,
and source slot 16 contains relocated native function pointer `0x324d9`.

`comparison-walker-selector16-relocated.json` exercises the authenticated stock
walker/selector path against that same standalone candidate. It executes the
source installer and validates callback relocations before starting the path.
Both timer-disabled and timer-enabled fixtures pass; stock and source call
selector16 with `[5, 6, 3, 1]` and return `[r0=16, r1=1]`. This path covers
80/130 walker bytes, 152/390 selector bytes, and 202/212 handler bytes; the
direct matrix covers the full handler extent. Source execution traps if it
reaches locked-image addresses. The only controlled timing edge remains the
ROM cycle-wait service at `0x40`.

Run `make verify`; `BASE_ELF` defaults to
`/tmp/opencfw-root-pcm22-relocated/candidate.elf`. Earlier receipts and the ABI
failure counterexample remain preserved for audit.
