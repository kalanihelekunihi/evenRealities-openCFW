# G2 production microphone test recovery

## Result

The retained `platform\product_test\production_mic_func.c` object is closed as
six functions at `[0x0058F4E4, 0x0058F8CC)`. It occupies 1,000 physical bytes
with SHA-256
`5a277c1e7b593a09a3861987f57707b99651c8b4bc63b5f9f3c07fa4b7f1ad05`:
898 executable bytes plus 102 bytes of alignment and shared literals.

Five functions were present in the authenticated Ghidra corpus. The leading
252-byte `production_pcm_callback_stereo` was not: it is restored from its
stored odd Thumb pointer at `0x0058F8AC`, exact retained diagnostic name and
path reference, contiguous boundary, shared pool, complete decodability, and
provider graph. The adjacent stored pointer at `0x0058F8A0` names the visible
single-channel callback. This makes the callback pair and both codec/PDM
lifecycle pairs complete.

No NationalChip LVP, codec-vendor DSP, CMSIS-FreeRTOS, or other third-party
implementation is linked in this object. Thirty-five calls reach the admitted
EasyLogger/private compact seams, five reach bounded IAR `memset`/`memcpy`, and
twenty-four reach first-party codec, PDM, channel-extraction, callback, and PCM
dispatch services. The object supplies no new dependency version discriminator
or recoverable private commit.

## Reproduction

Run:

```sh
make production-mic-closure
```

The analyzer authenticates the official image, all six bodies including the
restored callback, physical boundaries and shared pool, every instruction and
call, whole-image BL ingress, both stored entries, path references and exact
diagnostic names, upstream logging/compiler provenance, and production-routing
status.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered / restored functions | 6 / 5 / 1 |
| Path-anchored functions | 5 |
| Raw path references / referencing functions | 7 / 6 |
| Body / alignment-pool / physical bytes | 898 / 102 / 1,000 |
| Reachable instructions | 359 |
| Direct calls | 64 |
| Internal / external direct calls | 0 / 64 |
| Indirect calls | 0 |
| Whole-image direct `BL` entries | 8 |
| Stored exact entries / strict-interior entries | 2 / 0 |

The executable-body SHA-256 is
`c7ffe280cd5489f7ab79866325addfb3aa9fe89fed0142170c5819e6899c870b`.
The instruction topology digest is
`f1e45cdff96add83d701bbe4b895c10a37d30afe4a1c77781a5d90486399761c`,
and the direct-call digest is
`7b8a79197f67519a833a1e8b30d0921c7b7bfa4bc36d54ddad47dbb98beb1b70`.

## Recovered callback and lifecycle contract

Both PCM callbacks use fixed 400-byte stack scratch buffers. When extraction
is disabled, the single callback forwards the received PCM buffer and byte
count directly. When enabled, source 0 and source 1 select different
first-party extraction configurations before the bounded result is dispatched.

The restored stereo callback accepts source 0 only. With extraction disabled,
it forwards the source directly. With extraction enabled, it performs two
bounded extraction calls, copies both results into a local output buffer,
concatenates them, and dispatches twice the per-channel byte count. Other
source IDs return without dispatch. The callback's 0x328-byte frame contains
the two 400-byte work areas and fixed bookkeeping; no hidden heap or DSP
library is involved.

Codec microphone initialization uses listener ID `0x10B`, capture mode 0, and
selects the single or stereo callback from a one-byte argument. It then enables
the codec microphone and PCM path. Deinitialization disables the codec, removes
mode 0, and on success unregisters the handler and releases both extraction
buffers.

PDM initialization uses the same listener ID, capture mode 1, and the single
callback, then enables PDM and PCM routing. Its deinitializer reverses those
operations and releases the PDM extraction buffer on success.

## OpenCFW implication

This is first-party manufacturing/test orchestration, not a route to another
vendor DSP source tree. A source candidate can reuse ordinary bounded memory
operations and explicit calls into the future codec/PDM/PCM service boundary.
Golden PCM vectors should test raw forwarding, source selection, mono
extraction, stereo concatenation, zero-length and over-400-byte provider
responses, callback registration failure, and deinitialization cleanup.
Hardware microphone routing and acoustic equivalence remain device-validation
work.

No device, signing, flashing, erase, or runtime operation was performed.
