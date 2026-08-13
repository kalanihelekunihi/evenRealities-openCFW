# Goodix packed-word integrity boundary

## Result

Seven exact functions / 236 executable bytes implement one repeated 24-bit
packed-word integrity convention. Five functions / 162 bytes were previously
unclassified. Direct-call context now places all five behind the proprietary
Goodix GH3X2X provider gate. They are evidence, not clean-room implementation
material, and must not be recreated locally.

This attribution does not rest on byte identity alone:

- `0x000294F8` and `0x0002950C` are called only by the already frozen Goodix
  demo/provider component at `0x0002A1CC` and `0x0002A168`.
- Their shared encoder at `0x000294BC` has no other callers.
- validator copy A at `0x00028E5C` is reached through the GH_NADT processing
  path rooted at `0x0006E788`/`0x0006E838` and through the Goodix-rooted
  algorithm path called from frozen component entry `0x0002C944`.
- encoder copy A at `0x00028E70` has only that validator as a caller.
- the independently known GH_HR validator/encoder pair at `0x000759F4` and
  `0x0005A5EC` provides a third context-confirmed copy of the same convention.

The static census is reproducible with:

```sh
python3 scripts/firmware/summarize_r1_goodix_integrity_boundary.py
```

## Exact function census

| Entry / half-open extent | Bytes | Exact direct callsites | Boundary role |
|---|---:|---|---|
| `0x00028E5C..<0x00028E70` | 20 | `0x00061DD6`, `0x0006C6CE` | packed-word validator copy A |
| `0x00028E70..<0x00028EA6` | 54 | `0x00028E60` | packed-word encoder copy A |
| `0x000294BC..<0x000294F2` | 54 | `0x000294FC`, `0x00029512` | packed-word encoder copy B |
| `0x000294F8..<0x0002950C` | 20 | `0x0002A1E6` | packed-word validator copy B |
| `0x0002950C..<0x0002951A` | 14 | `0x0002A186` | packed-word integrity-bit inserter copy B |
| `0x0005A5EC..<0x0005A622` | 54 | `0x000759F8` | already gated GH_HR encoder |
| `0x000759F4..<0x00075A08` | 20 | `0x0006D53E` | already gated GH_HR validator |

The three 54-byte encoders have exact SHA-256
`f6556685cb2ed54dc42e8ff378ad47ff2fcc02ae4948b261bf5bb58ca4a78572`.
Each reads a separate copy of the same four-word table:

| Table address | Words |
|---|---|
| `0x000BCF18` | `6B851EB7 4147AE13 28F5C28F 15C28F5B` |
| `0x000B0EFC` | `6B851EB7 4147AE13 28F5C28F 15C28F5B` |
| `0x000B149C` | `6B851EB7 4147AE13 28F5C28F 15C28F5B` |

Every table copy has SHA-256
`448ddc2f827f6109a389e73dcc8a34db1ba3b44812f760451944fb015221d936`.

## Recovered behavior

The encoder operates on the low 24 bits of a packed word. Bits 1..2 select one
of four masks. The encoder combines bits 1..23 with that mask, computes
population-count parity, clears bit 0, and inserts the resulting parity bit at
bit 0. Validators recompute the word and compare it with the input. The
inserter updates a packed word in place.

These semantics are recorded so a licensed Goodix integration can be tested at
the adapter boundary. They do not authorize a local substitute for this helper
or any biometric algorithm that uses it.

## Clean-room disposition

All seven entries are `goodix_gh3x2x_candidate` with disposition
`vendor_source_required_not_redistributable`. No private Goodix symbol name is
claimed. openR1 may implement only the separately bounded R1 power, transport,
lifecycle, profile, and command adapters; the integrity convention and the
algorithms that consume it remain supplied by a lawfully obtained, compatible
Goodix provider.
