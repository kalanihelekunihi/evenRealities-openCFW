# G2 nanopb field/extension dispatch source audit

Status: production-integrated source recreation  
Target: G2 `2.2.6.10`, Apollo-main image  
Selected upstream: nanopb `0.4.9`, commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`

## Result

The private field/extension dispatch cluster is fully identified and recreated
from authenticated upstream source. The corrected stock function map is:

| Function | Stock span | Bytes | SHA-256 |
|---|---:|---:|---|
| `decode_field` | `[0x0048FBE4,0x0048FC26)` | 66 | `a7e2136d4de19007cab84722398b120c6cf806ec558163447cf11d33064e8479` |
| `default_extension_decoder` | `[0x0048FC26,0x0048FC78)` | 82 | `dbd41534fcd6ff0fc27f1bf87225f233020ba5c904e4aa4a5c9c85a83bd988d6` |
| literal island | `[0x0048FC78,0x0048FC88)` | 16 | `1026cb9d3335a6464ffa01ebd4901588496b37013be9aa1bf13a7de1c95c7fe3` |
| `decode_extension` | `[0x0048FC88,0x0048FCE2)` | 90 | `0f630c1173971762af8df1ec82ed50cff6f292a9b77eafae06e56b9f3b659472` |

This corrects the old recovery-table label that placed `decode_extension` at
`0x0048FC26`. That address is the default extension handler; the extension-chain
dispatcher starts at `0x0048FC88`.

## Upstream identity

The selected `pb_decode.c` definitions are pinned at these byte spans:

| Definition | Source span | Bytes | SHA-256 |
|---|---:|---:|---|
| `decode_field` | `[26221,27053)` | 832 | `1c6111be8313e278c2b1753401a701245c1baa7c90acd085f18c1eb277d7e42d` |
| `default_extension_decoder` | `[27227,27659)` | 432 | `175e06435cc0c7e7f0bf3d44aa6b2d3e0f5f9bc8384ce52d28c80bf21777a691` |
| `decode_extension` | `[27810,28413)` | 603 | `3229a97ca148e192ca3b1d0fd33df3a1654b6405bd247e0b6f6320041460f7da` |

An intermittent official-source lookup fetched `pb_decode.c` by immutable
commit from the nanopb GitHub repository for tags `0.4.4`, `0.4.5`, `0.4.6`,
`0.4.7`, `0.4.8`, `0.4.9`, and `0.4.9.1`. All three brace-balanced definitions
are byte-identical across that complete checked range. Consequently this cluster
cannot distinguish the point release, but it strongly supports direct source
reuse under the independently selected `0.4.9` compatibility baseline.

## Binary topology

The fail-closed analyzer authenticates the official 3,523,396-byte Apollo-main
image before accepting any inference. It proves:

- three callers of `decode_field`: the default extension handler,
  `pb_message_set_to_defaults`, and `pb_decode_inner`;
- one caller of `default_extension_decoder`, from `decode_extension`;
- one caller of `decode_extension`, from `pb_decode_inner`;
- no alternate wide, conditional, narrow, interior, or stored-pointer ingress;
- static calls from `decode_field` to `decode_static_field` at `0x0048F968`,
  the no-malloc `decode_pointer_field` stub at `0x0048FB1C`, and
  `decode_callback_field` at `0x0048FB30`;
- a source-owned call to `pb_field_iter_begin_extension` and recursive
  `decode_field` call in the default handler;
- the `extension->type->decode` dynamic callback sequence at `0x0048FCB8`;
- the stock `"invalid field type"` and `"invalid extension"` diagnostics and
  their PC-relative pointer loads.

These relationships reproduce the upstream control flow without needing to
decompile the cluster instruction by instruction. Capstone Thumb disassembly
was used to cross-check the function endings and dynamic `BLX` sequence after
Rizin's raw-file mapping mode proved unsuitable for this image's nonzero load
base. The checked-in analyzer uses independent Thumb branch decoding and pinned
bytes, so its result does not depend on either interactive tool.

## Production recreation

`runtime_nanopb_dispatch_extension.c` contains three selector-isolated leaves.
The reviewed Apple Clang 21 profile produces:

| Source function | Overlay offset | Run address | Text | Closure |
|---|---:|---:|---:|---:|
| `open_cfw_nanopb_decode_field` | 128680 | `0x007B39CC` | 52 | 71 |
| `open_cfw_nanopb_default_extension_decoder` | 128752 | `0x007B3A14` | 74 | 92 |
| `open_cfw_nanopb_decode_extension` | 128844 | `0x007B3A70` | 80 | 80 |

The first two closures carry 19 and 18 authenticated diagnostic bytes. One
generated alignment byte separates them. Each selected function's 8-byte
`CANTUNWIND`/`R_ARM_PREL31` companion is authenticated and deliberately
discarded as metadata rather than executable closure data.

All three complete stock entries are replaced by fail-closed `B.W` guards and
Thumb NOP fill. Existing relocated `pb_decode_inner` and
`pb_message_set_to_defaults` calls bind to the fixed, reviewed future overlay
addresses. The default handler binds to the source-owned iterator initializer
and relocated `decode_field`; `decode_extension` binds to the relocated default
handler while retaining its application-provided dynamic callback ABI.

The only remaining fixed executable seams are the three adjacent field-decoder
providers called by `decode_field`. They define the next bounded recovery
frontier: `decode_static_field`, the no-malloc pointer stub, and
`decode_callback_field`.

## Reproduction

```sh
python3 tools/analyze_g2_nanopb_dispatch_extension.py --json
python3 -m unittest \
  tests.test_analyze_g2_nanopb_dispatch_extension \
  tests.test_runtime_nanopb_dispatch_extension
```

The host harness covers every attribute dispatch case, sticky diagnostics,
iterator failure, tag/message mismatch, successful default extension decode,
dynamic extension chains, input consumption, and callback failure. Target
tests separately authenticate selector isolation and relocation shapes.
