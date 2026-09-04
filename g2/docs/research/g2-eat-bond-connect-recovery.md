# G2 pathless eAT bond/connect command recovery

Status: complete two-handler census, clean-room implementation, dual-profile
production routing, and fail-closed behavioral analysis. Historical source is
unavailable. Run addresses use `run = file_offset + 0x00437FE0`.

## Result

Two handlers and their private pool occupy `[0x005A4FA4,0x005A4FD0)`, ending
exactly where retained `at_buzzer.c` begins. `AT^CLEANBOND` owns a sixteen-byte
body, while `AT^BLE_KEEPCONNECT` owns an eighteen-byte body. Their 34-byte
concatenation has SHA-256
`3e9408b876d80efd450be92dcd28f209c51fba952fef4d93431198bad37f66d4`.
The ten-byte alignment/pool tail has SHA-256
`b2a1b8bf327cbfd103f143d160bf78ce3b58c79a9eb8a24f4e5279a8dbb43cbc`;
the complete 44-byte object has SHA-256
`32c7ffcc3bff0ac19951e69f662ee02c93ede84871d98e026f65c0db3f72c5d6`.

Records `[0x006C9260,0x006C9280)` provide the only two entries. The clean-bond
handler calls provider `0x004B46CE`, emits `CLEANBOND+OK`, and returns zero.
The keep-connect handler calls provider `0x0046F2DC` with argument one, emits
`BLE_KEEPCONNECT+OK`, and returns zero. The pair has four direct provider calls
and no direct entry, stored strict-interior pointer, or direct `BL`/`B.W`
strict-interior target.

No retained source path or exact historical symbols survive. The manifest's
handler names are descriptive. Historical source partition, inventory,
source-only count, license, and whole-source identity therefore remain
unknown.

## Production closure

The MIT clean-room implementation in `eat_bond_connect.c` reproduces the two
observable contracts: provider `0x004B46CE` plus `CLEANBOND+OK`, and provider
`0x0046F2DC(1)` plus `BLE_KEEPCONNECT+OK`; both return zero. Two isolated
functions compile to 46 bytes plus two alignment bytes under both reviewed
profiles. Four strict relocations bind the two retained BLE providers and the
retained output provider. The original 16- and 18-byte command entries are
replaced by guarded wide branches, while the ten-byte response-pointer pool is
retained.

Independent Apple and Linux canonical generations are byte reproducible. The
production components are 3,956,672 bytes with SHA-256
`90899422791207c0f91d9fd3c54dcba2bba8ebc6797de47ff5014b60c070d9df`
and `918c5888ac8b417efa21fc406de63ccffd8d9a5a24c5b80d18ec51d37e9a1a50`.
The complete packages are 4,750,780 bytes / SHA-256
`3afb463643b4c71538ef9ee9fbfe8dcac6860c93c49ff8dcc96f36a2e4e25c8a`
and 4,750,764 bytes / SHA-256
`58db365724602dc68da5ac435e13abeda6fb25320649b6c6dd8d9af6e7c2497e`;
both flash plans have zero unresolved regions.

The software functional gap is closed. Physical qualification is explicitly
blocked by unavailable evidence: it requires an authorized bonded G2/peer
trace proving bond deletion and fresh pairing, plus an authorized connected
G2/peer trace proving the intended keep-connect policy. No hardware operation
was performed.
