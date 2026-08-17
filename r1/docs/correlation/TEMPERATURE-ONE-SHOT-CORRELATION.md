# Temperature one-shot listener correlation

## Outcome

OpenR1 now reconstructs and composes the stock one-shot temperature path from the exact
`"temp"` sensor stream through the five-sample reducer, event 9, and the product-owned daily
temperature cache. The Zephyr listener is retained as an explicit typed start/stop API and is not
started during boot. No BLE command is inferred, and the two physical GXT310 channels remain
unitless/unlabelled rather than being called skin, ambient, core, or clinical temperature.

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Exact recovered evidence

| Extent | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `0x00042514..<0x0004256A` | 86 | `39c338cf4d422187d4c608a8b7fe3e6ac2609d4be0d0054147ab343d3e5e2014` | fixed-length system event `0x1006` boolean control |
| `0x0004B4B0..<0x0004B54A` | 154 | `2d22610c4505c81f9f9989114ac1570c366b32948aa82ac58853c48f04a741b9` | five-sample average, dual scaling, capture, event 9 publish |
| `0x0004B560..<0x0004B594` | 52 | `4df29f0bb268fad32e19e61746fd77ccc94d0726d8e321c0e7b0c552e5e5472a` | every prior accepted value within 300 |
| `0x0004B598..<0x0004B5B0` | 24 | `b97051e2ce6772c8127e0b6efa5fa4a45600a3bc42d81e917e06fc24d2a9c3de` | inclusive `30000...50000` gate |
| `0x0004B6C0..<0x0004B6FE` | 62 | `01529383d9556740deb853204cb9d84bd4d04c68b2cbf462f02bd9a35a509195` | `"once"` listener start/stop |
| `0x0004B920..<0x0004B9F0` | 208 | `9a796f9f908343c06334fa122a9f41771468e57d28d37ccff2573fef5cc8b8bb` | one-shot listener callback |
| `0x0004BBF0..<0x0004BC26` | 54 | `f515e0da5298838c50d396626160eea844f8f9cc30a9d6f9ab4e306603f90f61` | separately gated `"timing"` listener start |
| `0x0004BC40..<0x0004BCD6` | 150 | `8ffdb4962894501a85292a14defa42932f2a3fdea2d2e349168b99d7798c7296` | timing listener callback |
| `0x0008A8FC..<0x0008A928` | 44 | `9b7722026f3f79e3ddfc03fab438f004fd4b51f1aa0cc9a4ba272914ff2f4cf7` | bounded temperature event consumer |

The rebuilt image literals resolve both callback state loads (`0x0004BA40` and `0x0004BCD8`) to
`0x2001E3DC`, the one-shot/timing owner block (`0x0004B700` and `0x0004BC28`) to
`0x2001E3CC`, and the callbacks to Thumb entries `0x0004B921` and `0x0004BC41`.
The registration arguments are therefore exact: stream `"temp"`, listener `"once"` or
`"timing"`, rate 1, mode 1 (per sample).
The four listener start/callback bodies were absent from Ghidra's function CSV and are now exact
manual provenance supplements rather than unowned gaps between neighboring functions.

## State and callback contract

The shared 120-byte state beginning at `0x2001E3DC` has five UInt16 recent samples at `+0x00`,
recent count at `+0x0A`, callback-attempt count at `+0x0B`, one-shot active byte at `+0x0C`,
capture enable at `+0x0E`, capture count at `+0x10`, and 50 UInt16 captured values at `+0x12`.
`gomore_primitives_scaled_sample_state` now preserves these exact offsets and size with compile-time
assertions. Starting a one-shot clears exactly bytes `+0x00...+0x0D`, sets `+0x0C`, and preserves
the independent capture block.

Each callback increments the attempt byte first. Attempt 31 stops without examining the sample.
Attempts 1...30 accept an unsigned first halfword only in `30000...50000`. A valid value must be
within 300 of every currently retained value. A consistency failure clears the recent count and
does not retain the failing value; an out-of-range value leaves the retained sequence unchanged.
Five accepted values complete the measurement. Their integer average is multiplied by the exact
binary64 `0.01` path for UInt16LE event 9 plus six zero bytes and, when capture mode is enabled, by
the exact binary64 `0.1` path for the bounded timing buffer. Both completion and timeout unregister
the listener from `"temp"` during dispatch, exercising the framework's recovered deferred-removal
path.

## Source-built composition and boundary

`gomore_primitives_temperature_measurement_begin` and
`gomore_primitives_temperature_measurement_step` implement the callback state transition over
caller-owned memory. `openr1_sensor_stream_zephyr_temperature_once_set` binds it to the exact
two-byte calibrated GXT310 stream. Completion composes the already reconstructed scaled publisher
with `openr1_databases_zephyr_consume_temperature_event`, which reproduces the exact 250...500
event gate, firmware-time replacement, local-hour lookup, published-minus-250 storage, and hourly
aggregation.

The callable API is retained in `.openr1_platform_api`, but no startup call or public BLE route is
added. The separate sleep/timing activation policy, channel physical labels/units, and owned-ring
thermal validation remain open. This composition adds no executable firmware blob, model archive,
private event injection surface, calibration write, or hardware deployment action.
