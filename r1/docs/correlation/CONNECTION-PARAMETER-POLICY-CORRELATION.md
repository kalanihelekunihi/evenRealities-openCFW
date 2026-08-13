# R1 BLE connection-parameter policy correlation

Status: four R1 product functions / 498 bytes byte-pinned; pure policy implemented.

## Outcome

The former frontier leader `0x00051AA0` is the R1 BLE observer for connected (`0x10`),
disconnected (`0x11`), and connection-parameter-update (`0x12`) GAP events. It is not Nordic's
connection-parameter implementation. Nordic SDK structures and GAP operations remain provider
owned; the local implementation is limited to speed classification, per-role state, and retry
planning.

`r1/src/r1_connection_params.c` is a side-effect-free implementation. It accepts typed GAP
parameters and caller-supplied phone/glasses handles, then returns a cancel/retry action. It never
calls the SoftDevice, schedules a timer, logs, or opens BLE.

## Exact closure

`scripts/firmware/summarize_r1_connection_parameter_policy.py` authenticates the recovered
application and pins:

| Function | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `0x0004CB34..<0x0004CB3A` | 6 | `e144876acc5d13f879e211a20a854160bc17ba433c0b67e296f74cd659921186` | glasses connection-handle accessor |
| `0x0004CBA4..<0x0004CBAA` | 6 | `4af57962177981e766a33cad6cdf80f1a7892884aebd51a147f6bf4fdd7af566` | phone connection-handle accessor |
| `0x00051AA0..<0x00051C78` | 472 | `3b73ea67fb15c04cb02fcebeaeff9bcb04b32b574f3798079f74f84512237cbc` | GAP observer and retry policy |
| `0x00072B80..<0x00072B8E` | 14 | `b8482c5ec8f9a3e6f9028fb6ed2712777bce3a192c280b5f9b796a3767b4fe1b` | speed classifier |

All direct branch callsites are frozen. The observer is indirectly registered, while the
classifier has exactly two calls, both inside the observer. The observer literals also pin its
three-byte policy state at `0x200064B2`, requested-speed byte at `0x200064F6`, and delayed callback
Thumb pointer `0x000882AD`.

## Functional contract

- A connection is classified `fast` only when maximum interval is strictly below `50`; `50` is
  slow. The units remain the Nordic GAP provider's standard interval units.
- Connected events are handled only for the peripheral role. The requested speed is initialized
  from the received parameters, while both role-status bytes are initialized fast.
- Exact initial interval pairs `39/39` and `36/36` change an `0xFF` initialization marker to `1`.
  Other pairs do not, and an already-set marker is preserved.
- Disconnect cancels every pending retry for the recovered connection-policy callback.
- On update, an actual speed matching the requested speed updates the glasses status when its
  handle matches; otherwise it updates the phone status when that handle matches.
- A mismatch schedules the requested speed again. Actual slow uses a 4 ms delay; actual fast uses
  2,000 ms. These asymmetric values and the strict threshold are intentional compatibility rules.

Tests cover the `49/50` boundary, peripheral-role gate, both accepted pairs, preservation of an
existing marker, role-specific updates, both mismatch delays, and disconnect cancellation.

## Provider boundary

Nordic SDK 17.1.0 owns BLE event layouts, role lookup, connection-parameter structures, GAP update
requests, and SoftDevice operations. The recovered generic delayed-event loop and logging facade
remain outside this closure. The delayed callback at `0x000882AC` is pinned only as a referenced
boundary here; it is not admitted or recreated until its broader event-routing ownership is closed.

## Reproduction

```sh
python3 scripts/firmware/summarize_r1_connection_parameter_policy.py
make -C openR1 test
make -C openR1 sanitize
make -C openR1 arm-objects
```
