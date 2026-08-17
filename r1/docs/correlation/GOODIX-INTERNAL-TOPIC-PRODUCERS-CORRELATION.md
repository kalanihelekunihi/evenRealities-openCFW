# Goodix internal-topic producer correlation

## Result

The three callback entries in the R1 optical topic initializer that Ghidra retained only as
labels are now explicit bounded C. `raw_hr` was recovered first; this pass adds the sibling `adt`
and wear/living-object producers. All three are product glue around separately owned Goodix and
sensor-stream providers, not biometric algorithms.

The source-built target compiles these functions but does not start optical sampling, invent a
public sender, or infer physical meanings for the unlabeled UInt32 values.

## Pinned image evidence

Stock application load base: `0x00027000`. Rebuilt image SHA-256:
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

The product initializer `0x00089EEC..<0x00089FBE` clears the exact 240-byte backing state, binds
eight callback pointers, and registers the fixed internal topics. Its callback table contains
Thumb pointers to all three entries below even though Ghidra did not promote them to functions.

| Extent | Bytes | SHA-256 | Transparent symbol |
| --- | ---: | --- | --- |
| `0x00089E30..<0x00089E4C` | 28 | `c72f6f01113c2db81a12f28a57e02b3910b9d62c447ea4d144c0d555ad03f12a` | `r1_goodix_adt_append` |
| `0x0008A01C..<0x0008A038` | 28 | `6d8e91f9572f177c80454d8fdad3aecc847c74495e9636859a28825b330de651` | `r1_goodix_raw_hr_append` |
| `0x0008A054..<0x0008A062` | 14 | `646e81e180a4077043c8541c31378b9be0b0a495cf4aafff2dc8c8dd4d39231b` | `r1_goodix_wear_living_object_update` |

## Exact portable contracts

- The 24-byte `adt` record is one UInt8 count, three preserved reserved bytes, and five UInt32LE
  slots. An input appends at `4 + count * 4` and increments only the count byte while count is
  below five. Counts at or above five produce no write.
- The 124-byte `raw_hr` record has the same layout with thirty UInt32LE slots and the same
  saturation rule.
- The two-byte wear record stores the incoming low byte at offset 1 and then writes pending flag
  `1` at offset 0. This byte is the Goodix living-object input to later R1 wear fusion; it is not
  the final fused wear state.
- The backing-state offsets are exact: `raw_hr` at `0x40`, wear at `0xBC`, and `adt` at `0xD8`
  inside the 240-byte state initialized at `0x2001A1BC`.

The C adapters reject NULL records. The stock callbacks assume valid pointers; accepted-input
state and byte order remain exact. Host tests pin reserved-byte preservation, little-endian
encoding, capacity saturation, repeated wear updates, and NULL safety.

## Runtime boundary

These reducers preserve container behavior only. No name or field proves that `raw_hr` values are
a particular PPG channel, that `adt` words have a public unit, or that the living-object byte alone
is a trustworthy wear decision. The Goodix demo callback exposes channel arrays while the stock
`raw_hr` callback receives one already-selected scalar, so physical channel selection remains an
explicit capture/hardware gate.
