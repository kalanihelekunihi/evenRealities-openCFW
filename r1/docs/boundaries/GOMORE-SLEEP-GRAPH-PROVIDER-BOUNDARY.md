# GoMore sleep-classifier graph provider boundary

## Decision

Six formerly unclassified functions / 2,188 executable bytes construct and allocate the paired
sleep-classifier graphs used by the already gated GoMore sleep algorithm. They are now routed to
`gomore_health_algorithm_candidate` with disposition
`vendor_source_required_not_redistributable`. OpenR1 does not recreate their graph topology,
descriptors, model parameters, or allocation behavior.

| Entry | Bytes | Boundary role |
| --- | ---: | --- |
| `0x0002874C` | 892 | graph family used for selector value zero |
| `0x00028B8A` | 36 | mode-two graph allocator |
| `0x0002966C` | 884 | graph family used for nonzero selector values |
| `0x000340A0` | 236 | graph-family selector and output-stack builder |
| `0x00048D22` | 36 | mode-one graph allocator |
| `0x00072BE0` | 104 | mode-zero graph allocator and descriptor remapper |

## Exact topology

`0x000340A0` is the only direct caller of both large builders: it calls `0x0002966C` at
`0x000340BA` for nonzero graph families and `0x0002874C` at `0x00034186` for family zero. Its
three direct callers are the allocator wrappers at `0x00028B8A`, `0x00048D22`, and `0x00072BE0`.
Those wrappers are reached through the exact Thumb-pointer table at `0x000BCF40`:

```text
0x00072BE1, 0x00048D23, 0x00028B8B
```

The two graph builders create convolution, shape, pooling, recurrent/state, activation, and output
descriptors. Six calls from each builder enter the already gated floating-point neural-layer
constructor at `0x00074AAC`, whose descriptor callback is the pinned indirect executor
`0x00076BDD`. The exact bodies, direct caller map, constructor table, and aggregate digests are
verified.

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

These graph details establish the provider boundary and enable future licensed-source comparison;
they are not a clean-room model specification. A matching licensed GoMore provider remains
required.

```sh
python3 scripts/firmware/summarize_r1_gomore_sleep_graphs.py
```
