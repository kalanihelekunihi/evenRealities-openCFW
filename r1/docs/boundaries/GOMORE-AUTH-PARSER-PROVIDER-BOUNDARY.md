# GoMore SDK authorization-parser provider boundary

## Decision

The formerly unclassified function at `0x0008EA0C` / 528 executable bytes is routed to
`gomore_health_algorithm_candidate` with disposition
`vendor_source_required_not_redistributable`. It is not eligible for clean-room local
implementation.

The body contains `sdkAuth` diagnostics, authorization parsing and dispatch tables, and has one
direct caller: already GoMore-gated pKey/authorization orchestration at `0x0006B27C`, callsite
`0x0006B38A`, whose own diagnostics name `gomore_setAuthParameters`. No caller outside the GoMore
provider boundary was found.

## Exact evidence

| Entry | Bytes | SHA-256 | Direct callsites |
| --- | ---: | --- | ---: |
| `0x0008EA0C` | 528 | `4d168fed892590719ff7187b985bd55011be122106dc85f192cc300a05c660d0` | 1 |

The exact executable ranges are `0x0008EA0C..<0x0008EA20` and
`0x0008EA24..<0x0008EC20`; the skipped four-byte word at `0x0008EA20` is literal data, not code.

The direct-caller digest is
`89c30133f274cf13ec81bdd160439e31ea792bd70e19e157451895aeb4d851d7`.
The function normalizes a device identifier, processes an encoded authorization payload through
private dispatch tables, and reports vendor-specific SDK authorization status. Those observable
semantics establish provider placement; they do not authorize reconstruction of the private
format, tables, keys, or validation algorithm.

The function calls the already admitted R1 dual-AES callback seam at `0x000891A4` and the
separately source-routed toolchain `strtok` at `0x00027854`. Several generic-looking helpers remain
unclassified and are not transitively admitted by this closure.

## Provider rule

Enablement requires a lawfully obtained GoMore package with version, binary/source hash, target
ABI, license, and redistribution terms recorded in `third-party/fetched/manifest.json`. Until then:

- do not recreate the authorization parser or dispatch tables;
- do not extract or publish embedded authorization or key material;
- keep the live GoMore authentication path disabled; and
- retain R1 crypto, toolchain runtime, logging, and unresolved helpers as separate boundaries.

The summarizer is static, reads no private key material, emits no authorization material, and
exposes no live authentication operation.

## Reproduce

```sh
python3 tools/summarize_r1_gomore_auth_parser.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
