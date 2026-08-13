# Nanopb field-decoder cluster boundary audit

This audit records the production successor to the dispatch/extension
milestone. The stock boundary, source recreation, host oracle, fail-closed
ingress audit, Apple placement, and package ownership transition are complete.

## Authenticated stock split

| Function | Stock span | Bytes | SHA-256 |
|---|---:|---:|---|
| `decode_basic_field` | `[0x0048F7F4,0x0048F968)` | 372 | `2b1bf389327c0f6ccde636bbb51e36cd0bab3eccc811db9aa0efd3dbfef9e445` |
| `decode_static_field` | `[0x0048F968,0x0048FB1C)` | 436 | `58eeda598e1b8e418e41323c1749fa1cd7270a38afb93f0e092bec2a8cfa19f1` |
| `decode_pointer_field` | `[0x0048FB1C,0x0048FB30)` | 20 | `05dac50e007fa534e74598ebbf096b7de8143dee0738977e91b36bfa420cdc83` |
| `decode_callback_field` | `[0x0048FB30,0x0048FBE4)` | 180 | `8e278f306b51ccd2cabc176f7674d17665ca0647facb310c2fe99cfd00a62379` |
| Complete cluster | `[0x0048F7F4,0x0048FBE4)` | 1,008 | `ac71748abf2908adf7850dd7fe339f1c8befcee4fbe416250f80aa3159d37098` |

The wide-call census has five internal calls from `decode_static_field` to
`decode_basic_field`. The only direct external entries are the three dispatch
calls at `0x0048FBFC`, `0x0048FC04`, and `0x0048FC0C` to the static, pointer,
and callback functions. The completed alternate/interior/stored-pointer scan
found no executable alternate ingress or stored entry pointer.

## Upstream definitions and release discrimination

The selected nanopb 0.4.9 source commit is
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`.

| Function | Selected `pb_decode.c` span | Bytes | SHA-256 |
|---|---:|---:|---|
| `decode_basic_field` | `[11653,13922)` | 2,269 | `c4465869ffee60864637b4710e393a7bb5c60c00a847e6f28137f4b480c5af71` |
| `decode_static_field` | `[13922,17541)` | 3,619 | `64eb9ced4f650be17dbb7db6fa58f45ccdb9036460ae6d7aa355c3cfb8bcb24e` |
| `decode_pointer_field` | `[19783,24704)` | 4,921 | `06f716c1f96bb2c77c5651b26a9ec5e465958258395e687c1d87dfbd01d70477` |
| `decode_callback_field` | `[24704,26221)` | 1,517 | `45c67a796415dd023421f9108696478250e175837956c48fe8f960e3535afa24` |

A transient checkout/download matrix compared exact brace-balanced
definitions from the official tags:

| Official release | Peeled commit | Basic | Static | Pointer | Callback |
|---|---|---|---|---|---|
| 0.4.4 | `2b48a361786dfb1f63d229840217a93aae064667` | current | older | older | older |
| 0.4.5 | `c9124132a604047d0ef97a09c0e99cd9bed2c818` | current | current | older | older |
| 0.4.6 | `afc499f9a410fc9bbf6c9c48cdd8d8b199d49eb4` | current | current | current | current |
| 0.4.7 | `b97aa657a706d3ba4a9a6ccca7043c9d6fe41cba` | current | current | current | current |
| 0.4.8 | `6cfe48d6f1593f8fa5c0f90437f5e6522587745e` | current | current | current | current |
| 0.4.9 | `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | current | current | current | current |
| 0.4.9.1 | `cad3c18ef15a663e30e3e43e3a752b66378adec1` | current | current | current | current |

This cluster can exclude older source forms when retained behavior or compiled
bytes exercise those changes, but source identity alone does not distinguish
0.4.6 through 0.4.9.1. The no-malloc pointer body is especially weak as a
discriminator because most pointer-allocation source is preprocessed out.

## Rizin call closure

Rizin 0.9.1 was invoked as raw Thumb (`-n -a arm -b 16`, load base
`0x00437FE0`) and recovered exact function sizes plus these calls:

| Caller | Call sites and targets |
|---|---|
| `decode_basic_field` | `0x48F848 -> pb_dec_bool`; `0x48F872 -> pb_dec_varint`; `0x48F89C -> pb_decode_fixed32`; `0x48F8C6 -> pb_decode_fixed64`; `0x48F8E8 -> pb_dec_bytes`; `0x48F90A -> pb_dec_string`; `0x48F92C -> pb_dec_submessage`; `0x48F94E -> pb_dec_fixed_length_bytes` |
| `decode_static_field` | five calls to `decode_basic_field`; `0x48F9DA -> pb_make_string_substream`; `0x48FA30 -> pb_close_string_substream`; `0x48FAA8 -> memory fill`; `0x48FACC -> pb_field_iter_begin`; `0x48FAD6 -> pb_message_set_to_defaults` |
| no-malloc pointer stub | no calls |
| `decode_callback_field` | `pb_skip_field`, make/close substream, `read_raw_value`, `pb_istream_from_buffer`, and dynamic callback dispatch at `0x48FB7A` and `0x48FBDE` |

All named external targets already route to source-owned providers except
`pb_dec_fixed_length_bytes [0x0049053C,0x004905A8)`, 108 opaque stock bytes.
The memory fill can be eliminated locally. The two `BLX` calls are dynamic
application/schema callback ABI and are not missing firmware functions.

## Independent Ghidra confirmation

Ghidra 12.1.2 headless, using the raw Cortex/Thumb image and no full-image
autoanalysis, decompiled all four entries in about seven seconds. It recovered:

- the logical-type and wire-type switch with the same eight scalar/field
  decoder targets;
- required, optional, packed repeated, ordinary repeated, and oneof static
  handling with 16-bit size/count fields;
- the unconditional `no malloc support` error stub;
- callback skipping, bounded string substreams, forward-progress detection,
  raw scalar copying, and both dynamic callback sites.

The pinned diagnostic literals are `wrong wire type`, `invalid field type`,
`array overflow`, `failed to set defaults`, `no malloc support`, and
`callback failed`. The first five relevant literal slots are at `0x00490354`,
`0x00490488`, `0x00490538`, `0x004905A8`, and `0x004905AC`; callback failure
is at `0x004905B0`.

## Progress and next action

| Dimension | Estimate | Remaining work |
|---|---:|---|
| Stock boundaries and direct fixed calls | 100% | complete; maintain fail-closed pins |
| Upstream function identity and release matrix | 100% | optional object-level comparison can strengthen compiler provenance |
| Semantic/ABI recovery | 100% | complete; maintain analyzer pins as production addresses change |
| Source dependency closure | 100% | all fixed callees are source-owned; memory fill is local |
| Source recreation | 100% | selector-isolated implementation and host oracle pass |
| Apple production integration | 100% | complete; maintain object, relocation, placement, manifest, and package pins |
| Linux/Clang 22 reproduction | 0% | deferred until the reviewed compiler profile is available |
| Hardware execution | 0% | intentionally deferred until reverse engineering is near completion |

The recreated implementation is
`components/shared/nanopb/runtime_nanopb_field_decoder_cluster.c`, 14,057
bytes, SHA-256
`6c34245f6d3c305499ffb6be2bae69508fe6c6f4c4b79e8306d3b998f84c9901`.
Its host oracle covers all basic logical-type routes, wrong-wire and invalid
type diagnostics, optional/packed/repeated/oneof state, array overflow,
submessage default initialization, no-malloc pointer failure, callback skip,
progress and diagnostic propagation, plus fixed-length zero/exact/mismatch/
overflow behavior. All ten semantic, diagnostic, and relocation tests pass. Target selectors
0 through 4 compile with warnings-as-errors and expose only the authenticated
source-owned relocation families plus dynamic callback ABI.

The fail-closed analyzer
`tools/analyze_g2_nanopb_field_decoder_cluster.py` authenticates all five stock
boundaries and callers, 26 fixed outgoing calls, eight diagnostic literals and
their load sites, both dynamic callback sequences, the five upstream
definitions, and local source/header identities. Its whole-image scan finds no
stored entry pointers. Forty-seven apparent interior pointer values are pinned
Thumb-2 instruction-halfword collisions. Two apparent alternate branches are
also pinned data/instruction-byte collisions, not executable ingress. The
candidate therefore has zero fixed stock seams and is eligible for placement.

The efficient promotion unit was therefore these four functions plus
`pb_dec_fixed_length_bytes`, not four isolated leaves with one retained stock
seam. Five guarded full-span redirects now replace 1,116 stock executable
bytes. Apple places 1,132 source-owned closure bytes plus eight generated
alignment bytes at `[0x007B3AC0,0x007B3F34)`. The five leaf offsets are
128,924, 129,144, 129,392, 129,840, and 129,884 in the overlay.

The canonical overlay/component/package sizes are
`130064/3653460/4431954`, with SHA-256 values
`1aed0db7defff8bf547d306e417b4e783a569b63357ba9808e344c21d2e41d23`,
`a639f5d33b5db863a430fd98e98bf74ca130da3f51f9cb01947e5706c7dd1032`,
and `dc3c9dc059d32ad46c751dc7fbcc66ed371a01e15492a210fcf4a7d1a6d6bfa4`.
The 1,049-region Apollo manifest yields 1,121 placed, two unresolved, and five
container-only flash records. Package ownership is 130,803 source bytes
(2.951362%), 92,780 generated bytes (2.093433%), and 4,208,371 opaque or
cut-forward bytes (94.955205%); controlled ownership is 5.044795%.

The production nanopb allowlist is now 43 functions, and this cluster has no
fixed executable stock seam. Dynamic application/schema callbacks remain
intentional ABI. The next reconstruction frontier should be chosen from the
remaining origin-classification and low-confidence upstream rows rather than
decompiling already authenticated nanopb source. Linux replay and hardware
execution remain deferred.
