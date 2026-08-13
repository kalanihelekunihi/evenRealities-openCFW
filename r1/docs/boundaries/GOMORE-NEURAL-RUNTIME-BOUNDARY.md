# GoMore floating-point neural runtime boundary

## Decision

The former largest unknown at `0x00076BDC..<0x000770AE` is a 1,234-byte indirect
floating-point neural-layer executor. It is not R1 product behavior and must not be recreated as
local firmware code. The implementation remains gated as
`gomore_health_algorithm_candidate` / `vendor_source_required_not_redistributable` until an exact,
licensed GoMore SDK and its source/version provenance are authenticated.

This decision does not assert an original private symbol. It records the narrower fact needed for
clean-room admission control: the body executes proprietary health-model layers and therefore is
not an unattributed gap eligible for independent implementation.

## Indirect dispatch proof

The Thumb pointer `0x00076BDD` is stored at `0x00074B40`. The layer constructor at
`0x00074AAC` loads that word and writes it into offset `+0x14` of its 24-byte layer descriptor.
There is no direct branch to the executor because the graph runner calls the descriptor callback.

The constructor has sixteen exact direct callsites:

- six from model graph builder `0x0002874C`;
- six from model graph builder `0x0002966C`; and
- four from the additional health-model graph builder `0x0004387C`.

The first two builders are the paired classifier graphs already tied to the two SHA-pinned GoMore
sleep model/descriptor images at `0x000B2458` and `0x000B7998`. The sibling Goodix graph path uses
the separate constructor at `0x00074B44` and callback pointer `0x00085DC5`; it does not provide a
basis for treating this float executor as reusable R1 code.

## Behavioral census

The body performs floating-point convolution with specialized width-1, width-3, and width-5
paths, bias addition, temporary zero padding, optional negative-output activation handling, and a
sigmoid path implemented as `1 / (exp(-x) + 1)` with the exponent input capped at `88.0`.
These details establish the boundary and allow future licensed-source comparison. They are not an
authorization to reproduce the provider implementation or embedded model behavior.

The exact body SHA-256 is
`61c6cdae7f85eb4096726de5fe67c5c7f85ce4bc6991ef4d45a19825779875ea`.

The read-only verifier is reproducible with:

```sh
python3 tools/evidence/summarize_r1_gomore_neural_runtime.py
```

OpenR1 must bind a matching licensed provider or leave this inference capability unavailable.
Nordic SDK, CMSIS, or another generic neural library may not be substituted unless behavioral and
model compatibility are independently established and its license permits the integration.
