# Shared read-only stack-pointer observation

`application/runtime/native_stack.h` now owns the compiler-specific SP
observation used by both TWI register reads and packet writes. It always
inlines. Callers still need separate evidence for their frame offsets and
provider ABI; observing SP does not establish that layout.

The normal Clang path retains the empty fixed-SP constraint already validated
in the TWI work. GCC uses `__builtin_stack_save`. The register-read copies
previously used the reserved-SP output under GCC, which generated a move
*into* SP at return. Packet writes had already gained a GCC-specific path;
that implementation is now shared rather than duplicated.

A generated GCC negative-control leaf contains `MOV SP,R3; MOV R0,SP; BX LR`.
REA read all six bytes from that controlled compiler probe. This is compiler
artifact evidence, not a read of shipped firmware. With incoming R3 set to
`0x12345678`, execution changes SP to that value; the negative control rejects
it. The new helper reads SP without that assignment.

Standalone strict Clang and GCC probes each pass 384 cases. They exercise a
leaf and callers with one-, four- and sixteen-word local arrays, several entry
SP values, raw seeds, interrupt masks and both thread-mode MSP/PSP selections.
At the modeled observer, the captured pointer equals the actual SP. Returns,
saved registers, masks and the inactive stack bank remain intact. Observed
caller depths are 16, 24 and 72 bytes for both compilers. These tests validate
the observation primitive, not any particular TWI frame size.

Both complete TWI source units also compile in GCC diagnostic probes, and
their disassembly no longer contains the unexpected moves into SP. Those
probes retain the existing probe-only `-Wno-error=unused-parameter` for SDK
SVC declarations. Product warning policy is unchanged. The GCC consumers'
native frame-layout gaps remain unresolved; they do not inherit the helper's
validation. Exception paths, dynamic allocation, concurrent access and
physical peripherals are outside this proof.

All 577 normal R1 Clang objects are byte-for-byte identical to the prior build,
including relocations. Both composed payload hashes, manifest, strong symbols
and import sets are unchanged. Imports remain 164 application and 34 bootloader
symbols. This also preserves the earlier normal Clang TWI execution evidence;
neither register-read nor packet-write machine behavior changed.

Official generic qualification compiles 20 variants and selects no regions.
All 12 strict GCC variants still fail on the SDK SVC diagnostics. The exact
source plan is unchanged. The canonical hybrid application retains locked
SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,035 source-built bytes, 642,125 retained executable bytes and 248 resource
bytes. Source-built totals include assembly/data. Complete source firmware
and bootstrap ABI completion remain unproven.

The [machine-readable receipt](native-stack-c-review.json) records compiler
commands, probe ELF hashes, REA, executions and byte-preservation audits.
Ignored probes are under `build/goal-r1-native-stack-c/`.
