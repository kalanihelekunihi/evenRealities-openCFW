# G2 BLE peer-manager recovery

## Result

`platform\ble\app_ble_peer_mgr.c` is closed as a four-function, 512-byte
G2-local Cordio application adapter and is now replaced by maintained MIT C in
`components/apollo_main/core_overlay/app_ble_peer_manager.c`. It is not a
remaining third-party dependency. The object owns a seven-byte pending-peer
tuple (six-byte address plus address type), finds an existing connection across
three 48-byte Cordio connection records, and sequences unpairing differently
depending on whether that peer is connected or opening.

The authenticated current object is `[0x004D8F4C,0x004D914C)`: 446 code bytes
and 66 bytes of alignment/literal-pool data. The retained path anchors only
`findConnIdByAddr` and `AppBleMasterPeerMgrUnpairDev` (420 bytes). Contiguous
recovery adds the 22-byte `AppMasterSecClearAddr` and four-byte
`AppMasterSecGetAddr`, bringing the complete linked inventory to four.
Seven direct calls enter exact function starts, 30 direct calls leave the
object, no call targets a strict interior address, and no function entry is
stored in data.

## Behavior and prior-firmware shortcut

Retained function strings name `findConnIdByAddr` and
`AppBleMasterPeerMgrUnpairDev`. Past analysis of the older G2 image supplies
the exact adjacent `AppMasterSecClearAddr` and `AppMasterSecGetAddr` names and
the earlier three-function topology. Their tiny bodies remain structurally
invariant: clear zeroes seven bytes then writes address type `0xFF`; get
returns the tuple address.

The current unpair operation copies the requested address/type and queries
connection state. If no connection is active it removes pending reconnect
work and unpairs immediately. If the peer is connected or opening, it records
the pending tuple, resets retry work, and closes the link so unpairing can
complete after disconnect. The new `findConnIdByAddr` helper performs the
three-record address lookup. This explains the current image's larger
four-function object without inventing an upstream library source.

The seam below it is now also clear: Cordio/Ambiq supplies connection-address
and application-database APIs, while this file supplies G2 product sequencing.
## Production closure

The maintained implementation exports all four recovered functions. It uses
the exact SRAM tuple at `0x200003D8`, the three connection records at
`0x200717B0`, and strict retained-provider bindings for Cordio address lookup,
application master state, delayed-work removal, target selection, and the two
unpair events. Diagnostic logging is intentionally omitted. Host execution
tests cover null input, successful and exhausted record lookup, tuple clear/get,
the active-connection path, the record-found path, and immediate disconnected
unpairing including exact provider order and arguments.

The four leaves compile to 326 executable bytes under both reviewed profiles,
with eight Apple and twelve Linux alignment bytes. Seventeen strict relocations
are closed. Guarded wide branches displace all 446 stock body bytes; the
66-byte stock literal/pool tail remains retained noncode. Two independent
generations per profile produce Apple component SHA-256
`2ae9d295b6d07bf241cb3a10082d7a4ac68b4a10f35c3c4bb348298100e024de`
and Linux component SHA-256
`c568f98d70de52528d38335bf0b5b318c47e46aefb62e95e50772c0158c271c3`.

The software functional gap is closed. Physical qualification remains
explicitly blocked by unavailable evidence. It requires an authorized bonded
G2/peer trace showing that active/opening-peer disconnect completes deferred
unpair and permits fresh pairing, plus an authorized disconnected-peer trace
showing immediate address-based unpair clears persistence without initiating a
connection. No hardware operation was performed.

Reproduce with:

```sh
python3 tools/analyze_g2_app_ble_peer_manager.py
python3 -m unittest -v tests.test_analyze_g2_app_ble_peer_manager \
  tests.test_runtime_app_ble_peer_manager
```
