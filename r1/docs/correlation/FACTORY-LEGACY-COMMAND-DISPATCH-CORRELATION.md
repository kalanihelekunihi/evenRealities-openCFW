# Factory legacy-command dispatch correlation

## Outcome

The factory-input command router at `0x000625C0..<0x000627CE` is now represented by a separate,
bounded, non-invoking C route API. Its 526 executable bytes have SHA-256
`900beb3e3b665c01332df2c6ae3f901c301a0510a24acf25f447a74e71dbc51b`.
The sole direct caller is the factory queue drain at `0x00045F84`.

This function was an explicit Ghidra analysis seed omitted from the canonical function CSV. The
independent prologue, terminal tail branch through `0x000627CD`, following alignment word, literal
pool, and body hash establish the manual extent.

## Relationship to the normal router

Like the normal 464-byte router at `0x0004E258`, the factory router clears the 36-byte workspace
at `0x2001A174`, copies the incoming frame, reads the opcode at offset 2, and recognizes the same
23 handler routes:

`11 12 21 22 23 24 34 37 40 52 53 54 55 56 57 85 88 89 8A 91 94 95 F2`.

The factory copy has two additional explicit branches. Opcode `10` returns without invoking a
handler. Opcode `8B` obtains one status byte, writes it at workspace offset 4, clears offset 5,
and requests a six-byte response. The clean API reports these as
`R1_LEGACY_COMMAND_ROUTE_FACTORY_NOOP_0X10` and
`R1_LEGACY_COMMAND_ROUTE_FACTORY_STATUS_0X8B`; it does not perform the status query or send.

## Clean-room boundary

`r1_factory_legacy_command_route_frame` shares the hardened 3-to-36-byte workspace copy with the
normal router and returns only a typed route. It never invokes any recovered handler, exposes the
factory queue over BLE, mutates pairing/authorization state, calls the command-`F2` table, queries
hardware, or sends a response. Every destination remains independently source-gated.

Tests cover the shared 23 routes, both factory-only branches, an unknown opcode, zero-filled
workspace behavior through the common implementation, and rejection of the two factory-only
opcodes by the normal router.
