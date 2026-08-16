# GoMore sleep-classifier graph provider boundary

## Decision

Six pinned functions / 2,188 executable bytes construct and allocate the paired sleep-classifier
graphs used by the GoMore sleep algorithm. All six functions are now owner-authorized transparent
C with disposition `clean_room_reimplementation_owner_authorized`. In particular, the former
892-byte and 884-byte provider gates are reconstructed as
`quantized_runtime_gomore_sleep_graph_family_zero_build` and
`quantized_runtime_gomore_sleep_graph_family_nonzero_build`. Their model arenas are explicit
caller-owned word arrays and target base addresses; no absolute stock model pointer or executable
firmware byte is incorporated by either builder.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x0002874C` | 892 | source-admitted graph family used for selector value zero |
| `0x00028B8A` | 36 | source-admitted mode-two graph allocator |
| `0x0002966C` | 884 | source-admitted graph family used for nonzero selector values |
| `0x000340A0` | 236 | source-admitted graph-family selector and output-stack builder |
| `0x00048D22` | 36 | source-admitted mode-one graph allocator |
| `0x00072BE0` | 104 | source-admitted mode-zero graph allocator and descriptor remapper |

## Exact topology

The source-admitted `0x000340A0` dispatcher is the only direct caller of both large builders: it calls `0x0002966C` at
`0x000340BA` for nonzero graph families and `0x0002874C` at `0x00034186` for family zero. Its
three direct callers are the allocator wrappers at `0x00028B8A`, `0x00048D22`, and `0x00072BE0`.
Those wrappers are reached through the exact Thumb-pointer table at `0x000BCF40`:

```text
0x00072BE1, 0x00048D23, 0x00028B8B
```

The dispatcher consumes its recovered three-by-eight dimension table and executor tokens as
explicit inputs and emits the exact five 24-byte descriptor slots. The two source-admitted graph
builders create the fixed quantizer, convolution, shape, pooling, activation, and output prefix:
family zero consumes 1,714 model words, family one 952, and family two 1,092. Six calls from each
builder enter the source-admitted generic neural-layer descriptor constructor at `0x00074AAC`;
its execution callback `0x00076BDC` is now the local checked Float32 convolution executor, and the
constructor stores its target adapter instead of an absolute firmware token. Production
Thumb emulation asserts the exact complete graph hashes for all three families, while host tests
assert typed topology, cursor consumption, local executor bindings, and invalid-input behavior.

## Model identity and mixed-provider boundary

The graphs consume the two classifier-model regions already verified by the sleep-algorithm
census:

| Family | Range | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| modes below 100 | `0x000B2458..<0x000B7998` | 21,824 | `da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861` |
| modes at least 100 | `0x000B7998..<0x000BCED8` | 21,824 | `09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c` |

The separate builder at `0x0004387C` is intentionally excluded. It is reached through
`0x0006EB94 -> 0x0002F624 -> 0x00036C26` from the Goodix GH_SPO2 path, even though it shares
some model-runtime constructors. Shared mechanics do not justify sweeping a Goodix graph into the
GoMore ownership set.

The topology is no longer a provider boundary. The two 21,824-byte classifier parameter regions
are now checked-in transparent C data, exposed as bounded views over one deduplicated 11,581-word
initializer. They remain provenance-pinned recovered product parameters and are not claimed as an
independent derivation of the trained weights. Normal builds do not read or package the research
firmware image; see
[`MODEL-DATA-ADMISSION.md`](../correlation/MODEL-DATA-ADMISSION.md).

```sh
python3 tools/evidence/summarize_r1_gomore_sleep_graphs.py
python3 tools/generate_r1_model_data.py --check
PYTHONPATH=/tmp/openr1-unicorn python3 tools/evidence/emulate_r1_gomore_sleep_graphs.py \
  research/decompilation/rebuild/rebuilt-application.bin
```
