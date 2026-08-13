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
tables. This work adds no production-owned implementation bytes.

The adjacent `dm_dev.c` tranche is now independently closed. Continue with
`dm_dev_priv.c`, then `dm_main.c`, to bind the privacy-event consumer and the
global component-interface initialization/dispatch path.
