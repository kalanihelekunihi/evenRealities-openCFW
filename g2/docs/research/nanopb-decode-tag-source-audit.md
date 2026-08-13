# Nanopb `pb_decode_tag` source audit

This audit promotes the complete G2 tag decoder and authenticates the
one-byte `pb_wire_type_t` ABI consumed by the private decoder loop.

## Boundary and upstream provenance

| Evidence | Pin |
|---|---|
| Stock body | `[0x0048F66C,0x0048F6A0)`, 52 bytes |
| Stock SHA-256 | `727a94d16ba7b4018c3addee83a6c63e87f0c3f2a3fe6afdb315549d10f53114` |
| Direct callers | `0x0048FE2A`, `0x0048FE5E`, `0x0048FF68` |
| Upstream definition | nanopb 0.4.9 commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`, `pb_decode.c[8663:9043]` |
| Definition SHA-256 | `6cb0e89f976070f9d561474343e0ef46414107bbf64cbb17302be46dba412cfb` |

The fail-closed analyzer checks all wide/narrow branch forms and raw entry or
interior pointer values. It finds exactly the three `BL` callers, no alternate
or interior ingress, and no stored-pointer matches. The predecessor is the
source-replaced `pb_skip_string` body and the successor is the source-replaced
`pb_skip_field` body, independently hash-pinned.

## Recovered ABI and closure

Stock instructions at `0x0048F674`, `0x0048F678`, and `0x0048F69A` use
`STRB` for `eof` and `pb_wire_type_t`. This proves the wire type occupies one
byte in the G2 ABI, consistent with short-enum compilation, even though the C
upstream declaration uses an enum. The source compatibility header therefore
uses `uint8_t *`; `pb_decode_inner` was corrected to use a one-byte local.

The only outgoing call is `0x0048F682 -> 0x0048F4B8`, authenticated as private
`pb_decode_varint32_eof`. Production resolves it directly to the existing
source-owned leaf. There are no diagnostic, writable-data, heap, AEABI,
schema, callback, or hardware seams.

## Production placement

Apple Clang 21.0.0 emits 42 bytes at `[0x007B338C,0x007B33B6)`, after two
alignment bytes. Relocated and unrelocated SHA-256 values are
`f36301a6c133d6fcb0842f674a4c794a100d708843997b01ce57180b387ebaab`
and `1c1c3627e3f4e4e31029f32513dfe2a10e09a15c8c49f6e3cd5946a50ea753bc`.
The complete stock span is guarded and replaced by `B.W` plus Thumb NOP fill.

The corrected decoder loop now occupies 530 text bytes plus 88 diagnostic
bytes at `[0x007B3120,0x007B338A)`. Current overlay/component/package sizes
are `127122/3650518/4429012`, with package SHA-256
`7c62e89e6d051bb818c2b4c5c99b94a402a533f589feec3c6c5989ba35a1dbcf`.
Linux/Clang 22 and hardware execution remain deferred.

```sh
python3 tools/analyze_g2_nanopb_decode_tag.py --json
python3 -m unittest tests.test_runtime_nanopb_decode_tag
python3 components/apollo_main/core_overlay/build_component.py
```
