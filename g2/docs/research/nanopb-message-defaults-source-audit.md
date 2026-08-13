# Nanopb `pb_message_set_to_defaults` source audit

## Decision

The G2 function at `[0x0048FDF2,0x0048FE98)` is authenticated, source-recreated,
and production-integrated as nanopb `pb_message_set_to_defaults`. The selected
source oracle is nanopb 0.4.9 commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`, within the already authenticated
pristine-compatible 0.4.7--0.4.9 interval.

## Boundary and topology

The 166-byte stock body has SHA-256
`1409633f121586a45b076e247e2f1f33f6120be85044245f42ca777955bd34e4`.
Four direct `BL` callers enter at the function start:

| Call site | Encoding | 24-byte context SHA-256 |
|---|---|---|
| `0x0048FAD6` | `00f08cf9` | `c705b7ba6429c978f4f95dcae4056e3927fd184615216ec1f638187d7f3bcd9b` |
| `0x0048FD12` | `00f06ef8` | `9acfdc783f3d36de9c15774ce456fcbcbba122841bb38b198636bfcec79b830a` |
| `0x0048FDA2` | `00f026f8` | `3a9995f3f88f01efece026433380fdc356d19370e47b86a679026256aa96d730` |
| `0x0048FEDE` | `fff788ff` | `8a32e955323b76ffad002275f7cc1633fa95a58bd938b44a4a706776f17dd706` |

There is no alternate `B.W`, conditional, narrow, interior, or stored-pointer
ingress. The predecessor `pb_field_set_to_default` span
`[0x0048FCE2,0x0048FDF2)` is 272 bytes with SHA-256
`0d0dd0be0ae68f84bb20e39f7c95f500656316563d95b6d5cc3e290d4b131728`.
The successor is the authenticated 634-byte `pb_decode_inner` body.

## Upstream and dependency closure

The exact upstream definition is `pb_decode.c[31080:32048]`, 968 bytes with
SHA-256
`b907b8141e8f0376e9d5e86bf58efde7465d2a16ca3d30ece27ffda16d3afe9e`.
Its recovered stock calls are:

| Site | Target | Provider | Ownership |
|---|---|---|---|
| `0x0048FDFC` | `0x0048949C` | `pb_istream_from_buffer` | source |
| `0x0048FE1C` | `0x0048F49C` | `pb_istream_from_buffer` | source |
| `0x0048FE2A` | `0x0048F66C` | `pb_decode_tag` | source |
| `0x0048FE4C` | `0x0048FBE4` | `decode_field` | source replacement |
| `0x0048FE5E` | `0x0048F66C` | `pb_decode_tag` | source |
| `0x0048FE74` | `0x004D93D8` | `pb_field_iter_next` | stock |
| `0x0048FE7E` | `0x0048FCE2` | `pb_field_set_to_default` | stock |

All stream, tag, iterator, recursive-default, and field-dispatch calls now
resolve to reviewed source leaves. The `decode_field` relocation targets
`0x007B39CC`; there is no executable stock or stock-data seam.

## Independent Ghidra confirmation

Ghidra 12.1.2 headless imported the raw image with base `0x00437FE0` and
language `ARM:LE:32:Cortex:default`. Its decompiler independently recovered
the upstream control flow: initialize an empty stream, optionally attach the
descriptor default buffer, decode the first tag, set each field default,
decode a matching serialized default, clear the one-byte presence/count flag,
and advance the iterator until wraparound. It also recovered the same seven
callees and the one-byte wire-type local. This is corroborating semantic/ABI
evidence; the fail-closed byte analyzer remains the canonical proof artifact.

## Production placement and reproduction

Selector 1 emits 158 bytes at `0x007B382C`, relocated SHA-256
`c912af492c733b311f45ba61171d8678f7d2f346e0bced9a6ecde8de5d7ca61c`.
Six strict relocations bind source-owned stream/tag/iterator/default/dispatch
providers. The complete 166-byte stock entry is replaced by a
guarded `B.W` and Thumb NOP fill. The pair adds 414 source bytes, two generated
alignment bytes, and reclassifies 438 stock bytes from opaque to generated.

```sh
python3 tools/analyze_g2_nanopb_message_defaults.py --json
python3 -m unittest tests.test_analyze_g2_nanopb_message_defaults
python3 -m unittest tests.test_runtime_nanopb_defaults_pair
```

The reusable headless helper is `tools/ghidra/DumpFunctionDecomp.java`.
Full-image analysis took about 244 seconds, so subsequent work should preserve
a disposable analyzed project and query functions incrementally.

The analyzer is fail-closed on image identity, body bytes, caller contexts,
ingress topology, outgoing calls, neighbor spans, and the selected upstream
definition. Hardware and Linux byte-reproduction are deferred.
