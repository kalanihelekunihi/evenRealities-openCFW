# G2 BLE discovery-policy recovery

## Result

`platform\ble\app_ble_discovery.c` is closed as a two-function, 3,724-byte
G2-local policy object layered on the admitted AmbiqSuite Cordio application
framework. It is not third-party code. `APP_StartServiceDiscovery` contributes
214 code bytes and `APP_BleServerDiscCback` contributes 2,748, for 2,962 body
bytes plus 762 bytes of literal pools and alignment.

Both exact names occur in retained function strings and are corroborated by
the earlier G2 firmware analysis, where the same two functions have the same
214/2,748-byte sizes. The current image is independently byte-pinned. Three
stored Thumb pointers root the callbacks at `0x004B821C`, `0x004B8748`, and
the start helper's own literal pool; there is no direct BL ingress and no
strict-interior ingress. The object makes 179 direct provider calls.

The start helper cancels delayed discovery work, resets application discovery
state, invokes Cordio discovery setup, and posts the product message `0xA5`.
The callback implements states 0 through 8 and branches by connection role. It
coordinates database-hash reading, security, GATT and Ring discovery, optional
ANCS discovery, configuration, handle reporting, and completion/failure
policy. Cordio supplies the generic discovery primitives; the ordering,
role/phone rules, retry state, logging, and product callbacks are G2-local.

This source-family split is now usable as an OpenCFW shortcut: reuse the
admitted AmbiqSuite/Packetcraft discovery APIs, but reconstruct this state
machine as product code. Production routing remains deferred with the wider
central/peripheral BLE state machines and target validation.

Reproduce with:

```sh
python3 tools/analyze_g2_app_ble_discovery.py
python3 -m unittest -v tests.test_analyze_g2_app_ble_discovery
```
