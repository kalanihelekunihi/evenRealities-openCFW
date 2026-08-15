# Goodix packed-channel decoder source boundary

## Decision

The complete two-function / 856-byte closure is owner-authorized transparent C. The 334-byte
record assembler maps to `goodix_primitives_spo2_channel_records_assemble`; the formerly private
522-byte scaling helper now maps to `goodix_primitives_spo2_channel_scale_decode`. Both carry
`clean_room_reimplementation_owner_authorized`; no opaque firmware byte, absolute RAM table, or
hidden math callback is linked into the reconstructed bundle.

## Exact closure

| Entry | Bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x000335B4` | 522 | `f9972cff9f72e10bd9b1bfb21ebaaa92763a058f8f857ef46bd5f1b7c61e0e3f` | source-admitted typed channel scaling |
| `0x00061DA4` | 334 | `39fff2899dacfbad91bcff003cedfdac2ce2d9f0fbdd26f7f01db54927a98bfe` | source-admitted decoder/assembler |

The decoder's sole direct callsite is `0x0006E874` in the SHA-pinned GH_NADT processing root.
Its three scaling calls are exactly `0x00061E42`, `0x00061E86`, and `0x00061ECA`; the scaling
body has no outside caller. The `0x00066890` call leaves the stock integrity prepass enabled.

## Recovered contract

The assembler scans `3 * channel_count` presence bytes, replaces integrity failures with exact
`0x00800000`, reads the three channel-group masks MSB first, copies the sequence/header metadata,
assembles fixed 24-byte records, advances the wrapped UInt8 record count only on group two, and
reports expected-count mismatch.

The scaling callback has two stock encoding modes. Direct mode converts the selected signed Int32,
then divides in Float32 by exact `1000.0f` and the parallel UInt16 divisor. Packed mode applies the
recovered bit-width mask and the `max(width - 17, 0)` right shift, reads the signed Int16 divisor
and one of three explicitly bound scale-code tables, and evaluates one of two formulas in the
stock operation order:

- mode zero uses Float32 `value * 2 * 800 * 1000`, then binary64 division by `pow(2,17)`,
  multiplication by `pow(10,3)`, and division by the table scale and divisor;
- modes one and two use binary64 `value * 1.8 / pow(2,17) / scale / divisor * pow(10,9)`.

Exact stock literals are `1000.0f`, `800.0f`, binary64 `1.8`, bases/exponents `{10,3}`, `{10,9}`,
and `{2,17}`. The stock absolute table root `0x20007D68` and its `-0x58` / `-0x24` bank offsets
become three bounded table spans. `pow` is an explicit typed provider. Zero table/divisor entries
produce zero scale, unsupported encodings preserve the destination, and malformed spans are
rejected before mutation.

Focused tests pin direct decoding, unsigned direct divisors, the packed mask/shift rule, all three
table modes, exact power-provider call order, zero and unsupported-mode fallbacks, record mask
order, five-call destination layout, integrity replacement, metadata, capacity truncation,
mismatch/count wrapping, sequence wrapping, and validation before mutation. The source emits no private coefficients;
deployments supply transparent typed table values and the source-routed
toolchain math binding.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_goodix_channel_decoder.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
