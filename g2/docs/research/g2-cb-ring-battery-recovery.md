# G2 ring-battery callback facade recovery

The retained `platform\service\callback_mgr\cb_ring_battery.c` path had no
function in the baseline path census because its only path-referencing body
was missed by Ghidra. Raw source-order recovery closes five functions / 122
body bytes plus a 30-byte pool at `[0x00500378,0x00500410)`. The next halfword
is the prologue of a different callback. Six direct entries, ten body calls,
both boundaries, and the absence of indirect, stored, or strict-interior
ingress are pinned by the analyzer.

The facade owns generic callback list `0x20073F90` with retained type string
`RING_BAT_INFO`. It initializes/deinitializes that list, rejects a null
registration, registers valid callbacks, and publishes an event key with an
in/out value word. The latter is the exact 14-byte target used by
`UX_BatterySyncHandler` for changed level key 0 and charging key 1.

Five of ten calls are already admitted EasyLogger diagnostics. The others are
one first-party forwarding target and four generic callback-manager operations;
there is no CMSIS-FreeRTOS call or embedded third-party definition. Exact
public searches for the retained callback symbol and filename produced no
source candidate, so this object adds no version discriminator and cannot
reveal the private generating commit.

## Production routing

`components/apollo_main/core_overlay/cb_ring_battery.c` now supplies five
selector-isolated MIT clean-room leaves. Five guarded redirects replace
all 122 stock body bytes with 88 compiled Thumb bytes plus two alignment bytes;
each leaf has one strict relocation, terminating at either the source-owned
generic callback manager or the retained ring-battery consumer. The 30-byte
type, path, diagnostic, and literal pool remains authenticated stock data.

Host tests cover forwarding, fixed list/type identity, lifecycle, null
registration rejection, manager return propagation, and notification key/value
semantics. The canonical Apple overlay is 193,578 bytes with SHA-256
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`;
Apollo main is 3,716,974 bytes with SHA-256
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`;
and the complete 4,495,468-byte package hashes to
`03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 1,972,280-byte flash plan hashes to
`ef7a204c200024422defd2cb9e0064a5aa4278bb14533e4007bd0daf2db1e67f`.

This facade performs only in-memory callback-list operations and a bounded
call to the existing ring-battery consumer, so it introduces no independent
physical validation requirement. This closes the facade's software gap; it
does not close hardware-dependent gaps in the wider ring service.
