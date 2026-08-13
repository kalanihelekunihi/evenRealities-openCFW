# G2 BLE peripheral-role object recovery

Status: complete linked-object closure for stock G2 2.2.6.10. This is a
read-only analysis result; no recovered body is routed into production.

## Result

The retained path `platform\ble\app_ble_peripheral.c` owns the 6,560-byte
physical object `[0x0046DB04,0x0046F4A4)`, SHA-256
`d03a512b45aaa2cd3d6476a258f54270553bb82f42524838a0b23e0f700d36d3`.
It contains 31 functions / 5,888 body bytes and 18 literal-pool or alignment
regions / 672 bytes.

Only 12 functions carry the source path directly. Nineteen more are required
for complete closure. Twelve were already present in the baseline Ghidra
census; seven were restored from direct calls or stored Thumb pointers:

| Entry | End | Bytes | Identification |
|---:|---:|---:|---|
| `0x0046ED08` | `0x0046ED5A` | 82 | `APP_BleNameGet` |
| `0x0046EE70` | `0x0046EEDA` | 106 | `APP_BleSlaveAdvStartEvent` |
| `0x0046EEEC` | `0x0046EF56` | 106 | `APP_BleSlaveAdvStopEvent` |
| `0x0046EFFC` | `0x0046F090` | 148 | slave-unpair event poster |
| `0x0046F098` | `0x0046F0E0` | 72 | disconnect advertising-restart work |
| `0x0046F2DC` | `0x0046F328` | 76 | advertising-stop flag merger |
| `0x0046F350` | `0x0046F3A2` | 82 | `_bleSlaveSyncConnectEvt` |

Every restored body has a rooted entry, contiguous reachable instructions, and
a pinned return before a pool or the next function. With those bodies admitted,
a whole-image halfword scan finds no remaining direct target into an unknown
location in the physical object and no strict-interior BL decode.

The 31 entries have 44 direct BL sites, 33 from outside the object, plus eight
stored Thumb pointers. The bodies contain 374 linked-image calls: 11 target
another peripheral entry and 363 target external providers. The immediately
preceding 56-byte ring-buffer helper and following 30-byte controller
channel-mask helper are independently pinned, preventing adjacency-based
expansion.

## Recovered behavior

The object owns the G2 peripheral policy layer:

- product-test indefinite fast advertising versus normal fast advertising for
  30 seconds followed by slow advertising;
- PSN, firmware version `2.2.6.10`, product version, name, and address
  construction for advertising data;
- connection-open, negotiated ATT MTU, security-request, unpair, disconnect,
  advertising-stop, and automatic restart policy;
- application events `0xAD`, `0xB5`, `0xB6`, and `0xB7`;
- command-pipe, command-role, local-role, and left/right-role decisions; and
- DM-event fan-out to connection parameters, OTA, EUS, ESS, EFS, NUS, and ANCC.

The current object is larger than the earlier G2 peripheral sequence. It adds
explicit advertising-event callbacks, retry work, and command/eye-role helpers
around a stable advertising, MTU, security, and handler-init core.

## Third-party boundary and commit shortcut

This closure does not reveal another opaque third-party object. The bodies in
this physical interval are G2-local policy and adapters. Their external provider
seam terminates at Cordio DM/ATT/WSF and the already admitted AmbiqSuite Cordio
application framework. In particular, stock calls the separately closed
legacy advertising APIs such as `AppAdvStop`; it does not duplicate those
provider definitions in `app_ble_peripheral.c`.

The selected provider oracle remains AmbiqSuite 2.5.1 commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`, with Packetcraft r20.05c ancestor
`3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`. Those commits shortcut the
provider API/state-machine side of reconstruction, but cannot identify Even's
private policy revision. The retained path, version/name layout, timers,
application events, and role rules are downstream G2 behavior.

## Reproduction

Run:

```sh
python3 tools/analyze_g2_app_ble_peripheral.py
python3 -m unittest -v tests.test_analyze_g2_app_ble_peripheral
```

The authoritative tables are
`tools/manifests/g2-app-ble-peripheral-function-map.tsv` and
`tools/manifests/g2-app-ble-peripheral-closure.tsv`.
