# G2 BLE connection-parameter object recovery

Status: complete linked-object closure for stock G2 2.2.6.10. This is a
read-only analysis result; no recovered body is routed into production.

## Result

The retained path `platform\ble\app_connect_params.c` owns a 6,888-byte
physical object at `[0x00476CBC,0x004787A4)`. It contains 14 functions / 6,336
body bytes and eight intervening literal-pool or alignment regions / 552 bytes.
The complete object SHA-256 is
`ab0417a12435e9d204ccee9730a8a139d203516933de7587590b071ce5390deb`.

Ten functions contain a direct reference to the retained path. Four compact
helpers do not: `ble_msgtx_set_config`, `ble_msgtx_isConnected`,
`ble_state_skip_manual_start`, and `ble_param_reset_delayed_event`. All four
are independently rooted by external calls, retain the exact prior-G2 order
and behavior, and sit inside the closed physical interval. The boundary is not
an adjacency guess: the immediately preceding 204 bytes are the authenticated
final pool of `fw_event_loop.c`; the next address, `0x004787A4`, begins a
separately rooted 188-byte bond-erasure helper.

The object has 39 direct BL entry sites, 30 from outside the object, plus three
stored Thumb pointers to `_connectParamReq`. Its bodies contain 345 linked-image
calls, nine targeting another recovered connection-parameter entry and 336
targeting providers.

Two halfword-aligned scans appear to call strict function interiors:

| Apparent site | Apparent target | Authenticated containing instruction |
|---:|---:|---|
| `0x00483566` | `0x00477B72` | second halfword of `sdiv r7,r5,r4` at `0x00483564` |
| `0x00581EB6` | `0x004774C4` | second halfword of `udiv r6,r2,r5` at `0x00581EB4` |

They are Thumb-2 decoder artifacts rather than alternate function entries. The
audit pins the complete four-byte division encodings and retains both apparent
decodes as negative evidence.

## Ownership and behavior

This object is G2 product policy above Cordio, not another copied Cordio or
third-party translation unit. It depends on Cordio DM connection state, Cordio
WSF allocation/message delivery, and the G2 event loop, but its thresholds,
mode state, timers, role gates, ESS/OTA entry points, and retry sequencing are
product decisions.

Recovered behavior includes:

- fast event `0xA3`, slow event `0xA4`, and application request event `0xB9`;
- DM open, close, update-complete, and connection-parameter request handling;
- a fast/slow split at intervals 25 and 72 BLE units, with initial-policy
  selection changing the threshold used after connection;
- per-connection profiles for connection IDs 1 through 3, plus invalid-ID and
  central-role rejection;
- 2, 4, 10, 30, and 60 second retry/backoff/transition delays;
- immediate fast-mode paths for ESS and OTA, and a caller-selected delayed
  slow-mode reset.

Cordio is therefore a provider dependency, while the remaining opaque object
is G2-local. No additional third-party source admission is required for these
6,888 bytes.

## Cross-version evidence

The prior G2 corpus names 15 consecutive functions in this region. Fourteen
map in the same order to the current object. Seven retain the same body size;
the current `_connectParamReq_impl`, `_connectParamReq`, and
`APP_ConnectParamHandler` are larger, while several event/reporting bodies have
small size changes. The older 34-byte `ble_conn_param_log_format` helper is
absent: current `fw_event_loop.c` pool bytes extend directly to
`_bleSlaveConnUpdate`.

The older image and its historical clean-room reconstruction are used only as
a naming/topology oracle. They do not expose the private Even source revision
that produced stock 2.2.6.10, and no public dependency commit can identify a
first-party policy object. Every current body, gap, path pointer, retained
function string, ingress edge, and adjacent boundary is independently pinned.

## Reproduction

Run:

```sh
python3 tools/analyze_g2_app_connect_params.py
python3 -m unittest -v tests.test_analyze_g2_app_connect_params
```

The authoritative tables are
`tools/manifests/g2-app-connect-params-function-map.tsv` and
`tools/manifests/g2-app-connect-params-closure.tsv`.
