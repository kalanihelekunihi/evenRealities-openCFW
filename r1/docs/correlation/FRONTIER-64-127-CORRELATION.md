# 64...127-byte frontier correlation

The 64...127-byte inventory tier is now source-routed: 150 functions, 13,652 declared body
bytes (13,344 range-pinned; 308 remote continuation bytes recorded as omitted). Three
functions in the tier stayed unclassified for lack of function-local evidence:
`0x00034B08` (callerless vtable-`0xA6`/`0xAE` transaction), `0x0007260C` (callerless two-word
record store), and `0x0003E6B0` (callerless heap destructor with unresolvable owner).

Current reduction note: `0x00034B08` and `0x0003E6B0` are now source-admitted
under the later owner-authorized policy. The former is a typed
command/status/clock poller; raw Thumb-2 proves that the latter releases its
`+0x260` owner before tail-entering the missed destructor boundary at
`0x00029354`. Their original attribution uncertainty remains recorded above.
The Goodix candidate `0x00032788` is also source-admitted as
`goodix_primitives_nadt_default_initialize`; it transparently builds the exact
default configuration and process-version contract before entering the now
reconstructed context initializer.

| Family | Functions |
| --- | ---: |
| R1 product-specific | 96 |
| GoMore licensed-provider candidate | 28 |
| Goodix GH3X2X candidate | 11 |
| Sensor-stream framework candidate | 6 |
| Shared quantized-neural runtime candidate | 3 |
| YHM2710 candidate | 2 |
| Generic device-registry candidate | 2 |
| Nordic nRF5 SDK 17.1.0 | 1 |
| Arm toolchain runtime | 1 |

## Exact upstream closures

`0x00087ED0` (102 bytes) is `components/ble/peer_manager/peer_database.c::reattempt_previous_operations`
from the pinned SDK: statement-level match on the `m_pending_store` flag, the four-record
write-buffer scan at stride `0x0C` with the `store_busy`/`store_flash_full` flag byte at +10,
and the `write_buf_store_in_event` retry call.

`0x00090E8C` is the toolchain `sqrt` wrapper: the binary64 sqrt core plus the `0x7FF00000`
exponent-mask domain check raising EDOM through the runtime errno path. The stock image links a
second statically-compiled copy inside the provider region; the clean-room build links the
selected toolchain runtime instead.

## R1 product anchors

Product assignments rest on literal-resolved diagnostics and scatter-decoded board tables:
`[RING]`/`[thread_manager]`/`[ep]` format strings, the product version strings `2.2.6.0009` and
`603MV1.9.3`, and the named-GPIO records `acc_int_1`, `ppg_int`, `touch_rdy_in`,
`mcu_reset_irq`, `pmic_irq`, `nfc_gpo_irq`, `device_stacmd_irq` plus the rail outputs
`ppg_led_en`, `touch_ldo_en`, `ppg_reset_en`, `ship_mode_en`, and `touch_rdy_out` with their
recovered pin numbers.

## Boundaries and reservations

All provider-candidate and unresolved-framework entries carry the
`investigate_before_implementing` or `vendor_source_required_not_redistributable` disposition and
stay implementation-blocked.
GoMore and Goodix candidates follow exclusive gated call topology; the shared
quantized-neural runtime candidates (`0x00091E6C`, `0x00091DBE`, `0x00074BE0`) rest on
structural identity with the byte-pinned descriptor/arena machinery, with `0x00074BE0`
additionally showing the mixed gated-caller signature. No provider internals are recreated.
`0x0005128C` (board-power and two-byte identity read) is R1 product glue whose touch-controller
identity is inferred from rail helpers shared with the pinned IQS7211E board-open path; the
identity remains unproven and the surface stays gated.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_64_127.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
