# Final Ghidra explicit-entry closure

## Result

The final six application addresses named explicitly by the existing Ghidra
analysis scripts are now exact manual provenance supplements. They are six
real, contiguous Thumb functions—not data labels, instruction interiors, or
secondary segments—and total 666 executable bytes. The explicit-entry census
therefore has no remaining `within_noncontiguous_bounding_range_unproven`
rows.

| Exact extent | Bytes | SHA-256 | Transparent/source-provider mapping |
| --- | ---: | --- | --- |
| `0x000547F4..<0x00054860` | 108 | `cd6408a273e5cd3fc6a0e8b89bee18e583e64548c8718c24691bb6331f509937` | `r1_analog_close_plan_build` around Nordic SAADC |
| `0x00054B90..<0x00054C16` | 134 | `e38d6ca71816028adae320230a15921f7b1ee9a72fc2a193c04a7e54dffeca90` | `r1_gpio_input_open_plan_build` around Nordic GPIO/GPIOTE |
| `0x0006F600..<0x0006F638` | 56 | `f8e7e7060dc42cc772ec9e0c75bb0cd0210f4160c792f73398df0557e24dc87e` | `gxt310_read_temperature_milliunits` |
| `0x0006F648..<0x0006F6B2` | 106 | `c2dd528f1696a7dec0fff2859d0940930d8f75de84d7d582a962e4fc9f9190fa` | `gxt310_switch_mode` |
| `0x0006F738..<0x0006F794` | 92 | `996e62bb9f1dfdb48ae224674b0771b1e6783d32fe4d8c81a003a1b21824e7b1` | `gxt310_trigger_one_shot` |
| `0x00075290..<0x0007533A` | 170 | `f7255c4ceb866f64a4489c915448ac6c4f1f02ffc4fdf7f1be5022648f1d0482` | R1 LIS2DW12 double-tap configuration over official ST source |

## Recovered contracts

The analog close body scans three 40-byte records. A named open record causes
its recovered nrfx channel selector (`6`, `4`, or `3`) to be uninitialized and
its open byte cleared. The shared SAADC driver is uninitialized only when no
other record remains open and the driver-active byte is set. Unknown names
return provider status 1; already-closed records return success without an
effect. The local representation is a pure direct-typed plan, so the generic
stock registry and Nordic driver body are not recreated.

The GPIO input-open body scans seven 44-byte records with the exact production
names and pin topology. Unknown names return status 2 and an already-open
record returns success without reconfiguration. A first open plans raw pin
configuration 2, on-demand GPIOTE initialization, low-accuracy PORT-event
configuration from the record's pull/polarity bytes, event enable, and the
open-byte update. Its installed Thumb pointer is `0x00054B91` at decompressed
runtime address `0x200071FC`; the IRQ callback remains the separately pinned
`r1_gpio_input_irq_dispatch`.

The GXT310 shared read obtains two bytes, interprets them as signed big-endian
Int16, and applies the exact `(1/128) * 1000` scale with truncation toward zero.
The two write bodies are the already-tested `00 C2`/`01 C2` mode command and
`01 C1` one-shot command. Their six branch-only channel veneers at
`0x0006F804...0x0006F834` prove both recovered addresses (`0x90`, `0x94`) use
the shared bodies.

The LIS2DW12 adapter enables X/Y/Z tap detection, sets all three thresholds to
3, sets duration/quiet/shock to zero, selects tap mode 1, reads INT1 routing,
ORs mask `0x08`, writes routing back, and returns 1. The local pure plan owns
only those R1 values; all twelve register operations remain official ST
LIS2DW12 v2.1.0 provider calls. Its Thumb pointer is pinned at `0x0009A740`.

## Boundary and verification

No function in this closure performs host GPIO, ADC, sensor-bus, or interrupt
operations. Nordic and ST implementations remain pinned source providers; the
GXT310 behavior is independent owner-authorized C. There is no firmware blob,
binary library, copied object, or opaque callback.

Reproduce the exact extents, hashes, direct branches, decompressed operation
table pointers, and policy metadata with:

```sh
python3 tools/evidence/summarize_r1_remaining_explicit_entries.py
```
