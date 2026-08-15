# Goodix GH_NADT peak-mask provider boundary

## Decision

Seven formerly unclassified functions / 1,098 executable bytes formed a closed private helper
chain beneath the already pinned Goodix `GH_NADT_pre` root. Under the subsequent owner-authorized
clean-room reduction, the five formerly gated entries / 918 bytes now compile as transparent C;
the other two helpers were already source-admitted. No function in this historical boundary
remains provider-gated. Its former disposition was
`vendor_source_required_not_redistributable`.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x00030114` | 96 | peak-selection entry adapter; source-admitted |
| `0x0003441C` | 116 | window/descriptor adapter; source-admitted |
| `0x00047FA8` | 112 | selected-index collector; source-admitted |
| `0x00076B78` | 100 | private mask orchestrator; source-admitted |
| `0x00030178` | 494 | extrema-neighborhood bit-mask stage; source-admitted |
| `0x00066AB2` | 124 | mask-row selection helper; source-admitted |
| `0x00029AA0` | 56 | mask-column reduction helper; source-admitted |

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

The SHA-pinned bodies construct and reduce a packed bit mask from floating-point neighborhood
comparisons. The local typed APIs preserve the exact packed-bit order, strict extrema comparisons,
plateau suppression, row scoring, newest-index retention, paired threshold histories, and fixed
`{36,2,1}` / 125-sample / 20-index entry configuration. Stock transient allocations are replaced
by bounded caller-owned scratch; no private symbol name is asserted.

## Provider rule

This historical boundary no longer requires a Goodix binary provider. The admitted implementation
is the owner-authorized reconstruction in `reconstructed/goodix_primitives/`; it links no stock
bytes, absolute firmware pointers, or opaque tables. Other incomplete Goodix processing closures
remain separately gated, so the end-to-end biometric path still fails closed.

The original summarizer remains read-only, consumes only the pinned firmware image, reads no live
sensor data, and emits no algorithm implementation:

```sh
python3 tools/evidence/summarize_r1_goodix_nadt_peak_mask.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
