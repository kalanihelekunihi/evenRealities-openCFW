# Shared quantized-pooling provider boundary

Status: one 434-byte indirect neural-runtime function byte-pinned; implementation blocked pending
an attributable source, version, and license.

## Finding

The former frontier leader `0x00041816..<0x000419C8` is a signed-int8 pooling executor, not R1
application policy. Its body has SHA-256
`a1ac9ab4d9a3ea8143872c726b60ae7c4d778f66ac8afab9b4d39816dca0cb09`. It has no direct branch
caller because constructor `0x00074C6C` stores Thumb pointer `0x00041817` from literal address
`0x00074C8C` into a neural-layer descriptor.

The constructor is reached from four independently gated model-graph builders:

| Provider boundary | Builder | Constructor calls |
| --- | --- | ---: |
| GoMore sleep classifier | `0x0002874C` | 3 |
| GoMore sleep classifier | `0x0002966C` | 3 |
| Goodix GH_SPO2 graph | `0x0004387C` | 3 |
| Goodix dlCom graph | `0x0005D01C` | 1 |

That mixed call topology proves this is shared neural-runtime machinery, but it does not prove
whether GoMore, Goodix, or another bundled runtime owns the implementation. Similarity to generic
pooling operations is not enough to substitute CMSIS-NN or another library.

`../../scripts/firmware/summarize_r1_quantized_pooling_boundary.py`
authenticates the application, complete executor and constructor bodies, empty direct-caller set,
all ten constructor callsites, and the exact function pointer.

## Behavioral census, not a rewrite specification

The recovered dispatcher operates on signed eight-bit tensors. It selects maximum pooling for
window values 2 and 4, average pooling for window value 3, and uses sign-aware half rounding for
the average result. Unsupported descriptor combinations perform no recognized transform, and the
function returns zero.

These observations support provider matching and future integration tests only. OpenR1 does not
implement the executor, reconstruct its descriptor ABI, redistribute model data, or expose a
callable neural-runtime surface.

## Admission decision

The function is classified as `unknown_shared_quantized_neural_runtime_candidate` with disposition
`investigate_before_implementing`. A future implementation must use authenticated upstream source
whose version, license, descriptor layout, rounding, and tensor behavior are verified against this
evidence. Until then both GoMore and Goodix integrations must supply their licensed provider path,
and this shared executor remains unavailable.

```sh
python3 scripts/firmware/summarize_r1_quantized_pooling_boundary.py
```
