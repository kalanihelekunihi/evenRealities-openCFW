# GoMore tensor-runtime reduction correlation

Status: owner-authorized clean-room reconstruction, 2026-08-14. This is not GoMore source.

Six small tensor executors / 546 bytes are reconstructed from the Ghidra bodies and fresh VFP
disassembly of the byte-exact application rebuild (SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1`). No model, graph,
weights, tensor data, absolute function address, or original executable byte is included.

| Stock entry / extent | Reconstructed symbol | Recovered contract |
|---|---|---|
| `0x00091A0E..<0x00091A56` / 72 | `gomore_tensor_map` | apply unary float function elementwise |
| `0x00091C80..<0x00091CCC` / 76 | `gomore_tensor_multiply` | elementwise float multiplication |
| `0x00091CCC..<0x00091D2E` / 98 | `gomore_tensor_leaky_relu` | preserve nonnegative values, multiply negative values by caller scale |
| `0x00091EDC..<0x00091F4E` / 114 | `gomore_tensor_softmax` | two-pass unstabilized `expf`, sum, normalize |
| `0x000919BA..<0x00091A0E` / 84 | `gomore_tensor_dequant_bias_add` | dequantize each int16 bias and add to float input |
| `0x00091D30..<0x00091D96` / 102 | `gomore_tensor_int8_float_dot` | row-major signed-int8 weights × scalar scale × float vector, zero bias |

The stock functions selected in-place operation or allocated an output descriptor through the
already reconstructed `0x00091D9C` tensor-pool allocator. The new API makes the destination
explicit; callers can pass the source buffer for in-place behavior or a separately allocated
buffer. Unary `expf`, map, and int16-dequant operations are typed callbacks. This removes allocator
and code-address opacity while preserving arithmetic order, including softmax calling `expf` twice
per element and the dot loop multiplying `weight * scale * input` left-to-right.

`tests/test_reconstructed_gomore_tensor_runtime.c` covers every executor, in-place-compatible
iteration, signed weights, scale, dequant bias, negative activation, provider failures, and empty
arrays. The same sources pass strict host compilation, ASan/UBSan, and freestanding Cortex-M4
compilation.
