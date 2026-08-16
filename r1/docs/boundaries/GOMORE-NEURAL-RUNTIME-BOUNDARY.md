# GoMore floating-point neural runtime reduction

## Decision

The former largest unknown at `0x00076BDC..<0x000770AE` is a 1,234-byte indirect
floating-point neural-layer executor. Under the owner-authorized full-reduction policy it now
compiles as `quantized_runtime_float_conv1d_execute`, with checked descriptor, model, tensor,
buffer-capacity, workspace, and `expf` inputs. It retains GoMore attribution but has moved from
`vendor_source_required_not_redistributable` to
`clean_room_reimplementation_owner_authorized`.

## Indirect dispatch proof

The stock Thumb pointer `0x00076BDD` is stored at `0x00074B40`. The layer constructor at
`0x00074AAC` loads that word and writes it into offset `+0x14` of its 24-byte layer descriptor.
There is no direct branch to the executor because the graph runner calls the descriptor callback.
The reconstructed constructor writes the local target adapter instead, eliminating the absolute
firmware dependency.

The constructor has sixteen exact direct callsites:

- six from model graph builder `0x0002874C`;
- six from model graph builder `0x0002966C`; and
- four from the additional health-model graph builder `0x0004387C`.

The first two builders are the paired classifier graphs already tied to the two SHA-pinned GoMore
sleep model/descriptor images at `0x000B2458` and `0x000B7998`. The sibling Goodix graph path uses
the separate constructor at `0x00074B44` and callback pointer `0x00085DC5`; it does not provide a
basis for treating this float executor as reusable R1 code.

## Behavioral census

The body performs channel-major floating-point convolution with specialized width-1, width-3,
and width-5 paths, bias addition, temporary zero padding, optional ReLU/leaky-ReLU activation,
and a sigmoid path implemented as `1 / (exp(-x) + 1)` with exponent input capped at `88.0`.
The checked form uses virtual padding so input storage is not mutated, and requires caller
workspace only when output overlaps the logical input span. Groups are bounded to the stock graph
form (`groups=1`) or the recovered kernel-3 depthwise form.

The exact body SHA-256 is
`61c6cdae7f85eb4096726de5fe67c5c7f85ce4bc6991ef4d45a19825779875ea`.

The read-only verifier is reproducible with:

```sh
python3 tools/evidence/summarize_r1_gomore_neural_runtime.py
PYTHONPATH=/tmp/openr1-unicorn python3 tools/evidence/emulate_r1_float_conv1d.py \
  research/decompilation/rebuild/rebuilt-application.bin
```

The production-Thumb harness pins ordinary and depthwise kernel-3, kernel-5 leaky-ReLU, kernel-1
sigmoid, exact Float32 result bits, and restoration of the stock body's temporarily padded input.
Host tests reproduce those results, cover explicit overlap workspace, and reject malformed shapes
before mutation. Trained model parameters remain separate explicit data inputs and are not copied
from the firmware image by this reduction.
