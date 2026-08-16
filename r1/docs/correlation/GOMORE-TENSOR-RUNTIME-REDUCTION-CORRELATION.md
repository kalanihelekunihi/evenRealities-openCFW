# GoMore tensor-runtime reduction correlation

Status: owner-authorized clean-room reconstruction, 2026-08-14. This is not GoMore source.

Nineteen tensor-runtime routines / 2,678 bytes are reconstructed from the Ghidra bodies and fresh VFP
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
| `0x0009196E..<0x000919BA` / 76 | `gomore_tensor_add` | elementwise float addition |
| `0x0006562C..<0x0006567A` / 78 | `gomore_tensor_blend` | staged `factor * first + (1 - factor) * second` through the local multiply/map/add closure |
| `0x000656AA..<0x0006570A` / 96 | `gomore_tensor_int8_float_affine` | signed-int8/float dot followed by optional int16 dequantized bias |
| `0x00065538..<0x000655A4` / 108 | `gomore_tensor_dual_affine_activate` | two signed-int8/float branches, optional dual int16 bias, branch sum, and the stock logistic activation seam |
| `0x000655A8..<0x00065626` / 126 | `gomore_tensor_gated_dual_affine_activate` | two signed-int8/float branches, optional dual int16 bias, second-branch gate multiply, branch sum, and the stock `tanhf` activation seam |
| `0x00091E02..<0x00091E6C` / 106 | `quantized_runtime_tensor_slice` | construct a first-dimension view, retain trailing dimensions, and select the exact int8/int16 byte offset while propagating the int8 scale |
| `0x00035D12..<0x00035D6E` / 92 | `gomore_tensor_strided_copy_2d` | derive two source strides from shape selectors and copy the requested 2D output |
| `0x0007CA94..<0x0007CB98` / 260 | `gomore_tensor_pool_1d` | row-wise Float32 maximum or average pooling with explicit window, stride, padding, and tensor bounds |
| `0x000651CA..<0x00065304` / 314 | `gomore_tensor_batch_normalize_half` | normalize rank-2/3 Float32 tensors by caller-supplied half-precision scale, offset, variance, mean, and epsilon parameters |
| `0x00091B08..<0x00091C42` / 314 | `gomore_tensor_conv1d_half` | convolve a two-dimensional Float32 input with caller-supplied three-dimensional half-precision weights, explicit stride, and symmetric padding |
| `0x00065304..<0x00065376` / 114 | `gomore_tensor_conv1d_half_bias` | compose the local half-weight convolution, add a caller-supplied half bias across each output row, and optionally release the input through an explicit binding |
| `0x00065376..<0x000653E6` / 112 | `gomore_tensor_chain_run` | run an explicit descriptor sequence, release each candidate output, replace it with the returned binding, and hand that result to the next stage |
| `0x000653E6..<0x00065536` / 336 | `gomore_tensor_cell_run` | slice three paired primary/bias tensor rows, run two dual affine activations and one first-output-gated activation, then blend the second and third results with exact temporary ownership release |

The stock functions selected in-place operation or allocated an output descriptor through the
already reconstructed `0x00091D9C` tensor-pool allocator. The new API makes the destination
explicit; callers can pass the source buffer for in-place behavior or a separately allocated
buffer. The blend wrapper is flattened to explicit arrays while retaining its four stock arithmetic
stages; the affine and dual-branch wrappers compose the already-local dot and half-dequant
operations. The dual wrappers replace two allocator-owned temporaries with distinct caller-owned
output/scratch arrays. Their literal targets are pinned as Thumb `0x0008F49D` (local logistic) and
`0x0003B329` (toolchain `tanhf`) and are exposed as typed activation callbacks. Shape and
stride fields in the copy wrapper are explicit dimensions/selectors. The slice reuses the typed
shared-runtime descriptor/pool, replaces the stock unchecked interval with explicit bounds, and
retains the stock bufferless view ownership. Unary `expf`, map, and
int16-dequant operations are typed callbacks. This removes allocator
and code-address opacity while preserving arithmetic order, including softmax calling `expf` twice
per element and the dot loop multiplying `weight * scale * input` left-to-right. The pooling
executor replaces descriptor pointers with explicit source/destination extents and exposes the
toolchain maximum operation as a typed callback; mode zero retains the exact `-FLT_MAX` seed,
mode one retains sequential Float32 accumulation/division, and unsupported modes remain inert.

The `0x00065304` wrapper retains the stock output-channel/column bias order and therefore converts
the same half bias once per output element. Its optional `0x00091C48` input release is a typed
runtime/tensor binding; preflight rejects a short bias vector or missing release callback before
convolution, conversion, output mutation, or release. Tests pin the complete padded convolution,
all weight and bias conversions, exact biased output, release arguments, and no-mutation failure.
The adjacent `0x00065376` chain runner replaces the stock overlapping configuration arrays with
typed per-stage descriptors while retaining the exact stage-call, candidate-release, output-slot
replacement, optional first-input release, and next-input handoff order. The still-gated composite
stage body was an explicit callback rather than an embedded code address. Tests pin both stages and
all three releases, including the zero-stage result and short-output preflight path.
The now-local `0x000653E6` composite cell replaces the two implicit descriptor pairs with typed
primary/bias source bindings and a three-index slice provider. It preserves two ordinary dual
activations, the first activation as the third-stage gate, the final factor blend, and the stock
release order: every primary pair, each enabled bias pair, the first activation before blending,
then the second and third activations. Bias-disabled execution never slices or releases bias
bindings. Bounded slice failure releases every binding already acquired while leaving the result
unchanged.
The batch-normalization executor replaces its output allocation and optional input release with an
explicit caller-owned destination. Rank and dimensions are bounded, all private half-precision
parameters are caller inputs, half conversion and `sqrtf` are typed callbacks, and the recovered
outer/channel/width loop plus `(input - mean) / sqrt(variance + epsilon) * scale + offset`
operation order is unchanged.
The convolution executor likewise replaces two tensor-pool allocations and the temporary release
with caller-owned Float32 weight scratch and output arrays. It converts the complete half-weight
tensor before producing output, preserves output-channel/position/input-channel/kernel iteration
order, and exposes the recovered output width while bounding every source, weight, scratch, and
destination extent.

`tests/test_reconstructed_gomore_tensor_runtime.c` covers every executor, in-place-compatible
iteration, signed weights, scale, optional dequant bias, dual-branch addition, recurrent gating,
distinct-scratch enforcement, negative activation, blend endpoints and interior values, a
2x3-to-3x2 stride transpose, maximum/average pooling, inert modes, exact rank-3 batch-normalization
values and callback order, a padded two-channel/two-output half-weight convolution with exact
converted scratch and output values, bounds/provider failures, and empty arrays;
the recurrent-cell fixtures additionally pin all six enabled slices, both dual activations, the
gated activation, the blend tuple, the complete fifteen-release order, bias-free execution, and
later-slice cleanup;
`tests/test_reconstructed_quantized_runtime.c` pins both slice element-width forms, shape/count,
scale propagation, and rejected bounds. The same
sources pass strict host compilation, ASan/UBSan, and freestanding Cortex-M4 compilation.
