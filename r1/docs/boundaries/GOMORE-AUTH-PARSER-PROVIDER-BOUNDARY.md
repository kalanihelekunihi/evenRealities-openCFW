# GoMore SDK authorization-parser provider boundary

## Current decision

The formerly gated function at `0x0008EA0C` / 528 executable bytes is now source-admitted as
`gomore_primitives_sdk_auth_parse` under the owner-authorized clean-room reduction. Its historical
provider attribution remains `gomore_health_algorithm_candidate`; the ownership disposition is now
`clean_room_reimplementation_owner_authorized`.

The body contains `sdkAuth` diagnostics, authorization parsing and dispatch tables, and has one
direct caller: source-admitted typed pKey/authorization orchestration at `0x0006B27C`, callsite
`0x0006B38A`, whose own diagnostics name `gomore_setAuthParameters`. The reconstructed caller and
parser expose no key logging or export. No caller outside the GoMore provider boundary was found.

## Exact evidence

| Entry | Bytes | SHA-256 | Direct callsites |
| --- | ---: | --- | ---: |
| `0x0008EA0C` | 528 | `4d168fed892590719ff7187b985bd55011be122106dc85f192cc300a05c660d0` | 1 |

The exact executable ranges are `0x0008EA0C..<0x0008EA20` and
`0x0008EA24..<0x0008EC20`; the skipped four-byte word at `0x0008EA20` is literal data, not code.

The direct-caller digest is
`89c30133f274cf13ec81bdd160439e31ea792bd70e19e157451895aeb4d851d7`.
The function normalizes the trailing sixteen characters of a 24-character device identifier,
Base64-decodes the fixed pKey buffer, tries two decrypt configurations, requires four
comma-delimited fields, and dispatches them through four parsers plus three validators. The local C
preserves that control flow with bounded buffers and explicit callbacks.

The function calls the already admitted R1 dual-AES callback seam at `0x000891A4` and the
separately source-routed toolchain `strtok` at `0x00027854`. The reconstruction uses a typed decrypt
binding and bounded local token splitting instead of retaining firmware addresses or mutable global
dispatch tables.

## Transparent configuration rule

The original 64 bytes at the two stock decrypt-key addresses are not copied into openR1. Production
configuration supplies two caller-supplied 32-byte decrypt keys and explicit message-match,
field-parser, and validator callbacks. This makes every dependency auditable and prevents a hidden
authorization blob from entering the firmware bundle.

Host tests pin both-key fallback, UUID normalization, four-field dispatch, validator-selected return
values, `-1005`/`-1002` errors, negative parser propagation, and invalid-configuration rejection.
Production-Thumb fixtures execute the stock body with stub keys/callbacks and emit no stock
authorization material.

The original static summarizer remains historical byte/callgraph evidence; the emulator and local
implementation are the current behavioral evidence.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_gomore_auth_parser.py
PYTHONPATH=/tmp/openr1-unicorn python3 tools/evidence/emulate_r1_sdk_auth_parser.py \
  research/decompilation/rebuild/rebuilt-application.bin
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
