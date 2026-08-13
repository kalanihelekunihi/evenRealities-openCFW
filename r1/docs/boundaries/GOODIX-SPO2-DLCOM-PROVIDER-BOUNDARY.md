# Goodix GH_SPO2 and dlCom processing provider boundary

## Decision

The recovered boundary contains 85 functions / 19,568 executable bytes: 82 formerly unclassified
Ghidra functions / 19,520 executable bytes and three manual provenance supplements / 48 bytes.
All are routed to `goodix_gh3x2x_candidate` with disposition
`vendor_source_required_not_redistributable`.

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

No executable caller or raw function pointer to `0x000617F8`/`0x000617F9` exists in the application
image. A raw Thumb decoder does find apparent callsite `0x0003007A`, but those six bytes are a
literal pool immediately before the real table-selected wrapper at `0x0003007E`; the wrapper begins
after the coincidental instruction encoding and calls `0x000742E4`, not `0x000617F8`. The two newly
admitted bodies are therefore provider-owned dormant residue, not evidence of a production path.

The 984-byte formatter at `0x0006CCC0` is another provider-owned sibling. The already gated
Goodix input wrapper `0x0002C944` is its sole direct caller, at `0x0002CA2C`, immediately after
calling processing root `0x0006C6A8`. Its optional callback output names the algorithm mode,
sampling frequency, channel count, output window, scaling, timestamp, memory use, heart-rate
state, per-channel PPG samples, enable flags, accelerometer, and gyroscope inputs. Those exact
strings, the body hash, and sole caller are pinned. This is Goodix diagnostic support, not R1
product telemetry, and its private callback ABI is not reproduced locally.

## Exact census

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x00028AD4` | 62 | dlCom model-graph dispatcher |
| `0x00028CF4` | 200 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00028DDA` | 164 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00028DE6` | 106 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000290DC` | 34 | dlCom quantized recurrent-runtime helper |
| `0x00029394` | 96 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0002951A` | 196 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00029AD8` | 340 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0002F624` | 52 | GH_SPO2/dlCom generated-model initialization bridge |
| `0x0002F65C` | 4 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0002FF10` | 338 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0003007E` | 16 | manual dlCom graph-builder table wrapper |
| `0x00030800` | 364 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0003113C` | 1,240 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00031774` | 82 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00034500` | 1,102 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00034B54` | 348 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00035772` | 48 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00035D6E` | 196 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00035F44` | 44 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00036408` | 364 | dlCom quantized recurrent-runtime helper |
| `0x00036590` | 364 | dlCom quantized recurrent-runtime helper |
| `0x00036718` | 26 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000367C4` | 230 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000368D0` | 160 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00036B58` | 116 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00036C26` | 262 | GH_SPO2/dlCom generated-model initialization bridge |
| `0x00036EB4` | 72 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000372B0` | 214 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0003754A` | 2 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00037DB4` | 56 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00037F54` | 206 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00038050` | 16 | manual dlCom graph-builder table wrapper |
| `0x0003F740` | 168 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0003F7F8` | 164 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000417F0` | 16 | manual dlCom graph-builder table wrapper |
| `0x00041F4C` | 210 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00042024` | 228 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0004304C` | 50 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0004387C` | 686 | GH_SPO2/dlCom generated model-graph builder |
| `0x0005CDF8` | 150 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0005CEA8` | 40 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0005D01C` | 400 | dlCom generated model-graph builder |
| `0x0005D5D0` | 16 | GH_SPO2/dlCom shared graph-runtime helper |
| `0x000617F8` | 1,100 | dormant dlCom generated model-graph executor |
| `0x00061EF2` | 16 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00061F04` | 138 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00061FEA` | 22 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000662DA` | 16 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000663B4` | 120 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00066430` | 34 | GH_SPO2/dlCom shared runtime helper |
| `0x00066470` | 68 | GH_SPO2/dlCom shared runtime helper |
| `0x00066494` | 92 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0006652A` | 54 | GH_SPO2/dlCom shared runtime helper |
| `0x00066560` | 64 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00066608` | 154 | GH_SPO2/dlCom shared runtime helper |
| `0x0006671C` | 266 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000668A4` | 50 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00066C18` | 48 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0006C6A8` | 1,370 | GH_SPO2/dlCom processing root |
| `0x0006CCC0` | 984 | GH_SPO2/dlCom input diagnostic formatter |
| `0x0006EB94` | 128 | GH_SPO2/dlCom generated-model initialization bridge |
| `0x0006FDE0` | 54 | dlCom quantized recurrent-runtime helper |
| `0x000708F8` | 498 | GH_SPO2/dlCom closed-callgraph helper |
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
| `0x00075E1C` | 318 | GH_SPO2/dlCom shared runtime helper |
| `0x000768B8` | 396 | GH_SPO2/dlCom closed-callgraph helper |
| `0x0007DD18` | 58 | GH_SPO2/dlCom closed-callgraph helper |
| `0x00085CA4` | 22 | GH_SPO2/dlCom closed-callgraph helper |
| `0x000876C8` | 932 | dormant dlCom quantized neural-layer executor |
| `0x000928CA` | 2 | GH_SPO2/dlCom shared runtime helper |
| `0x000929D6` | 46 | GH_SPO2/dlCom shared runtime helper |
| `0x00092B68` | 44 | GH_SPO2/dlCom shared runtime helper |
| `0x00095B04` | 22 | GH_SPO2/dlCom closed-callgraph helper |
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

OpenR1 may implement only the product-owned power, transport, scheduling, record conversion, and
health-event adapters around a lawfully obtained and authenticated Goodix provider. It must not
recreate the GH_SPO2 algorithm, dlCom execution engine, generated graph, model topology, weights,
or signal-processing helpers from this recovered code. Until a matching licensed provider is
bound, the optical biometric path remains fail-closed and emits no synthetic measurements.

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
