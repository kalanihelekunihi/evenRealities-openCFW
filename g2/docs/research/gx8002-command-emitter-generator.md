# GX8002 command-stream generator infrastructure

Date: 2026-09-11. This closes part of the "source-authored generator" half of
the codec's model/accelerator-program gap (`docs/source-only-goal.md`: "The
codec has ... 9,164 accelerator-command bytes, and 120,800 model bytes"),
without closing either byte range. It builds the encoder side of the
gxDNN/SNPU command-stream format that `analyze_gx8002_model_command_chain.py`
and `docs/research/gx8002-gxdnn-cmodel.md` already decoded read-only, and a
standard half-precision quantizer for the tensor data such a program would
reference.

## What was built

`tools/gxdnn_command_emitter.py` is a source-authored assembler/disassembler
for the command-stream wire format:

- the 32-bit base-slot/offset addressing scheme;
- header framing: opcode byte, the sequential-vs-linked bit, the relative
  link word (the absolute-pointer bit is rejected, matching the existing
  analyzer -- that representation is still unresolved), and the
  completion-interrupt bit `cmd_process.o` was shown to test;
- full field layout for the three opcode-1 general-operation subtypes that
  are completely decoded: `copy` (subtype 2), `tensor_vector` (subtype 4)
  and `tensor_tensor` (subtype 5) -- addresses, 12/12/8-bit extents,
  outer/middle strides (inner stride is the implicit 1 already established),
  16-bit immediate, and the two-bit arithmetic selector resolved in
  `gx8002-gxdnn-arithmetic-dispatch.json`.

Every other opcode (`0x40`/`0x41`/`0x42`/`0x43`) and every other opcode-1
subtype (`active`, `pool`, `reduce`, `tensor_scalar`, `format`, `bn`) has no
established field semantics in this tree, so the module never invents any:
it carries those bodies as an explicitly opaque `RawCommand` payload that
round-trips losslessly but is not interpreted. A program built only from
`CopyCommand`/`TensorOpCommand` is fully understood, named-field source with
no opaque content.

`tools/gxdnn_quantize.py` quantizes tensor elements to the codec's two-byte
half-precision format. It reuses Python's standard IEEE754 binary16 codec
(`struct` format `e`) rather than reimplementing rounding, because
`gx8002-half-table-matches.json` and `gx8002-half-arithmetic-verification.json`
already established that the codec's compiled conversion tables and rounded
arithmetic match that same round-to-nearest-even IEEE binary16 behavior.

## Field discovery beyond the existing decode

While building the encoder, three payload positions the existing analyzer
does not export were checked byte-by-byte across every one of the 212
shipped commands: the word at payload offset 4 for `copy` commands, the word
at payload offset 8 for `copy`/`tensor_vector`/`tensor_tensor` commands, and
the six tail bytes at payload offset 34. All three are exactly zero in every
one of the 152 shipped `copy`/`tensor_vector`/`tensor_tensor` commands (the
nonzero tail values observed elsewhere belong to the still-opaque `bn`/
`active` subtypes and are untouched by this work). The encoder therefore
treats them as reserved-must-be-zero fields and the decoder raises if it
ever sees them nonzero, rather than silently discarding unexplained data.
The three subtypes' tensor/copy control words were likewise confirmed to
carry only the subtype nibble and, for tensor ops, the two-bit arithmetic
selector -- no stray bits -- across all 152 instances.

Header bits 8-9 do vary among otherwise-identical-looking `copy`/
`tensor_vector`/`tensor_tensor` commands (values 0, 0x100, 0x300 observed)
with no explanation anywhere in this tree. The `Command.header_reserved`
field preserves these verbatim without claiming to understand them.

## Qualification

`tests/test_gxdnn_command_emitter.py` and `tests/test_gxdnn_quantize.py`
(22 cases) cover: address/extent codec round-trips; per-command round-trips
for `copy` and both `tensor_vector`/`tensor_tensor` arithmetic kinds across
randomized synthetic values; rejection of the reserved-nonzero, absolute-
link, and out-of-range-selector cases; a 50-command randomized synthetic
program round-trip; and half-precision quantization against known IEEE
binary16 values and Python's own reference codec.

One test class authenticates the firmware image and the codec's shipped
9,164-byte command block by SHA-256 (the same hashes
`analyze_gx8002_model_command_chain.py` pins), decodes all 212 commands with
this module, and re-encodes them -- reproducing the original bytes exactly.
This is an **encoder fidelity check against the real oracle**: it shows the
assembler correctly implements the addressing/extent/stride/selector
encoding for every `copy`/`tensor_vector`/`tensor_tensor` command actually
shipped (152 of 212), plus lossless framing round-trip for the 60 still-
opaque commands. It does **not** admit the shipped graph, its specific
addresses/extents/strides, or any of its bytes as source-owned: those values
were read from the stock image, not authored, and the test says so in its
docstring. Building a *new* program from freshly authored `CopyCommand`/
`TensorOpCommand` values (not derived from decoding stock bytes) is what
would actually exercise the generator as a source-authored replacement path.

## What remains open

This does not close either the 9,164-accelerator-command-byte or the
120,800-model-byte range, and no change here touches the codec build,
`overlay.json`, or any manifest. Concretely still missing:

- **Field semantics for six of nine opcode-1 subtypes and all four
  non-opcode-1 command types.** `active`, `pool`, `reduce`, `tensor_scalar`,
  `format`, `bn`, and opcodes `0x40`-`0x43` remain fully opaque; 60 of the
  212 shipped commands (including all 18 `bn` batch-norm commands, likely
  holding the nonzero tail constants noted above) cannot be authored, only
  passed through raw. `cmd_process.o`/`calc.o` disassembly is the next route
  (per `gx8002-gxdnn-cmodel.md`'s open items).
- **A trained model.** The 120,800-byte weight block is trained numeric
  parameter data, not configuration; there is no source representation for
  "the weights a keyword-spotting model happened to learn" short of actually
  training a model. This requires: confirming what class labels/wake word
  the device's KWS model actually targets (unknown -- there is no recovered
  ground truth in this tree), a lawfully licensed training corpus for that
  task, and a training pipeline. None of these exist yet in this repository.
- **A functional qualification harness.** Even with a newly trained model,
  "functionally qualified replacement" per `docs/source-only-goal.md`
  requires demonstrating equivalent behavior, which requires a software
  gxDNN command-stream interpreter (executing the decoded arithmetic/
  addressing/broadcast semantics) since no hardware operation is permitted
  and no NPU simulator exists in this tree. That interpreter is unbuilt.
- **Production routing.** Nothing here is wired into
  `build_gx8002_source_candidate.py` or any manifest; per the active goal,
  candidate source that is not production-routed does not count as
  completion, and routing an unqualified replacement model would be
  irresponsible even if it were built.

Recommended next steps, in order: decode the remaining six opcode-1
subtypes and the four non-opcode-1 command layouts; build and qualify a
gxDNN interpreter against the already-authenticated arithmetic/half
semantics; identify (or explicitly rule out) any recoverable ground truth
for the device's actual keyword-spotting task; only then attempt a
from-scratch trained, quantized, emitted, and functionally qualified
replacement, produced under the integration lock.
