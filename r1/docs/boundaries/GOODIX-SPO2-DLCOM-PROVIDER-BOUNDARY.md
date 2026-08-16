# Goodix GH_SPO2 and dlCom processing provider boundary

> Current reduction note (2026-08-14): the owner-authorized source-admission
> policy now supersedes this report's earlier implementation prohibition for
> the seven-function recurrent closure. Entries `0x36408`, `0x6FDE0`,
> `0x739A8`, `0x7400C`, `0x7405C`, `0x74A20`, and `0x74AA4` compile from
> transparent C; see `../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md`.
> The zero-safe population variance at `0x7DD18` and its `0x61FEA` standard-
> deviation wrapper are also local; see `../correlation/GOODIX-PRIMITIVES-REDUCTION-CORRELATION.md`.
> The `0x61F04`/`0x66430` incremental-deviation pair and rolling-window
> entries `0x66470`, `0x66494`, `0x6652A`, `0x66560`, and `0x66608` are local
> as well.
> Numerical post-processing leaves `0x35F44`, `0x36EB4`, `0x37DB4`,
> `0x668A4`, and `0x66C18` are also source-admitted.
> The compiler-scattered `0x3113C` stream accumulator is now source-admitted
> with typed filter/window state and caller scratch.
> The strict spectral-peak/local-energy concentration helper at `0x2FF10`
> is source-admitted with its `log10` dependency as an explicit typed provider.
> The discontiguous report/candidate/event-latch wrapper at `0x29AD8` is also
> source-admitted together with its `0x34500` analyzer through typed bindings.
> The four-channel packed population-deviation adapter at `0x34B54` is
> source-admitted with caller-owned scratch and an explicit square-root provider.
> The seven-way model-graph dispatcher at `0x28AD4` is now local as well;
> its stock ROM table is an explicit typed caller binding with checked index
> and operation slots.
> The final processing root at `0x6C6A8` is now local as well. All executable
> entries in this census are source-admitted. The exact 3,924-word generated
> model is checked-in transparent C data exposed through a typed bounded view;
> no production build reads or retains stock firmware bytes. See
> `../correlation/MODEL-DATA-ADMISSION.md`.

## Decision

The recovered boundary contains 85 functions / 19,568 executable bytes: 82 formerly unclassified
Ghidra functions / 19,520 executable bytes and three manual provenance supplements / 48 bytes.
All remain attributed to `goodix_gh3x2x_candidate`; under the owner-authorized reduction each now
has an independently compiled transparent-C implementation or typed executor veneer.
The original provider census disposition was `vendor_source_required_not_redistributable`; it is
retained as attribution history, while the current ownership ledger records the local sources.

The existing Goodix-gated entry at `0x0002C944` directly invokes the 1,370-byte processing root
`0x0006C6A8` at callsite `0x0002CA24`. A direct-call traversal from that root reaches 56 formerly
unclassified functions / 9,922 bytes in at most five levels. Those bodies construct and process
optical biometric inputs and use the already gated Goodix version/DSP path.

The same component contains a generated model-graph dispatcher at `0x00028AD4`. Its exact table at
`0x000BCF58` contains Thumb pointers to `0x0005D01C`, `0x00038050`, `0x0003007E`, and
`0x000417F0`, followed by three null entries. The latter three are valid 16-byte functions omitted
by Ghidra: each preserves stacked arguments, directly calls the 1,426-byte graph builder at
`0x000742E4`, and returns. The census includes the dispatcher-selected builders and their closed
direct descendants.

Goodix's [GH3220 developer trace](https://developers.goodix.com/zh/bbs/detail/c7d1af01d0e8467cac183bc66c74cdb9)
prints the same `dlCom_pre2exc_pv_v1.3.0_c00c91c9`,
`GH_SPO2_pre_pv_v2.1.10.0`, `277e89de`, and network hash `1f1cf98b` identities embedded in this
R1 image. This is primary-source attribution evidence, not a redistribution grant.

Some small math/model-runtime helpers have callers outside the 56-function direct-root closure.
They are admitted to this provider boundary because they are direct descendants of the recovered
GH_SPO2/dlCom roots and/or are selected by the exact dlCom table, not because of outside-caller
exclusivity. No outside-caller exclusivity is claimed.

The closure now also includes the 364-byte quantization-range helper at `0x00036590`, SHA-256
`7a5924b07eb3bb6587ae894a0152b69b2197ee0930f5fb4fd4f19c6d08f7a393`. Its sole direct call is
at `0x00085F36` inside the adjacent Goodix signed-int8 neural executor. It is structurally
identical to the already gated `0x00036408` helper used by the dlCom recurrent executor, including
the exact `-255`, `255`, `254`, `192.25`, `63.75`, and `1/255` range-adjustment constants. This
is vendor algorithm evidence only; neither helper is reimplemented by openR1.

The closure now also pins the generated quantized recurrent runtime. The already Goodix-gated
GH_SPO2 initializer at `0x0006EC28` exclusively reaches
`0x0006EB94 -> 0x0002F624 -> 0x00036C26`. The scatter-loaded continuation of `0x00036C26`
calls the 686-byte graph builder `0x0004387C` twice, at `0x00099030` and `0x0009903C`, then calls
the recurrent-layer constructor `0x00074A20` at `0x000990AE`. Those four newly admitted bridge and
builder functions total 1,128 bytes. The graph builder's body and exact callers are pinned; shared
descriptor constructors `0x00074AAC` and `0x00074C98` remain outside the Goodix census because the
separate GoMore graphs also call them.

The recurrent-layer constructor
stores Thumb pointer `0x000739A9` from word `0x00074A98` in its 24-byte layer descriptor, so the
graph runner reaches the 1,120-byte executor indirectly. The executor and five constructor/runtime
helpers total seven functions / 2,264 bytes. They implement quantization, gate matrix products,
sigmoid, `tanhf`, and recurrent-state updates and therefore remain provider code, not a local neural
implementation target. The three other constructor callsites are preserved as shared-runtime
evidence rather than used to claim outside-caller exclusivity.

Two additional generated-model bodies are present but unregistered in the shipped image. The
1,100-byte graph executor at `0x000617F8` and its 932-byte quantized neural-layer executor at
`0x000876C8` share the exact model-configuration object at `0x000BD668` with the admitted dlCom
builder at `0x000742E4`; the inner executor also calls the admitted Goodix callback selector
`0x00074C90` at `0x000878B2`. Five executable calls from the outer body reach the inner body.
This establishes provider ownership without inventing private symbols or recreating the model.
Both executors are now separately source-admitted under the owner-authorized reduction policy;
their typed plans and caller-owned scratch preserve topology without making this a live route.

No executable caller or raw function pointer to `0x000617F8`/`0x000617F9` exists in the application
image. A raw Thumb decoder does find apparent callsite `0x0003007A`, but those six bytes are a
literal pool immediately before the real table-selected wrapper at `0x0003007E`; the wrapper begins
after the coincidental instruction encoding and calls `0x000742E4`, not `0x000617F8`. The two newly
source-admitted bodies remain dormant in the shipped image and are not evidence of a production path.

The compiler-scattered report analyzer at `0x00034500` now compiles as
`goodix_primitives_spo2_report_analyze`; its concatenated executable-segment SHA-256 is
`bc76647d6dc27ce40c9742402fc03ed2a819c12381e489ab7057d04d78fc0350`.
It is the typed provider invoked by the already admitted `0x00029AD8` report/event wrapper. The
exact 36-byte output record retains four spectral candidates, concentration and rolling
statistics, ten decision gates, and the persistent streak updates. Bounded spectra and four
explicit rolling-window descriptors replace private pointer arithmetic without enabling the
optical result path or incorporating any model weights.

The 984-byte formatter at `0x0006CCC0` is another provider-owned sibling. The already gated
Goodix input wrapper `0x0002C944` is its sole direct caller, at `0x0002CA2C`, immediately after
calling processing root `0x0006C6A8`. Its optional callback output names the algorithm mode,
sampling frequency, channel count, output window, scaling, timestamp, memory use, heart-rate
state, per-channel PPG samples, enable flags, accelerometer, and gyroscope inputs. Those exact
strings, the body hash, and sole caller are pinned. This is Goodix diagnostic support, not R1
product telemetry. The body now compiles as
`goodix_primitives_spo2_input_diagnostics_emit`; its stock executable SHA-256 is
`bab60e2e6fdbd5958cac9cd00efc6f13ec921e6af437ea9af500a9a84cd95d7c`.
The reconstruction preserves the initial timestamp-zero gate, exact record order and strings,
per-channel PPG loop, `ceil(3 * channel_count / 8)` enable-byte loop, and separate heap-availability
query for each active output route. Bounded typed sinks replace the private variadic formatter and
128-byte scratch ABI, and no telemetry route is enabled by this admission.

The compiler-scattered 1,240-byte stream accumulator at `0x0003113C`, executable-segment SHA-256
`96f4fe901ef2933d58e73b36d5532d8bc3623246beee03d37969cc472b695935`, now compiles as
`goodix_primitives_spo2_stream_accumulate`. Its four optical filters, adaptive discontinuity
limits, packed output histories, decimal-residual filter, four motion histories, percentile
state, and downstream packed histories are explicit typed state. The implementation preserves
warm-up finalization, mode-zero fixed limits, mode-one 60-sample smoothed scales, axis residual
correction, RMS motion magnitude, first-window median cleanup and complete replay, subsequent
rolling-percentile selection, and the every-third magnitude output lane. Caller scratch replaces
the sole stock allocation; no private RAM pointer remains.

The final 1,370-byte processing root at `0x0006C6A8` now compiles as
`goodix_primitives_spo2_process`; its exact executable SHA-256 is
`400fd57d9c750bef559ccbc41301602007192f79f8cc13cebadd528795011d2c`.
It retains first-group integrity sanitation, sampling-frequency quotient and processing cadence,
MSB-first assembly of three four-channel groups, stream accumulation, the `>50` stream and
`>150`/modulo-25 spectral gates, seven-bank expansion and normalization, five-channel spectrum
preparation, report analysis, bins 15 through 113, four-row reciprocal-maximum normalization,
configured in-place quantization, filtered timed dispatch, logistic scoring, exact Float32
rounding, score-70 flag, scaled score, and delayed result publication.

The stock 7,740-byte and 16-byte transient allocations are replaced by one fixed caller workspace.
Configuration, packed banks, spectral sources, report histories, model dispatch records, math
providers, quantized runtime, and all persistent counters are typed bindings. Tests cover cadence,
integrity clearing, exact three-group assembly, mismatch/no-mutation behavior, malformed extents,
and a complete downstream execution. The adjacent report wrapper now models its exact 512-byte
channel-4-to-channel-0 copy with distinct source and destination spans.

## Exact census

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x00028AD4` | 62 | dlCom model-graph dispatcher |
| `0x00028CF4` | 200 | 60-sample mean / 59:1 smoothed scale; source-admitted |
| `0x00028DDA` | 164 | Float32-to-packed-6/9 selector head/shared tail; source-admitted |
| `0x00028DE6` | 106 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000290DC` | 34 | dlCom quantized recurrent-runtime helper |
| `0x00029394` | 96 | GH_SPO2/dlCom row-range normalization helper; source-admitted |
| `0x0002951A` | 196 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00029AD8` | 340 | report analyzer seam, candidate acceptance, history shift, and three-phase event latch; source-admitted |
| `0x0002F624` | 52 | GH_SPO2/dlCom generated-model initialization bridge |
| `0x0002F65C` | 4 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0002FF10` | 338 | strict spectral-peak and local/harmonic energy concentration in dB; source-admitted |
| `0x0003007E` | 16 | manual dlCom graph-builder table wrapper; source-admitted executor veneer |
| `0x00030800` | 364 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0003113C` | 1,240 | four-channel optical/motion stream accumulator with typed histories and caller scratch; source-admitted |
| `0x00031774` | 82 | strict positive local-peak maximum selector; source-admitted |
| `0x00034500` | 1,102 | GH_SPO2/dlCom report analyzer; source-admitted |
| `0x00034B54` | 348 | packed-6/9 four-channel population deviations with stride-three selection; source-admitted |
| `0x00035772` | 48 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00035D6E` | 196 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00035F44` | 44 | decimal truncation; source-admitted |
| `0x00036408` | 364 | dlCom quantized recurrent-runtime helper |
| `0x00036590` | 364 | dlCom quantized recurrent-runtime helper |
| `0x00036718` | 26 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000367C4` | 230 | transient-history indexed dispatch and capped logistic score transform; source-admitted |
| `0x000368D0` | 160 | quartile-band median replacement; source-admitted |
| `0x00036B58` | 116 | default-range in-place Float32-to-Int8 quantizer wrapper; source-admitted |
| `0x00036C26` | 262 | GH_SPO2/dlCom generated-model initialization bridge |
| `0x00036EB4` | 72 | two-word bit-reversal permutation; source-admitted |
| `0x000372B0` | 214 | scaled four-to-eight-decimal residual with parity sign; source-admitted |
| `0x0003754A` | 2 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00037DB4` | 56 | warm-up sample average finalizer; source-admitted |
| `0x00037F54` | 206 | seven-bank packed-6/9 to Float32 workspace expansion; source-admitted |
| `0x00038050` | 16 | manual dlCom graph-builder table wrapper; source-admitted executor veneer |
| `0x0003F740` | 168 | gated packed-6/9 triplicate workspace expansion; source-admitted |
| `0x0003F7F8` | 164 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000417F0` | 16 | manual dlCom graph-builder table wrapper; source-admitted executor veneer |
| `0x00041F4C` | 210 | rolling sorted-window percentile selector; source-admitted |
| `0x00042024` | 228 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0004304C` | 50 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0004387C` | 686 | GH_SPO2/dlCom generated model-graph builder |
| `0x0005CDF8` | 150 | elapsed-gated typed dispatch and exact Float32 output scaler; source-admitted |
| `0x0005CEA8` | 40 | input-word copy and typed five-binding dispatch wrapper; source-admitted |
| `0x0005D01C` | 400 | dlCom generated model-graph builder |
| `0x0005D5D0` | 16 | GH_SPO2/dlCom shared graph-runtime helper |
| `0x000617F8` | 1,100 | dormant dlCom generated model-graph executor |
| `0x00061EF2` | 16 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00061F04` | 138 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00061FEA` | 22 | population-standard-deviation wrapper; source-admitted |
| `0x000662DA` | 16 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000663B4` | 120 | UInt8 population-standard-deviation helper; source-admitted |
| `0x00066430` | 34 | incremental-deviation descriptor wrapper; source-admitted |
| `0x00066470` | 68 | float-window mean; source-admitted |
| `0x00066494` | 92 | indexed float-window removal; source-admitted |
| `0x0006652A` | 54 | signed-16 rolling-window push; source-admitted |
| `0x00066560` | 64 | byte rolling-window push; source-admitted |
| `0x00066608` | 154 | decimated float rolling-window push; source-admitted |
| `0x0006671C` | 266 | cascaded biquad sample processor with discontinuity correction; source-admitted |
| `0x000668A4` | 50 | reciprocal-maximum normalization; source-admitted |
| `0x00066C18` | 48 | percentile lookup; source-admitted |
| `0x0006C6A8` | 1,370 | complete GH_SPO2/dlCom processing root with fixed caller workspace; source-admitted |
| `0x0006CCC0` | 984 | GH_SPO2/dlCom typed input diagnostic emitter; source-admitted |
| `0x0006EB94` | 128 | GH_SPO2/dlCom generated-model initialization bridge |
| `0x0006FDE0` | 54 | dlCom quantized recurrent-runtime helper |
| `0x000708F8` | 498 | fixed five-channel normalized spectrum preparation; source-admitted |
| `0x000739A8` | 1,120 | dlCom quantized recurrent-layer executor |
| `0x0007400C` | 80 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0007405C` | 208 | dlCom quantized recurrent-runtime helper |
| `0x000742E4` | 1,426 | dlCom generated model-graph builder |
| `0x00074AA4` | 4 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00074A20` | 120 | dlCom quantized recurrent-layer constructor |
| `0x00074B44` | 144 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00074C6C` | 30 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00074C90` | 4 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00074CB4` | 34 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00074CE4` | 30 | GH_SPO2/dlCom shared graph-runtime helper |
| `0x00075E1C` | 318 | real-input FFT magnitude reduction; source-admitted |
| `0x000768B8` | 396 | 128-point complex radix-2 DIF core; source-admitted |
| `0x0007DD18` | 58 | population-variance helper; source-admitted |
| `0x00085CA4` | 22 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000876C8` | 932 | dormant dlCom quantized neural-layer executor |
| `0x000928CA` | 2 | GH_SPO2/dlCom shared runtime helper |
| `0x000929D6` | 46 | GH_SPO2/dlCom shared runtime helper |
| `0x00092B68` | 44 | GH_SPO2/dlCom shared runtime helper |
| `0x00095B04` | 22 | configured-shape in-place quantizer veneer; source-admitted |
| `0x00099010` | 4 | GH_SPO2/dlCom closed-callgraph helper |

## Compiler-scattered executable ranges

The function inventory reports aggregate executable bytes, not contiguous ownership, for several
entries. The verifier concatenates only these exact instruction ranges:

- `0x00028DDA..<0x00028DE0` + `0x000362F4..<0x00036392` = 164 bytes
- `0x00028DE6..<0x00028DEC` + `0x0004FDF8..<0x0004FE5C` = 106 bytes
- `0x00029AD8..<0x00029BB4` + `0x00098F84..<0x00098FFC` = 340 bytes
- `0x0003113C..<0x00031554` + `0x00031564..<0x00031624` = 1,240 bytes
- `0x00034500..<0x00034902` + `0x00034930..<0x0003497C` = 1,102 bytes
- `0x00066470..<0x0006648C` + `0x0009295C..<0x00092984` = 68 bytes
- `0x0006671C..<0x000667BA` + `0x0009285E..<0x000928CA` = 266 bytes
- `0x000742E4..<0x000747B4` + `0x000747BC..<0x0007487E` = 1,426 bytes

This excludes literal pools, table data, and unrelated neighboring functions. The three manual
wrappers are independently pinned as `0x0003007E..<0x0003008E`,
`0x00038050..<0x00038060`, and `0x000417F0..<0x00041800`.

## Clean-room consequence

Production use remains gated for unreconstructed GH_SPO2 algorithm bodies, the dlCom execution
engine, generated graphs, model topology, and weights. Under the owner-authorized full reduction,
individually bounded helpers may be independently reconstructed from the pinned analysis with
transparent constants and tests; this now includes the FFT core and magnitude reduction above.
Until the complete source closure is bound, the optical biometric path remains fail-closed and
emits no synthetic measurements.

The static census verifies the recovered image hash, all 80 entries, all executable segments,
every function body hash, the complete direct-caller map, the dispatcher table, and exact component
markers. It also pins the diagnostic formatter's sole caller and input-field strings, the shared
model-configuration literals, the five outer-to-inner neural-layer calls, the callback edge, and
the false-positive literal-pool branch encoding:

```sh
python3 tools/evidence/summarize_r1_goodix_spo2_dlcom_boundary.py
```

The summarizer emits no algorithm source, accesses no live sensor, and does not authorize provider
reimplementation.
