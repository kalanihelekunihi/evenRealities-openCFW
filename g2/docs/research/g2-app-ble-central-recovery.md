# G2 BLE central-role and RingLink object recovery

Status: complete linked-object closure for stock G2 2.2.6.10. This is a
read-only analysis result; no recovered body is routed into production.

## Result

The retained path
`platform\ble\app_ble_central.c` owns a 15,752-byte physical object at
`[0x0049F828,0x004A35B0)`. It contains 44 functions / 14,288 body bytes and
30 intervening literal-pool or alignment regions / 1,464 bytes. The complete
object SHA-256 is
`8038f98faaa62f91addd9e09c1ae18b215c74abfb07579c21c20282a1e6a205d`.

This corrects the initial path-anchor-only lower bound in two ways:

- the first central helper is the 72-byte RingLink-state name mapper at
  `0x0049F828`, immediately after the independently authenticated literal pool
  for `ring_connect_policy.c`; and
- 20 functions have no central source-path reference in their own body. Fourteen
  are present in the authenticated baseline Ghidra census and six were restored
  by rooted Thumb control-flow recovery.

The six restored functions are:

| Entry | End | Bytes | Identification |
|---:|---:|---:|---|
| `0x004A1B60` | `0x004A1F30` | 976 | `APP_MasterConnectEvent` |
| `0x004A21CC` | `0x004A224A` | 126 | `APP_MasterScanEvent` |
| `0x004A22C6` | `0x004A22DE` | 24 | active-master-connection predicate |
| `0x004A285C` | `0x004A2864` | 8 | delayed ready-publication wrapper |
| `0x004A2EA4` | `0x004A2FB2` | 270 | `APP_MasterCancelRingConnectRetry` |
| `0x004A316C` | `0x004A34B0` | 836 | `APP_MasterTryReconnectRingByScene` |

Every restored entry has a direct call or stored Thumb-pointer witness, a
contiguous reachable instruction body, and a pinned return before the next
literal pool or function. The 256-byte final pool at
`[0x004A34B0,0x004A35B0)` retains the later central diagnostics and the seventh
copy of the source-path pointer. At `0x004A35B0`, a new valid Thumb prologue
starts independently rooted IMU helper code, so the central object does not
expand to the next Ghidra-discovered IMU function.

## Ingress and topology

The 44 entries have 160 halfword-decoded direct BL sites across the image, of
which 58 originate outside the physical object, plus 17 stored Thumb pointers.
The bodies contain 851 linked-image calls: 102 target another recovered central
entry and 749 target external providers. The stored pointers principally expose
the connect-event callback, system-start work item, connect-cancel callback,
and ready-publication work item.

One raw halfword pattern at `0x00631CEE` decodes as a BL to `0x0049FAF4`, which
is the middle of `_bleMasterScanStop` and begins with `cmp r1,#0x33` rather than
a callable prologue. It is retained as a strict-interior decode in the audit and
is not promoted to a second function entry. This distinction keeps the closure
fail-closed without inventing an ABI for an apparent data or unreachable-code
decode.

## Recovered behavior

The object is the product policy layer above Cordio, not an unrecognized Cordio
or other third-party source copy. Its state and provider topology covers:

- seven RingLink states: `IDLE`, `OPENING`, `CONNECTED`,
  `LOCAL_DISCONNECTING`, `SWITCH_DISCONNECTING`, `CANCELLING`, and `UNPAIRING`;
- scan selection, paired-record lookup, RPA resolution, RSSI selection, DM
  connection open/cancel, ATT discovery cancellation, and PHY/RSSI operations;
- application messages `0xAE` through `0xB4` for connect, disconnect,
  connect-cancel, unpair, scan, RSSI, and PHY operations;
- owner-side policy derived from dominant hand and device role;
- short retry, escalating retry, delayed failure notification, and the long
  retry interval;
- dominant-hand link switching, silent local teardown, complete unpair cleanup,
  and scene-triggered reconnect with 500/1000 ms scheduling.

These decisions, state encodings, diagnostic text, and application-provider
seams are G2-specific. Cordio remains a dependency through already admitted DM,
ATT, WSF message, security, and database APIs, but there is no missing
third-party source dependency to recover for this object.

## Cross-version evidence

The prior G2 decompilation corpus supplies 21 names and a stable ordering for
the older, smaller central object. It corroborates the scan/connect core,
`dmDiscCancel`, message dispatch, `APP_MasterConnectEvent`, target/auth helpers,
PHY, and retry-reset functions. It is used only as a naming and topology oracle:
the current image independently pins every byte, body, ingress site, literal
pool, path pointer, and boundary.

The current object is materially newer. It adds explicit RingLink states,
failure-notification arming, dominant-hand switching, unpair cleanup, and scene
reconnect. Therefore neither the prior image nor any public SDK identifies the
private commit that produced 2.2.6.10. Historical source and the exact producing
commit remain unavailable.

## Reproduction

Run:

```sh
python3 tools/analyze_g2_app_ble_central.py
python3 -m unittest -v tests.test_analyze_g2_app_ble_central
```

The analyzer authenticates the official payload, function and closure
manifests, all 44 bodies, all 30 non-body regions, both adjacent-object
boundaries, retained strings, seven source-path pointer cells, entry/call
topology, stored callbacks, and production-routing exclusion. The authoritative
tables are
`tools/manifests/g2-app-ble-central-function-map.tsv` and
`tools/manifests/g2-app-ble-central-closure.tsv`.
