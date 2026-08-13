# Goodix GH_NADT provider boundary

## Decision

58 functions / 19,274 executable bytes form a byte-pinned Goodix GH_NADT
provider boundary. 57 functions / 19,148 bytes were newly routed out of the unclassified
frontier; `0x0006E788` was already gated as the exact GH_NADT version builder and is retained here
as the identity anchor.

Every function in this census is classified as `goodix_gh3x2x_candidate` with disposition
`vendor_source_required_not_redistributable`. No NADT, liveness, signal-processing, or classifier
implementation is admitted to the clean-room source tree. A matching lawfully obtained Goodix
provider is required. Only separately identified R1 board, transport, lifecycle, configuration,
and output-routing adapters may be created locally.

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
`0x0006E574`, `0x0006E664`, and `0x0006E838` are independently called from the already gated
Goodix wrapper/demo component. The direct branch to `0x0006E574` occurs at `0x0002CDBE`; it is
pinned from the executable bytes even though the Ghidra callgraph export omitted that edge.

The previously unresolved spectral pair is now directly closed by the preprocessing entry:

```text
0x0006E838 -> 0x000766AC -> 0x00035850
```

`0x000766AC` prepares a resampled spectral window, extracts candidate peaks, and calls
`0x00035850`; `0x00035850` scores harmonic consistency and selects bounded candidates. These are
descriptive boundary roles derived from data flow, not recovered private Goodix symbol names. Each
function has exactly the preceding Goodix-rooted direct caller, so the pair is provider-routed
rather than recreated as local DSP.

The preprocessing core also has one direct child that the earlier census missed:

```text
0x0006E838 -> 0x00036F88
```

`0x00036F88` is a 744-byte NADT state/output-selection helper. Its sole callsite is
`0x0006EA7A` inside the authenticated preprocessing core, and its only direct calls are Arm
toolchain floating-point helpers. Its body and caller set are pinned as part of this closure; the
private selection states and thresholds are not admitted as clean-room behavior.

The later closure of the signal-confidence path adds another exact private graph:

```text
0x0006E838 -> 0x00095828 -> 0x00029144
                              -> signal correlation, peak, and statistic helpers
```

`0x00095828` has the authenticated GH_NADT preprocessing core as its sole caller, at
`0x0006EA88`. Recursive traversal over its unclassified direct descendants closes nineteen
functions / 3,246 bytes. The graph covers dual-window correlation, local-peak selection, rolling
statistics, periodic-rate estimation, and confidence/state tracking. Sixteen entries have no
caller outside this graph, while the root's sole external caller is the authenticated preprocessing
core. The half-precision converter `0x00028DE0` and sum-of-squares helper
`0x000928E0` also have callers in two still-unclassified adjacent signal routines, so
outside-caller exclusivity is not claimed for those shared helpers. Their admission rests on the
exact NADT-rooted callgraph and provider data flow, not on invented private symbols.

The preprocessing core also exclusively reaches the generated-model inference bridge:

```text
0x0006E838 -> 0x000968C4 -> 0x0002907C -> 0x00037890 -> 0x00034194
```

That seven-function / 1,964-byte graph normalizes inference input, prepares tensor descriptors,
executes the generated subgraph, and copies the result. The bridge's sole caller is `0x0006E838`
at `0x0006E94E`; every recursive unclassified descendant has no caller outside the graph. Its
tensor operations repeatedly call the already gated Goodix descriptor helper `0x0005D5D0`.
Sensor-algorithm heap calls and Arm memory helpers remain separately owned and excluded. This
evidence gates the private model graph without reconstructing topology, weights, or inference
behavior.

Generic compiler/runtime helpers and the separately gated sensor-algorithm heap are excluded.
This is therefore a provider-boundary closure, not an inference that every adjacent math routine
belongs to Goodix.

## Exact census

| Entry | Executable bytes | Boundary role |
| --- | ---: | --- |
| `0x00028B18` | 114 | NADT scalar transform helper |
| `0x00028DE0` | 6 | NADT half-precision conversion helper |
| `0x00028DEC` | 40 | NADT vector conversion helper |
| `0x00028E14` | 66 | NADT input validity helper |
| `0x0002907C` | 18 | NADT generated-model executor wrapper |
| `0x00029144` | 520 | NADT dual-window feature/correlation extractor |
| `0x0002F7DC` | 138 | NADT generated-model tensor projection helper |
| `0x00030B6C` | 300 | NADT window filter helper |
| `0x00031624` | 192 | NADT secondary classifier helper |
| `0x00034194` | 630 | NADT generated-model subgraph executor |
| `0x0003497C` | 180 | NADT peak-quality helper |
| `0x000357A2` | 44 | NADT sample statistic helper |
| `0x00035850` | 1,162 | NADT harmonic-candidate selector |
| `0x00035F70` | 192 | NADT signal normalization helper |
| `0x00036034` | 394 | NADT sample preparation helper |
| `0x000361D8` | 88 | NADT magnitude statistic helper |
| `0x0003623C` | 70 | NADT classifier subhelper A |
| `0x00036394` | 110 | NADT classifier subhelper B |
| `0x00036734` | 140 | NADT local-peak index extractor |
| `0x00036F88` | 744 | NADT state/output selection helper |
| `0x000373A4` | 216 | NADT optical sample transform |
| `0x00037890` | 500 | NADT generated-model graph executor |
| `0x00037A84` | 220 | NADT peak dispersion/phase-quality estimator |
| `0x00037B80` | 554 | NADT auxiliary state classifier |
| `0x0003E6C8` | 216 | NADT Gaussian interval-probability helper |
| `0x00042BD0` | 316 | NADT periodic-peak rate estimator |
| `0x00047240` | 3,240 | NADT primary signal classifier |
| `0x0005144C` | 66 | NADT array statistic helper |
| `0x0005CED4` | 158 | NADT rolling-vector helper |
| `0x00061F94` | 30 | NADT sample-mean wrapper |
| `0x00061FB4` | 28 | NADT sample-sum helper |
| `0x00061FD4` | 22 | NADT sample-standard-deviation wrapper |
| `0x00066394` | 28 | NADT rolling-vector latest-value accessor |
| `0x00066490` | 4 | NADT rolling-vector length accessor |
| `0x000666A4` | 110 | NADT normalized autocorrelation helper |
| `0x000668DC` | 36 | NADT minimum-index helper |
| `0x00066900` | 434 | NADT local-maximum mask helper |
| `0x00066B30` | 222 | NADT filter kernel helper |
| `0x0006E008` | 1,294 | GH_NADT streaming process |
| `0x0006E540` | 4 | GH_NADT result accessor |
| `0x0006E548` | 30 | GH_NADT public-version copier |
| `0x0006E574` | 210 | GH_NADT state reset |
| `0x0006E664` | 712 | GH_NADT initializer |
| `0x0006E788` | 126 | GH_NADT version builder; previously gated |
| `0x0006E838` | 682 | GH_NADT preprocessing core |
| `0x0006F838` | 190 | NADT generated-model tensor-combine helper |
| `0x000766AC` | 478 | NADT spectral peak-preparation pipeline |
| `0x0007DCD8` | 60 | NADT sample-variance helper |
| `0x0007DD58` | 874 | NADT alternate-state classifier |
| `0x000856EC` | 1,154 | NADT window classifier |
| `0x00087618` | 176 | NADT turning-point extractor |
| `0x000928E0` | 26 | NADT sum-of-squares helper |
| `0x00092A04` | 336 | NADT correlation/convolution helper |
| `0x00095750` | 198 | NADT inference-input normalization helper |
| `0x00095828` | 674 | NADT signal-confidence/state tracker |
| `0x000968C4` | 290 | NADT generated-model inference bridge |
| `0x00097984` | 86 | NADT bounded-history update |
| `0x00098E4C` | 126 | NADT feature-index extractor |

Six compiler-scattered bodies use explicit executable segments rather than absorbing intervening
functions or literal islands:

- `0x00035850`: `0x00035850..<0x00035C40`, `0x00035C78..<0x00035D12`
- `0x00036034`: `0x00036034..<0x000361AE`, `0x000361B0..<0x000361C0`
- `0x00047240`: `0x00047240..<0x000476E6`, `0x000476F8..<0x00047B08`,
  `0x00047B18..<0x00047F0A`
- `0x0006E008`: `0x0006E008..<0x0006E410`, `0x0006E42C..<0x0006E532`
- `0x0006E664`: `0x0006E664..<0x0006E75E`, `0x00073E2C..<0x00073FFA`
- `0x000856EC`: `0x000856EC..<0x00085AF0`, `0x00085B1C..<0x00085B9A`

The two newly closed bodies are independently hash-pinned as
`c9fbb161215e9026649909ed8ef04b628221d7d51cbd4affb3c04f0a4c6a6c7a` for the 1,162
executable bytes of `0x00035850` and
`adf8c54c2b2af59806f5a940cb1470aa71c010e3918ce4725559063151b25c33` for the 478-byte
`0x000766AC` body.
The later 744-byte `0x00036F88` closure is pinned as
`1c454b3b53453c7d2e53dc9c04a6ed66c3d82d85b1e3dc7d389085d1cc59f3f3`.
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

OpenR1 must bind this boundary only through an authenticated licensed Goodix provider matching the
recovered ABI and component identity. If that provider is absent, NADT-dependent behavior remains
disabled and must not be approximated with locally reconstructed vendor logic. Observable public
outputs may be used as compatibility tests for an admitted provider, but decompiled control flow
is not a substitute implementation.
