# Goodix GH_NADT peak-mask provider boundary

## Decision

Seven formerly unclassified functions / 1,098 executable bytes form a closed private helper chain
beneath the already pinned Goodix `GH_NADT_pre` root. They are routed to
`goodix_gh3x2x_candidate` with disposition `vendor_source_required_not_redistributable`; OpenR1
must obtain this behavior from a lawfully licensed Goodix GH3X2X provider and must not reproduce
the recovered extrema/peak-selection algorithm locally.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x00030114` | 96 | peak-selection entry adapter |
| `0x0003441C` | 116 | window/descriptor adapter |
| `0x00047FA8` | 112 | selected-index collector |
| `0x00076B78` | 100 | private mask orchestrator |
| `0x00030178` | 494 | extrema-neighborhood bit-mask stage |
| `0x00066AB2` | 124 | mask-row selection helper |
| `0x00029AA0` | 56 | mask-column reduction helper |

## Closed call graph

The only entry from outside this closure is callsite `0x0006E8E6` in the already provider-gated
GH_NADT preprocessing root at `0x0006E838`, tied to embedded identity
`GH_NADT_pre v1.0.2.0 / 548d894d`. The exact route is:

```text
0x0006E838 -> 0x00030114 -> 0x0003441C -> 0x00047FA8 -> 0x00076B78
                                                               |-> 0x00030178
                                                               |-> 0x00066AB2
                                                               `-> 0x00029AA0
```

`0x0003441C` invokes the collector twice, but no function in the seven-entry closure has a direct
caller outside this route. The static summarizer pins every body SHA-256 and every direct callsite,
including the maximum five-helper depth from the existing provider root.

The bodies construct and reduce a packed bit mask from floating-point neighborhood comparisons.
That description is solely for ownership placement. It is not a clean-room specification and does
not expose or authorize reconstruction of Goodix thresholds, formulas, or private symbols.

## Provider rule

Use a matching Goodix GH3X2X SDK whose version, binary/source hashes, target ABI, license, and
redistribution terms are recorded in the provider manifest. Until that package is authenticated,
keep this optical-processing path disabled. Product-owned sensor transport and lifecycle adapters
may remain local, but this algorithm closure may not.

The summarizer is read-only, consumes only the pinned firmware image, reads no live sensor data,
and emits no algorithm implementation:

```sh
python3 scripts/firmware/summarize_r1_goodix_nadt_peak_mask.py
python3 scripts/firmware/build_r1_source_ownership.py --check
python3 scripts/firmware/verify_openr1.py
```
