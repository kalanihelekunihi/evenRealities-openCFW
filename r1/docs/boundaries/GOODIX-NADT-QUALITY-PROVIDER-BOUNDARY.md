# Goodix GH_NADT channel-quality provider boundary

## Decision

The formerly unclassified function at `0x00088E80` / 518 executable bytes is attributed to
`goodix_gh3x2x_candidate`. Under the later owner-authorized reduction it is now routed to
`clean_room_reimplementation_owner_authorized` as
`goodix_primitives_nadt_channel_quality_update`.

## Exact evidence

| Entry | Bytes | SHA-256 | Direct callsites |
| --- | ---: | --- | ---: |
| `0x00088E80` | 518 | `9c4e682f8fe366f1b1f3c68743331392e9c8c80466e6463653bbf363bf3e825f` | 1 |

The sole callsite is `0x0006E916` inside already SHA-pinned GH_NADT processing root
`0x0006E838`. That root is tied to embedded provider identity
`GH_NADT_pre v1.0.2.0 / 548d894d`, and there is no outside direct caller. The direct caller-set
digest is `21a9202e4352d08144ee2a1e8a2bf7e63d6776a408fda69b0a98923af823fb52`.

The body updates the first 44-byte logical channel record. Its six diagnostic bits cover two
summary thresholds, activity, validity, metric limits/sentinels, and signed quality; the caller
mask is applied last. Three uses of the already-local scaled logistic helper produce reciprocal
secondary/primary metric scores and a signed-quality score, combined with exact Float64 weights
0.4, 0.4, and 0.2 before truncation to the capped 0..100 byte.

## Provider rule

The local implementation accepts typed configuration, summary, and record fields and an explicit
exponential provider. It contains no absolute state address, hidden callback, or opaque firmware
data. Live optical-processing adoption and hardware validation remain separate from source
admission; toolchain math remains a separately source-routed dependency.

The summarizer is static, reads no live sensor data, and emits no private thresholds or algorithm
implementation.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_goodix_nadt_quality.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
