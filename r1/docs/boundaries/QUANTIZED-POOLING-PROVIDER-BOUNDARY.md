# Shared quantized-pooling provider boundary

Status: six functions / 1,328 bytes of shared quantized-neural runtime byte-pinned; implementation
blocked pending an attributable source, version, and license.

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

`../../tools/evidence/summarize_r1_quantized_pooling_boundary.py`
authenticates the application, complete executor and constructor bodies, empty direct-caller set,
all ten constructor callsites, and the exact function pointer.

The next frontier adds a second shared descriptor path. Constructor
`0x00074CE4..<0x00074D02` stores Thumb pointer `0x000293FD` from `0x00074D04`. Its six callers
include the two GoMore graph builders above and four independently gated Goodix builders.
Indirect executor `0x000293FC..<0x000294B6` converts floating-point tensors to signed Int8 after
helper `0x00035E34..<0x00035F26` derives its scale and zero-point parameters. Their exact sizes are
30, 186, and 242 bytes. The 228-byte int8-add executor `0x00036C7C..<0x00036D60` is installed by
the adjacent shared descriptor path at `0x00074CD8`; it applies two input scales/zero points,
requantizes, saturates, and updates output range metadata. Together with the pooling executor, the
shared boundary was five functions / 1,120 bytes at that tier.
[`FRONTIER-230-248-CORRELATION.md`](../correlation/FRONTIER-230-248-CORRELATION.md) pins the quantizer family;
[`FRONTIER-224-230-CORRELATION.md`](../correlation/FRONTIER-224-230-CORRELATION.md) pins the int8-add executor.

The 204...210-byte frontier adds `0x00093628..<0x000936F8`, a 208-byte twelve-descriptor
tensor-arena compactor/allocator reached at `0x00091DAC` and `0x00091DD6`. It sorts live offsets,
moves live buffers, and allocates from an approximately 1,700-word shared arena. Its surrounding
descriptor runtime is shared across separately gated model graphs, but no exact source identity
or license is known. [`FRONTIER-204-210-CORRELATION.md`](../correlation/FRONTIER-204-210-CORRELATION.md) pins
that sixth body and brings the boundary to six functions / 1,328 bytes.

## Sharpened fingerprint evidence

The provenance investigation added the following structural detail. None of it changes the
admission state; the family remains `investigate_before_implementing`. The ownership-ledger
candidate family now totals 26 functions / 2,486 executable bytes, of which this boundary pins
the six-function / 1,328-byte core documented above.

- AOT-compiled static-graph ABI: 24-byte layer records hold eight packed parameter bytes, the
  model context at `+0x8`, a weights offset at `+0xC`, a bias offset at `+0x10`, and the run
  function pointer at `+0x14`. A compile-time weight-arena cursor is threaded through the
  builders (GoMore sleep `0x0002874C`/`0x0002966C`, GH_SPO2 `0x0004387C`, dlCom `0x0005D01C`).
- Model provenance string triples `{name, "vX.Y.Z", 8-hex git hash}` are embedded and assembled
  into version reports at `0x0006EC90`: `dlCom_pre2exc` / `v1.3.0` / `c00c91c9`,
  `pv_v1.1.0` / `v2.0.3.0` / `21d2063d`, and
  `GH_SPO2_pre_pv_v2.1.10.0` / `277e89de` / `1f1cf98b`. `dlCom` (deep-learning compiler) is a
  private toolchain name with zero public footprint.
- Quantization is asymmetric int8 with float min/max metadata, a zero point biased by `-0x80`,
  and `scale = 255 / (max - min)`. Requantization is performed in float with
  round-half-away-from-zero: the int8-add executor at `0x00036C7C` dequantizes both operands,
  adds, requantizes, and saturates. There is no integer multiplier/shift requantization.
- The pooling executor at `0x00041816` supports only window-2 max (unrolled four times),
  window-4 max, and window-3 average with sign-aware half rounding. The descriptor encodes
  byte0 = type, byte1 = window, byte2 = stride; anything else is a silent no-op returning zero.
- The tensor layer uses a 12-slot descriptor pool with a 0x14 stride and a compacting word arena
  of 0x6A4 words that qsorts live offsets and memmoves (`0x00093628`).
- The same runtime serves both the GoMore sleep-classifier graphs and the Goodix GH_SPO2/dlCom
  graphs, so one private toolchain produced all of the models.

## Candidates rejected

- CMSIS-NN: stateless integer kernels, no descriptor layer.
- TFLM: C++ flatbuffer interpreter, incompatible ABI.
- NNoM: checked against upstream source — dynamic allocation, Qm.n q7 arithmetic, HWC 3-D
  tensors, and a build/run lifecycle do not match.
- uTensor: C++, incompatible ABI.
- TinyEngine, tinyMaix, emlearn, X-CUBE-AI: era/ABI mismatches.

## Next evidence step

Acquire a Goodix GH3x2x health-algorithm SDK or evaluation firmware and check for the
`{name, version, git-hash}` header triple, the `dlCom` string, the 24-byte descriptor with the
function pointer at `+0x14`, and the 12-slot / 0x14-stride tensor pool with the 0x6A4-word
compacting arena. Also grep other wearable firmware dumps in the research workspace for
`dlCom`, `pre2exc`, and `pv_v` strings.

## Behavioral census, not a rewrite specification

The recovered dispatcher operates on signed eight-bit tensors. It selects maximum pooling for
window values 2 and 4, average pooling for window value 3, and uses sign-aware half rounding for
the average result. Unsupported descriptor combinations perform no recognized transform, and the
function returns zero.

These observations support provider matching and future integration tests only. OpenR1 does not
implement the executor, reconstruct its descriptor ABI, redistribute model data, or expose a
callable neural-runtime surface.

## Admission decision

All six functions are classified as `unknown_shared_quantized_neural_runtime_candidate` with disposition
`investigate_before_implementing`. A future implementation must use authenticated upstream source
whose version, license, descriptor layout, rounding, and tensor behavior are verified against this
evidence. Until then both GoMore and Goodix integrations must supply their licensed provider path,
and this shared executor remains unavailable.

```sh
python3 tools/evidence/summarize_r1_quantized_pooling_boundary.py
```

## Attribution re-examination 2026-08

An independent re-test (see
[`unknown_shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md`](unknown_shared_quantized_neural_runtime_candidate-ATTRIBUTION-2026-08.md))
eliminated CMSIS-NN with quoted upstream evidence (integer-only library: `NN_ROUND` is a
shift-offset macro, requantization is `arm_nn_requantize` doubling-high-mult, softmax is
base-2/fixed-point; repo-wide zero float usage) against this family's float requantization
(`(x-min)*(255.0f/range)`, ±0.5 rounding, −128 bias, float softmax capped at `88.0f`). TFLM,
tinyMaix, NNoM, and the TensorFlow public nudge variants were also re-confirmed as non-matches.
The `dlCom` toolchain retains zero public footprint. The runtime therefore remains
unattributed and blocked; the same report identifies the surrounding platform layer's vendor
(Wuxi Bravechip BCL603M/ChipletRing, byte-exact BAE8 GATT base UUID at `0x000991A0`, firmware
string `603MV1.9.3`), which narrows the probable owner of the shared runtime and provides a
commercial source-acquisition route.

## Reduction 2026-08

Under the owner-authorized full reduction (2026-08-14, see
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md)), the twenty-six ledger entries of
`unknown_shared_quantized_neural_runtime_candidate` (the shared quantized tensor executors and descriptor constructors, including the pooling body above) are reconstructed
from the recovered decompilation evidence as independently compiled C in
[`../../reconstructed/quantized_runtime/`](../../reconstructed/quantized_runtime/).  The
reconstruction is not vendor source; it carries per-function provenance
banners, and its contract, reconstruction decisions, divergences, and
host-test mapping are documented in
[`../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md`](../correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md).
The ledger disposition for the twenty-six entries is now
`clean_room_reimplementation_owner_authorized`.  This document remains the
provenance record of why no upstream source was admitted.
