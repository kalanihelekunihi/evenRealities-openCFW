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

The clean-room two-function implementation is production-routed for both the
reviewed Apple Clang and Linux Clang profiles. Its 516 compiled text bytes and
23 strict relocations replace all 2,962 bounded stock body bytes; the 762-byte
stock literal-pool/alignment remainder stays classified and retained. Host
tests cover all nine states, both connection roles, allocation and missing
record failures, database-hash/GATT/Ring/ANCS ordering, configuration, handle
reporting, and completion/failure behavior. Exact route, component, manifest,
and package checks are fail closed.

No physical G2, phone peer, Ring peer, radio capture, or authorization was
available in this environment. Live validation is therefore explicitly
blocked by unavailable physical evidence. Required evidence is an authorized
paired-phone and Ring trace proving role-aware discovery/configuration/failure/
completion ordering plus a disconnect/reconnect trace proving attempt state
and handles do not survive incorrectly. No hardware operation was performed.

Reproduce with:

```sh
python3 tools/analyze_g2_app_ble_discovery.py
python3 -m unittest -v tests.test_analyze_g2_app_ble_discovery \
  tests.test_runtime_app_ble_discovery
```
