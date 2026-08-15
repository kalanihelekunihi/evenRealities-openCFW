# Goodix GH_NADT provider boundary

## Decision

58 functions / 19,274 executable bytes form a byte-pinned Goodix GH_NADT
provider boundary. 57 functions / 19,148 bytes were newly routed out of the unclassified
frontier; `0x0006E788` was already gated as the exact GH_NADT version builder and is retained here
as the identity anchor.

Every function in this census remains classified as `goodix_gh3x2x_candidate`. The result binding,
zero-safe sample variance, its standard-deviation wrapper, the bounded
`0x0003497C` peak-quality update, and the `0x00031624` / `0x00035F70`
Int16/Int32 autocorrelation pair, the `0x00066900` multiscale maximum mask,
its `0x00036734` peak-index caller, and the `0x00092A04` / `0x000666A4`
centered-correlation/normalized-autocorrelation pair, plus the complete `0x00029144`
dual-window feature/correlation extractor, `0x00037B80` auxiliary state classifier, and
`0x0007DD58` alternate-state classifier are owner-authorized local C; the preprocessing root is also owner-authorized local C
with typed stage bindings and caller-owned scratch. The remaining liveness, signal-processing,
and classifier implementations retain disposition
`vendor_source_required_not_redistributable`. A matching lawfully obtained Goodix provider is
required for those remaining bodies.

## Identity and callgraph evidence

The application stores the exact marker fragments `GH_NADT_pre`, `v1.0.2.0`, and `548d894d` at
`0x0006E808`. The version builder at `0x0006E788` composes those fragments. The recovered streaming
path invokes the NADT processing chain every 25 samples.

The ownership chain is direct and closed:

```text
existing Goodix candidate 0x0002CDD4
  -> GH_NADT streaming process 0x0006E008
       -> NADT window classifier 0x000856EC
            -> NADT primary signal classifier 0x00047240
```

The complete unclassified callee closure rooted at `0x0006E008` ends after four additional
levels; no other unclassified descendants remain beyond this census. Public result, version,
reset, initialization, and preprocessing entry points at `0x0006E540`, `0x0006E548`,
`0x0006E574`, `0x0006E664`, and `0x0006E838` are independently called from the Goodix
wrapper/demo component. The direct branch to `0x0006E574` occurs at `0x0002CDBE`; it is
pinned from the executable bytes even though the Ghidra callgraph export omitted that edge.

The 682-byte preprocessing root at `0x0006E838`, body SHA-256
`d0e8d34ddfaf97ba47f66e94aa6a104b3efac71452ecb02f4f5a25379f04f656`, now compiles as
`goodix_primitives_nadt_preprocess_execute`. It preserves the recovered process/frame counters,
two failure-encode paths, accumulation-readiness return, 25-frame batch index, exact fourteen-stage
ordering, quartic output transform, threshold-gated bit-range adjustment, and inference-status
return. All five transient stock allocations are explicit caller-owned spans. Its direct stage
callees are already source-admitted typed C entries; no recovered address or private allocation is
retained in the executable path.

The 874-byte alternate-state classifier at `0x0007DD58`, body SHA-256
`46240b4aebd8a3f9d4b26e2f109215ddb0793c7005de78f85826dc9ab7711775`, now compiles as
`goodix_primitives_nadt_alternate_state_classify`. Its fixed 200-sample range and sample gates,
two shared-state autocorrelation passes, strict signed-extrema filter, peak quality, alternating
interval statistics, and consecutive-match transition are typed explicitly. The two signal banks,
two extrema banks, and interval bank replace five stock heap allocations with caller-owned
workspace. The stock processing spin is a checked rejection.

The previously unresolved spectral pair is now directly closed by the preprocessing entry:

```text
0x0006E838 -> 0x000766AC -> 0x00035850
```

`0x000766AC` prepares a resampled spectral window, extracts candidate peaks, and calls
`0x00035850`; `0x00035850` scores harmonic consistency and selects bounded candidates. The first
body is now reconstructed as `goodix_primitives_nadt_spectral_peak_prepare`: its private channel
offset and scale vector/factor are bounded typed inputs, its nine heap temporaries are caller
workspace, and `0x00035850` is an explicit harmonic-selector binding. The downstream selector
retains its independent provider gate.

The preprocessing core also has one direct child that the earlier census missed:

```text
0x0006E838 -> 0x00036F88
```

`0x00036F88` is a 744-byte NADT state/output-selection helper. Its sole callsite is
`0x0006EA7A` inside the authenticated preprocessing core, and its only direct calls are Arm
toolchain floating-point helpers. It now compiles as
`goodix_primitives_nadt_output_state_select`: the private lane record becomes typed rate history,
threshold, signal, persistence, retained-rate, phase, flag, and five-state fields. The local entry
preserves kinds 1/2/5, states 0/1/2/12/21, strict sample/threshold gates, bounded 65..100 output,
retained-rate perturbation, and the late persistence override.

The later closure of the signal-confidence path adds another exact private graph:

```text
0x0006E838 -> 0x00095828 -> 0x00029144
                              -> signal correlation, peak, and statistic helpers
```

`0x00095828` has the authenticated GH_NADT preprocessing core as its sole caller, at
`0x0006EA88`. Its root now compiles as
`goodix_primitives_nadt_signal_confidence_update`, consuming the already typed
`0x00029144` result and replacing the stock 496-byte allocation with an exact 124-Float32 caller
workspace. It preserves rate blending/selection, strict interval-deviation mode counters, rolling
rate acceptance and hold recovery, rolling mean, and the zero-centered Gaussian confidence
integral. Recursive traversal over the historical direct descendants covers nineteen
functions / 3,246 bytes. Sixteen entries have no
caller outside this graph, while the root's sole external caller is the authenticated preprocessing
core. The half-precision converter `0x00028DE0` and sum-of-squares helper
`0x000928E0` also have callers in two still-unclassified adjacent signal routines, so
outside-caller exclusivity is not claimed for those shared helpers. Their admission rests on the
exact NADT-rooted callgraph and provider data flow, not on invented private symbols.

The 520-byte `0x00029144` root now compiles as
`goodix_primitives_nadt_dual_window_features_extract`. It takes the final 125 Float32 values from
each of two explicit spans, uses the already-local normalized-autocorrelation and multiscale peak
helpers, preserves the stock no-peak `0.5f` dispersion behavior, and retains the exact appended
terminal phase, quality, and periodic-rate paths. The primary autocorrelation is converted through
the recovered sign/5-bit-exponent/10-bit-fraction format before the normalized dot product with the
secondary autocorrelation. The six stock heap allocations are one fixed caller-owned workspace;
the private `+0xD8/+0xDC` and `+0xE8/+0xEC` pointer/count walks are typed source fields. Its body
SHA-256 is `c981e359c84c06bd9782fd5a9230b1f446a78947b354b5d56fc23b4df0851661`.

The window-classifier branch also reaches one now-closed auxiliary classifier:

```text
0x000856EC -> 0x00037B80
```

The 554-byte body compiles as
`goodix_primitives_nadt_auxiliary_state_classify`. It evaluates the final 50
Int16 values, writes the recovered wrapping range diagnostic, calculates the
rounded sample deviation, compacts adjacent duplicates, filters strict local
maxima/minima across half the full range, and applies the recovered endpoint/
trimmed-mean clustering tests. Five configuration fields and the current
result/mode/consecutive-match state replace the absolute objects at
`0x20037E10` and `0x20007C88`. Its 100-byte heap allocation is two fixed
25-entry Int16 index banks in caller workspace. The stock unbounded
processing-state spin is a checked no-mutation rejection. Exact body SHA-256
is `52f12f8d61f54c675abefbdb349899fbbcdec3f843aaaa65f9274e5ba5af601e`.

The preprocessing core also exclusively reaches the generated-model inference bridge:

```text
0x0006E838 -> 0x000968C4 -> 0x0002907C -> 0x00037890 -> 0x00034194
```

That seven-function / 1,964-byte graph normalizes inference input, prepares tensor descriptors,
executes the generated subgraph, and copies the result. The bridge's sole caller is `0x0006E838`
at `0x0006E94E`; every recursive unclassified descendant has no caller outside the graph. Its
tensor operations repeatedly call the already gated Goodix descriptor helper `0x0005D5D0`.
Sensor-algorithm heap calls and Arm memory helpers remain separately owned and excluded. This
evidence originally gated the complete private model graph. The outer `0x00037890` topology now
compiles as a bounded seven-stage orchestrator with typed callbacks. The nested
`0x00034194` body now compiles as
`goodix_primitives_nadt_generated_subgraph_execute`: its nineteen operator
vectors, two quantization-range words, scalar-2000 descriptor, complete
`125 -> 16x125 -> 16x62 -> 16x31 -> 16x15 -> 8x15` topology, branch tensor,
and 0x7C0-byte in-place workspace are explicit. Private operator/model weights
remain caller bindings rather than copied firmware data. Its exact body hash
is `18b51a96c3f0c3d0c9c47727c5ec8f5a569e603ad2c882e74fef43f84588e285`.

Generic compiler/runtime helpers and the separately gated sensor-algorithm heap are excluded.
This is therefore a provider-boundary closure, not an inference that every adjacent math routine
belongs to Goodix.

## Exact census

| Entry | Executable bytes | Boundary role |
| --- | ---: | --- |
| `0x00028B18` | 114 | second-order difference-equation output with standard round provider; source-admitted |
| `0x00028DE0` | 6 | NADT half-precision conversion helper |
| `0x00028DEC` | 40 | NADT vector conversion helper |
| `0x00028E14` | 66 | NADT input validity helper |
| `0x0002907C` | 18 | NADT generated-model executor wrapper |
| `0x00029144` | 520 | NADT dual-window feature/correlation extractor with caller workspace and exact packed-5/10 correlation path; source-admitted |
| `0x0002F7DC` | 138 | three-stage Float32 tensor projection with fixed `0x1F0` middle bank; source-admitted |
| `0x00030B6C` | 300 | eleven-boundary plus uniform 23-tap reflected NADT window filter with typed matrix and caller scratch; source-admitted |
| `0x00031624` | 192 | NADT secondary classifier helper |
| `0x00034194` | 630 | nineteen-operator generated-model subgraph with explicit range words and fixed workspace; source-admitted |
| `0x0003497C` | 180 | NADT peak-quality helper |
| `0x000357A2` | 44 | NADT sample statistic helper |
| `0x00035850` | 1,162 | NADT harmonic-candidate selector |
| `0x00035F70` | 192 | NADT signal normalization helper |
| `0x00036034` | 394 | three-lane direct/calibrated NADT sample preparation with caller-owned previous-configuration state; source-admitted |
| `0x000361D8` | 88 | capped squared-deviation statistic; source-admitted |
| `0x0003623C` | 70 | indexed signed-16 trimmed mean; source-admitted |
| `0x00036394` | 110 | NADT Int16 sample-standard-deviation helper; source-admitted |
| `0x00036734` | 140 | NADT local-peak index extractor; source-admitted |
| `0x00036F88` | 744 | NADT five-state rate/output selector with typed history and configuration; source-admitted |
| `0x000373A4` | 216 | two-stage NADT optical sample transform with explicit coefficient/history banks and round provider; source-admitted |
| `0x000377D8` | 178 | positive cosine-similarity helper; source-admitted |
| `0x00037890` | 500 | seven-stage NADT generated-graph orchestrator with typed subgraph/node bindings; source-admitted |
| `0x00037A84` | 220 | NADT peak dispersion/phase-quality estimator; source-admitted |
| `0x00037B80` | 554 | final-50 range/deviation/extrema auxiliary state classifier with explicit state and caller workspace; source-admitted |
| `0x0003E6C8` | 216 | NADT Gaussian interval-probability helper; source-admitted |
| `0x00042BD0` | 316 | NADT periodic-peak rate estimator with caller-owned selection/difference scratch; source-admitted |
| `0x00047240` | 3,240 | NADT primary signal classifier |
| `0x0005144C` | 66 | signed-32 vector mean; source-admitted |
| `0x0005CED4` | 158 | signed min/max and Float32 online-statistics update; source-admitted |
| `0x00061F94` | 30 | NADT sample-mean wrapper |
| `0x00061FB4` | 28 | NADT sample-sum helper |
| `0x00061FD4` | 22 | NADT sample-standard-deviation wrapper; source-admitted |
| `0x00066394` | 28 | NADT rolling-vector latest-value accessor |
| `0x00066490` | 4 | NADT rolling-vector length accessor |
| `0x000666A4` | 110 | NADT normalized autocorrelation helper; source-admitted |
| `0x000668DC` | 36 | NADT minimum-index helper |
| `0x00066900` | 434 | NADT local-maximum mask helper; source-admitted |
| `0x00066B30` | 222 | NADT reflected-boundary signed-int FIR helper; source-admitted |
| `0x0006E008` | 1,294 | GH_NADT streaming process |
| `0x0006E540` | 4 | GH_NADT result accessor; source-admitted as explicit binding |
| `0x0006E548` | 30 | GH_NADT public-version copier |
| `0x0006E574` | 210 | GH_NADT state reset; source-admitted with typed workspace and release binding |
| `0x0006E664` | 712 | GH_NADT initializer; source-admitted with explicit caller-owned workspace and allocator binding |
| `0x0006E788` | 126 | exact GH_NADT preprocessing/DSP identity builder; source-admitted |
| `0x0006E838` | 682 | GH_NADT preprocessing orchestrator with typed stage plan and caller-owned scratch; source-admitted |
| `0x0006F838` | 190 | three-stage UInt8 tensor workspace pipeline; source-admitted |
| `0x000766AC` | 478 | fixed-125 NADT spectral peak-preparation pipeline with caller workspace and explicit harmonic-selector binding; source-admitted |
| `0x0007DCD8` | 60 | NADT sample-variance helper; source-admitted |
| `0x0007DD58` | 874 | fixed-200 NADT alternate-state classifier with typed state and caller-owned workspace; source-admitted |
| `0x000856EC` | 1,154 | NADT window classifier |
| `0x00087618` | 176 | NADT turning-point index extractor; source-admitted |
| `0x000928E0` | 26 | NADT sum-of-squares helper |
| `0x00092A04` | 336 | NADT correlation/convolution helper; source-admitted |
| `0x00095750` | 198 | capped inference-input normalization helper; source-admitted |
| `0x00095828` | 674 | NADT signal-confidence/state tracker |
| `0x000968C4` | 290 | one-lane NADT generated-model inference bridge with caller scratch and explicit executor/selector bindings; source-admitted |
| `0x00097984` | 86 | alternating-extrema bounded-history update; source-admitted |
| `0x00098E4C` | 126 | strict signed-16 local-extrema index extractor; source-admitted |

Six compiler-scattered bodies use explicit executable segments rather than absorbing intervening
functions or literal islands:

- `0x00035850`: `0x00035850..<0x00035C40`, `0x00035C78..<0x00035D12`
- `0x00036034`: `0x00036034..<0x000361AE`, `0x000361B0..<0x000361C0`
- `0x00047240`: `0x00047240..<0x000476E6`, `0x000476F8..<0x00047B08`,
  `0x00047B18..<0x00047F0A`
- `0x0006E008`: `0x0006E008..<0x0006E410`, `0x0006E42C..<0x0006E532`
- `0x0006E664`: `0x0006E664..<0x0006E75E`, `0x00073E2C..<0x00073FFA`
- `0x000856EC`: `0x000856EC..<0x00085AF0`, `0x00085B1C..<0x00085B9A`

The historically paired bodies are independently hash-pinned as
`c9fbb161215e9026649909ed8ef04b628221d7d51cbd4affb3c04f0a4c6a6c7a` for the 1,162
executable bytes of `0x00035850` and
`adf8c54c2b2af59806f5a940cb1470aa71c010e3918ce4725559063151b25c33` for the 478-byte
`0x000766AC` body; the latter now maps to the source-admitted typed pipeline
while `0x00035850` remains provider-gated.
The later 744-byte `0x00036F88` closure is pinned as
`1c454b3b53453c7d2e53dc9c04a6ed66c3d82d85b1e3dc7d389085d1cc59f3f3`.
The 682-byte preprocessing root `0x0006E838` is pinned as
`d0e8d34ddfaf97ba47f66e94aa6a104b3efac71452ecb02f4f5a25379f04f656`.
The 874-byte alternate-state classifier `0x0007DD58` is pinned as
`46240b4aebd8a3f9d4b26e2f109215ddb0793c7005de78f85826dc9ab7711775`.
The nineteen-function signal-confidence graph is pinned as 3,246 executable bytes; its entry is
`0x00095828`, whose 674-byte body SHA-256 is
`509a3440ed4c47ba3c10db0911eb66bff2fbe1bf804e294ad5fe024dad5b98eb`.
The seven-function inference graph is pinned as 1,964 executable bytes; its former largest unknown
at `0x00034194` has 630-byte body SHA-256
`18b51a96c3f0c3d0c9c47727c5ec8f5a569e603ad2c882e74fef43f84588e285`.

The static summarizer verifies the supplied application image hash, every segment hash and size,
all direct callsites, the identity marker, aggregate counts, and the non-redistributable provider
disposition:

```sh
python3 tools/evidence/summarize_r1_goodix_nadt_boundary.py
```

It emits no algorithm source and performs no live sensor access.

## Integration rule

OpenR1 must bind the still-gated bodies in this boundary only through an authenticated licensed
Goodix provider matching the recovered ABI and component identity. If that provider is absent,
NADT-dependent behavior whose closure crosses those bodies remains disabled. Observable public
outputs may be used as compatibility tests for an admitted provider, but decompiled control flow
is not a substitute implementation outside the owner-authorized source reduction.
