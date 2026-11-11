# Hardware candidate byte qualification

The official qualifier was run against the current STACMD transmit and hardware
TWI completion/wait units. All three compiled, but none produced a selected
region. A second pass tested recorded, O2, Os, Oz and Og settings with isolated
function linking and native-function matching enabled: all 15 variants compiled,
and none qualified. The official tool was unchanged; probe wrappers filtered its
candidate input to these three source paths.

STACMD parity is behaviorally tested but differs from the stock instruction body
at `0x968a8`. In the normal object both are 26 bytes: stock uses an incrementing
signed loop with parity in R0 and input in R3, while Clang uses a different
register allocation, increment encoding and branch condition. Equal size and
bounded stock/C results do not establish byte identity.

Completion/wait results additionally include unresolved isolated-link/native
bindings. Their negative result is not proof that their complete instructions
cannot match: the filtered candidate input limits the official binding universe,
and writable globals and internal helpers are not established native bindings.
Those issues require evidence-backed binding work before a stronger conclusion.

No firmware source, manifest, canonical source-plan entry or G2 gate changed in
this audit. The canonical plan SHA-256 remains
`964cbd3af9f4ea7ed207bb4b480d18a9529060dc3801663d296389472982aa7c`.
The last full R1 composition remains 562 compiled units, zero failures or
duplicate strong symbols, and 211 application / 34 bootloader imports. That
composition is separate evidence from this qualification pass.

The results identify remaining byte-build dependencies; they establish neither
source completeness nor physical hardware behavior. Source and tool hashes,
full rejection records and probe bindings are retained in the
[machine-readable audit](hardware-byte-qualification-review.json).
