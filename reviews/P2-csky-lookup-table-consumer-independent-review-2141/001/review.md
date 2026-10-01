# Independent review 2141: C-SKY lookup-table consumer

**Result: PASS_STATIC_SCOPED.** Candidate `analysis/csky-lookup-table-consumer-2074/001` remains unaccepted.

The source slice and conditional coordinate agree: `0x10024BE0 - 0x10023400 = 0x17E0`. The 400-byte body spans child `[0x17E0, 0x1970)`, with 396 code bytes followed by the four-byte `0x200266E0` literal. The task hint `0x18E0` instead maps to `0x10024CE0`, within the body.

The frozen verifier reruns successfully and checks source/body geometry, C-SKY disassembly, local and direct edges, 20 caller windows and arguments, dependencies, static translated fixtures, and artifact hashes. The pseudocode’s branch, arithmetic, read/modify/write, and output-store descriptions are consistent with the included listing. These fixtures are translated checks, not C-SKY execution.

The packet correctly leaves the conditional mapping unproven as a physical load. Live table initialization, indirect callers, surrounding caller behavior, hardware effects, and whole-image coverage remain open. No canonical records were changed.
