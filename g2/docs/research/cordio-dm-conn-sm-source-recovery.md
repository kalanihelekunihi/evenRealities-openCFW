# Cordio DM connection state-machine source recovery

The stock G2 image contains one complete `dm_conn_sm.c` function and its
state table. `dmConnSmExecute` occupies `[0x00533EF4,0x00534532)` (1,598
bytes); its 58-byte literal pool ends at `0x0053456C`. The complete physical
translation-unit footprint hashes to
`dc8d749ab17a2a225e784c1e722eb3a17d72ccfec595f674295a373281021575`.

The decisive version evidence is not the C function text, which is invariant
between Packetcraft r19.02 and r20.05. It is the 80-byte table at
`0x006ECC58`: five states, eight events, and two bytes per entry. Stock also
masks the WSF event with `7`. Packetcraft r19 and AmbiqSuite 2.4.2/2.5.1 use
thirteen events per state and a `0x0F` message mask. Packetcraft r20 moves
connection updates into `DM_ID_CONN_UPD`; its five-by-eight table matches
stock byte-for-byte.

The safe public semantic base is therefore Packetcraft r20.05 through
r20.05c, blob `58c5c6e1e4df5744c9a41902634cdd23a1aef906`, under Apache-2.0. Stock is
not an exact compilation of that public text: it expands five diagnostic
sites, validates the action-set ID against three, and reports an invalid set.
Those additions remain clean-room behavior evidence rather than copied
vendor source.

At runtime the function reads `pMsg->hdr.event` at offset 2 and
`dmConnCcb_t.state` at offset `0x15`, updates state before dispatch, then uses
the high action nibble to select one of three action sets at SRAM
`0x20073FE4` and the low nibble to select the member. The recovered main,
master, and slave tables point to the already bounded `dm_conn.c` and
role-specific actions. Two direct callers are proven at `0x004B689E` and
`0x004B690E`; there are no stored pointers or exterior interior branches to
the function.

The fail-closed reproducer is
[`../../tools/analyze_g2_cordio_dm_conn_sm.py`](../../tools/analyze_g2_cordio_dm_conn_sm.py).
It authenticates the official firmware, body, pool, retained path, state
table, callers, all 90 direct logger relocations, literal cells, and action
tables.

## Production admission

`runtime_cordio_dm_conn_sm.c` now owns the executable dispatcher. One guarded
redirect replaces all 1,598 stock function bytes with 120 compiled Cortex-M55
bytes under two strict relocations. The implementation masks the event to
three bits, validates the five-state CCB before table access, writes the next
state before action dispatch, validates all three action-set pointers and their
6/2/4 member bounds, and falls back to the authenticated no-action provider.
The exact 80-byte r20 transition table and 58-byte TU pool remain retained,
authenticated constant data rather than executable software gaps.

The host oracle exhaustively runs all 40 state/event transitions and exercises
null CCB/message, invalid state, absent action-set, and absent action-pointer
paths. Full and selector-isolated Cortex-M55 builds, exact routing, component,
manifest, deterministic package, and flash-plan checks pass. The canonical
overlay/component/package sizes are 357,394 / 3,880,790 / 4,659,284 bytes;
the 3,586,814-byte flash plan has 5,160 placed, two unresolved, five
container-only, and six protected regions.

No image was signed, flashed, or installed. Live connection establishment,
controller completion, role-action timing, cancellation, disconnect, and
paired-temple behavior remain blocked by unavailable authorized responsive
G2/EM9305 physical evidence.
