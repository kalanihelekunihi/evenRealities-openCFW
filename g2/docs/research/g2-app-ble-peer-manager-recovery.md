# G2 BLE peer-manager recovery

## Result

`platform\ble\app_ble_peer_mgr.c` is closed as a four-function, 512-byte
G2-local Cordio application adapter. It is not a remaining third-party
dependency. The object owns a seven-byte pending-peer tuple (six-byte address
plus address type), finds an existing connection across three 48-byte Cordio
connection records, and sequences unpairing differently depending on whether
that peer is connected or opening.

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
Production implementation remains deferred with the surrounding central BLE
state machine; this audit only closes ownership, ABI, bounds, and behavior.

Reproduce with:

```sh
python3 tools/analyze_g2_app_ble_peer_manager.py
python3 -m unittest -v tests.test_analyze_g2_app_ble_peer_manager
```
