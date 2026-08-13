# Goodix GH_HR processing provider boundary

## Decision

31 formerly unclassified functions / 7,144 executable bytes are now routed to the existing Goodix
GH_HR provider gate. The largest is `0x00032808` / 2,814 bytes. Its sole direct caller is the
already byte-pinned GH_HR algorithm core at `0x0006D51C`, through callsite `0x0006D5FA`.

The frozen direct-call graph reaches all 31 entries from that provider core in at most four levels.
Every direct caller of every newly routed entry is either already Goodix-gated or another member of
this same closed set; there are zero outside direct callers. This proves a linked-component
ownership boundary without inventing private Goodix symbol names.

All entries are `goodix_gh3x2x_candidate` with disposition
`vendor_source_required_not_redistributable`. No heart-rate detector, filter, feature extractor,
or decision algorithm is admitted for local reconstruction. OpenR1 must bind a lawfully obtained,
authenticated Goodix provider matching the recovered ABI and exact
`GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1` identity.

## Exact census

| Entry | Bytes | Ownership label |
| --- | ---: | --- |
| `0x00029090` | 40 | GH_HR closed-callgraph helper |
| `0x00029656` | 22 | GH_HR closed-callgraph helper |
| `0x000299EC` | 176 | GH_HR closed-callgraph helper |
| `0x0002D458` | 4 | GH_HR closed-callgraph helper |
| `0x0002F224` | 56 | GH_HR closed-callgraph helper |
| `0x0002F260` | 74 | GH_HR closed-callgraph helper |
| `0x00030090` | 128 | GH_HR closed-callgraph helper |
| `0x00030368` | 286 | GH_HR closed-callgraph helper |
| `0x00030E1C` | 72 | GH_HR closed-callgraph helper |
| `0x00032808` | 2,814 | GH_HR feature/event decision core |
| `0x00034490` | 106 | GH_HR closed-callgraph helper |
| `0x00034A58` | 14 | GH_HR closed-callgraph helper |
| `0x00034A66` | 22 | GH_HR closed-callgraph helper |
| `0x00034CBC` | 956 | GH_HR closed-callgraph helper |
| `0x00035084` | 84 | GH_HR closed-callgraph helper |
| `0x00036EFC` | 118 | GH_HR closed-callgraph helper |
| `0x0003738C` | 22 | GH_HR closed-callgraph helper |
| `0x00037588` | 372 | GH_HR closed-callgraph helper |
| `0x00037710` | 16 | GH_HR closed-callgraph helper |
| `0x00037720` | 24 | GH_HR closed-callgraph helper |
| `0x0003773C` | 150 | GH_HR closed-callgraph helper |
| `0x00037DEC` | 158 | GH_HR closed-callgraph helper |
| `0x00038030` | 28 | GH_HR closed-callgraph helper |
| `0x0003DE20` | 234 | GH_HR closed-callgraph helper |
| `0x00048018` | 392 | GH_HR closed-callgraph helper |
| `0x0004FDB8` | 64 | GH_HR closed-callgraph helper |
| `0x000567C4` | 94 | GH_HR closed-callgraph helper |
| `0x00056828` | 20 | GH_HR closed-callgraph helper |
| `0x00070B60` | 178 | GH_HR closed-callgraph helper |
| `0x00086BAC` | 394 | GH_HR closed-callgraph helper |
| `0x00087A78` | 26 | GH_HR closed-callgraph helper |

`0x00032808` is a compiler-scattered body. Its 2,814 executable bytes are exactly:

- `0x00032808..<0x00032C10`
- `0x00032C1C..<0x00033020`
- `0x0003303C..<0x000331F4`
- `0x000331F6..<0x00033330`

`0x00034CBC` likewise excludes the two-byte gap between `0x0003505A` and `0x0003505C`.
The verifier concatenates only the recorded executable segments and does not absorb intervening
literal/data islands.

## Reproducible evidence

The static summarizer verifies the supplied application-image hash, the exact size and SHA-256 of
every function, every executable segment, and all direct callsites:

```sh
python3 scripts/firmware/summarize_r1_goodix_hr_boundary.py
```

The census deliberately excludes attributable compiler/runtime functions, the separately gated
sensor-algorithm heap, and any non-reachable neighboring math body. It emits no algorithm source,
uses no sensor, and does not authorize local provider reimplementation.
