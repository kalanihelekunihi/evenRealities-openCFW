# Goodix GH_HR processing provider boundary

## Decision

31 formerly unclassified functions / 7,144 executable bytes are now routed to the existing Goodix
GH_HR provider gate. The largest is `0x00032808` / 2,814 bytes. Its sole direct caller is the
already byte-pinned GH_HR algorithm core at `0x0006D51C`, through callsite `0x0006D5FA`.

The frozen direct-call graph reaches all 31 entries from that provider core in at most four levels.
Every direct caller of every newly routed entry is either already Goodix-gated or another member of
this same closed set; there are zero outside direct callers. This proves a linked-component
ownership boundary without inventing private Goodix symbol names.

All entries remain attributed to `goodix_gh3x2x_candidate`. The sample-variance,
sample-standard-deviation, conditional descriptor wrapper leaves, and complete extrema tracker are owner-authorized local C;
the remaining detector, filter, feature-extractor, and decision bodies retain disposition
`vendor_source_required_not_redistributable`. OpenR1 must bind a lawfully obtained, authenticated
Goodix provider matching the recovered ABI and exact
`GH_HR_exc_pv_v2.0.3.0_CONF_nc_21d2063d_002271a1` identity.

The adjacent 406-byte primary/private-context constructor at `0x0006D204` has
since left this gate. `goodix_primitives_hr_primary_context_create` makes its
two stock global owners, four HRNet table addresses, and selectors 0/1/6 of
the copied constructor vector explicit typed bindings. It preserves the exact
configuration defaults and tail literals and has a paired, failure-clean
31-allocation teardown; the graph implementations bound through that API keep
their own independent ownership dispositions.

The 956-byte compiler-scattered body at `0x00034CBC`, SHA-256
`41bf9766adb1e05d96397c6e20463f9f7b51fc184319261670451cc4fa50dce0`, now compiles as
`goodix_primitives_hr_extrema_tracker_update`. Its 48-byte tracker record exposes direction state,
trough/peak positions and values, pair readiness, rise/fall amplitudes and spans, completion flag,
and sample index. The local entry preserves full-buffer gating, period-boundary compensation,
the exact `0/1/2` direction latch, and mode-one four-sample cardinal-spline refinement. The stock
82-float stack area is a bounded caller-owned 41-point workspace; its two four-word coordinate
tables are explicit curve bindings.

## Exact census

| Entry | Bytes | Ownership label |
| --- | ---: | --- |
| `0x00029090` | 40 | GH_HR closed-callgraph helper |
| `0x00029656` | 22 | GH_HR conditional buffer-mean wrapper; source-admitted |
| `0x000299EC` | 176 | six-float interval/state merge; source-admitted |
| `0x0002D458` | 4 | GH_HR closed-callgraph helper |
| `0x0002F224` | 56 | GH_HR sample variance; source-admitted |
| `0x0002F260` | 74 | GH_HR counted UInt32 history; source-admitted |
| `0x00030090` | 128 | GH_HR capped running triplet; source-admitted |
| `0x00030368` | 286 | five-history GH_HR mean/center/weighted-feature pipeline with local periodic resampling and explicit coefficient providers; source-admitted |
| `0x00030E1C` | 72 | wrapping-age/strict-gate triplet snapshot copier; source-admitted |
| `0x00032808` | 2,814 | GH_HR feature/event decision core |
| `0x00034490` | 106 | grouped row-wise weighted-sum kernel; source-admitted |
| `0x00034A58` | 14 | GH_HR sample standard deviation; source-admitted |
| `0x00034A66` | 22 | GH_HR closed-callgraph helper |
| `0x00034CBC` | 956 | full-buffer trough/peak tracker with typed state and optional caller-workspace spline refinement; source-admitted |
| `0x00035084` | 84 | Float32 round-to-nearest with exact halves away from zero; source-admitted |
| `0x00036EFC` | 118 | strided descending top-selection helper; source-admitted |
| `0x0003738C` | 22 | GH_HR conditional standard-deviation wrapper; source-admitted |
| `0x00037588` | 372 | 25-phase mean/interpolation resampler with caller-owned state; source-admitted |
| `0x00037710` | 16 | float-buffer full predicate; source-admitted |
| `0x00037720` | 24 | bounded float-buffer accessor; source-admitted |
| `0x0003773C` | 150 | evenly spaced cardinal-spline sampler; source-admitted |
| `0x00037DEC` | 158 | baseline-qualified event-pair rebalancer; source-admitted |
| `0x00038030` | 28 | GH_HR closed-callgraph helper |
| `0x0003DE20` | 234 | GH_HR median-absolute-deviation inlier mask; source-admitted |
| `0x00048018` | 392 | four-point cardinal-spline evaluator; source-admitted |
| `0x0004FDB8` | 64 | GH_HR fixed-32-byte record-history helper; source-admitted |
| `0x000567C4` | 94 | GH_HR closed-callgraph helper |
| `0x00056828` | 20 | GH_HR closed-callgraph helper |
| `0x00070B60` | 178 | clamped-deviation mean-outlier counter; source-admitted |
| `0x00086BAC` | 394 | newest-first four-candidate position-band selector with clamps, tags, fallback, and positive compaction; source-admitted |
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
python3 tools/evidence/summarize_r1_goodix_hr_boundary.py
```

The census deliberately excludes attributable compiler/runtime functions, the separately gated
sensor-algorithm heap, and any non-reachable neighboring math body. It emits no algorithm source,
uses no sensor, and does not authorize local provider reimplementation.
