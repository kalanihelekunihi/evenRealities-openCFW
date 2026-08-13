# Goodix GH_NADT channel-quality provider boundary

## Decision

The formerly unclassified function at `0x00088E80` / 518 executable bytes is routed to
`goodix_gh3x2x_candidate` with disposition `vendor_source_required_not_redistributable`. It is a
private GH_NADT channel-quality/derived-score stage, not R1 product behavior, and is not eligible
for local reconstruction.

## Exact evidence

| Entry | Bytes | SHA-256 | Direct callsites |
| --- | ---: | --- | ---: |
| `0x00088E80` | 518 | `9c4e682f8fe366f1b1f3c68743331392e9c8c80466e6463653bbf363bf3e825f` | 1 |

The sole callsite is `0x0006E916` inside already SHA-pinned GH_NADT processing root
`0x0006E838`. That root is tied to embedded provider identity
`GH_NADT_pre v1.0.2.0 / 548d894d`, and there is no outside direct caller. The direct caller-set
digest is `21a9202e4352d08144ee2a1e8a2bf7e63d6776a408fda69b0a98923af823fb52`.

The body derives per-channel flag bits from private thresholds and record fields, then applies
floating-point transforms to update a bounded score byte. This behavioral description is only
enough to place the code behind the Goodix provider boundary; it does not authorize copying its
thresholds, constants, formulas, or inferred implementation.

## Provider rule

Use a lawfully obtained Goodix GH3X2X package with recorded version, hashes, ABI, license, and
redistribution terms. Until then, do not recreate this quality/scoring stage, do not emit its
private thresholds, and keep the live optical-processing path disabled. Toolchain math remains a
separately source-routed dependency.

The summarizer is static, reads no live sensor data, and emits no private thresholds or algorithm
implementation.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_goodix_nadt_quality.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
