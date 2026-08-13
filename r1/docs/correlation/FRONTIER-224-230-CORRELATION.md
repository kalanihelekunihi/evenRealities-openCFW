# 224...230-byte frontier correlation

The six largest unresolved application functions after the 230...248-byte closure are now
source-routed from immutable body hashes, complete instruction extents, direct-call scans,
function-pointer references, Nordic SDK source, and the recovered firmware-security audit.

| Recovered function | Bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00049838..<0x0004991E` | 230 | `fa53e4fba782075d0566bf47659cdb6b6968c0e1ec6a703a123a75613c8223cd` | R1 heart-rate mode transition |
| `0x00036C7C..<0x00036D60` | 228 | `9a93470b26a6b71044994554398155f661cf05e24cc969e641d3d9330267d1ce` | blocked shared quantized-neural runtime |
| `0x00065D64..<0x00065E48` | 228 | `75633aa478660597d6d07d0d344b854aabfc4bc9073b27531d2a0055e3f6d29c` | R1 delayed-event cancellation |
| `0x00094C74..<0x00094D56` | 226 | `1c94d828ab675943b6e946655e8692329c49d0225cf7ed5236f89c8276a1ca1d` | R1 ring-stability decision |
| `0x000309DC..<0x00030ABC` | 224 | `2d2b8f7f9339240a2e01c58ae1beddcddb69619d29a48d4b043823cfea9c84af` | Nordic SDK `nrfx_pdm_irq_handler` |
| `0x0004D2F4..<0x0004D3D4` | 224 | `d9fa60a25d56e12c8f24f697a3968c09372cd391844b5c3aba07e9ab22ad6c0c` | R1 gate around Nordic PHY update |

These six functions total 1,360 bytes. The 22-byte mode setter at `0x000499C4` and 76-byte
rolling-window feeder at `0x00094A60` close two supporting R1 helpers, producing an eight-function
/ 1,458-byte closure.

## R1 event and health policy

`0x00065D64` scans all 64 delayed-event slots and clears every event whose callback matches the
request and whose context matches when the requested context is nonzero. A zero context is a
wildcard. When at least one slot is removed, it samples the 1,024-Hz CMSIS tick, wakes the worker,
and calls the already closed timer step with the `0xFFxxxxxx` elapsed override. The clean-room
`r1_delayed_event_cancel` returns the removal count, elapsed time, wakeup request, due events, and
timer action. It performs no mutex, thread, timer, logging, or live queue operation.

`0x00049838` stops the previous mode's sensor-stream subscription when present. Leaving mode `1`
also stops its mode timer, any active heart-rate measurement timer, the active HRV timer, and
clears the HRV timing state. Entering mode `1` creates a timer with period 600 when one does not
already exist. The 22-byte setter accepts only modes `0...3`. `r1_heart_rate_mode_plan_transition`
models those product decisions while the unidentified sensor-stream framework and Goodix/GoMore
biometric providers remain external.

`0x00094A60` maintains an eight-float rolling window. After eight observations, `0x00094C74`
increments a UInt16 counter when the recovered nonnegative motion-deviation value is no greater
than the exact float32 bit pattern `0x3D4CCCCD` (approximately `0.05`). State becomes detected at
counter 600. A value above that threshold clears both counter and state. The stock code compares
the raw signed float bits and contains a nominal `0x3E051EB8` (`0.13`) decrement branch that is
unreachable for the nonnegative input domain after the preceding comparison; the clean model
retains the exact raw-bit branch behavior. `r1_ring_stability_observe` reports evaluation, state
change, callback request, counter, and state without acquiring motion samples or implementing a
sensor provider.

## Nordic provider reuse

`0x000309DC` is the Nordic nrfx PDM interrupt handler, reached through Thumb vector pointer
`0x000309DD` stored at `0x000270B4`. STARTED and STOPPED event checks, double-buffer release,
overflow reporting, active-buffer selection, and deferred buffer-request behavior match
`modules/nrfx/drivers/src/nrfx_pdm.c::nrfx_pdm_irq_handler` in nRF5 SDK 17.1.0. The pinned source
file has SHA-256 `770b05a7f0abf5d12cab42c5ee1e30791918c804c5e2e438061239020cf339fb`.
OpenR1 must compile that Nordic source when a validated PDM board use requires it; it does not
recreate the driver locally or enable an otherwise unprovisioned peripheral.

`0x0004D2F4` rejects the invalid handle and every link whose Nordic
`ble_conn_state_status` is not connected, then passes the requested transmit/receive PHY bytes to
`sd_ble_gap_phy_update`. `r1_connection_phy_update_plan` owns only this R1 gate. The Nordic SDK
adapter `openr1_bae8_request_phy_update` calls the SDK's connection-state module and S140 API
directly, so no SoftDevice implementation is copied.

## Shared runtime boundary

`0x00036C7C` is installed by Thumb pointer `0x00036C7D` at `0x00074CD8`. It combines two signed
int8 tensors with float scales and zero points, requantizes each element, saturates to signed
seven-bit magnitude, and publishes output range metadata. The surrounding descriptor constructors
are shared by separately gated GoMore and Goodix graphs. No attributable source, version, or
license is identified, so this fifth shared-runtime function remains
`investigate_before_implementing`; no generic neural-library substitute is admitted.

## Reproducible unsigned image

The new clean-room policies and Nordic adapter are retained in the linked application at
`0x000360F0`, `0x00036570`, `0x0003685C`, `0x00038228`, and `0x0003926A`. The verified unsigned
application contains 94,804 bytes of text, 236 bytes of data, and 132,544 bytes of BSS. Its
95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`; the standalone HEX has
SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_224_230.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

Code signing, deployment authorization, keys, live identity extraction, provider substitution,
security-enforcement bypasses, and device programming remain outside this closure.
