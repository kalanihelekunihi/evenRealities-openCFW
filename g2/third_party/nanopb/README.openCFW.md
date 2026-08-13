# nanopb 0.4.9 compatibility snapshot

This directory contains an authenticated, minimal nanopb C runtime snapshot
from the official `nanopb-0.4.9` annotated tag. The selected tag resolves to
commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824` and tree
`2c4c260bcff3f9f7081238d377274dd385d76582`.

## Qualification

Version 0.4.9 is a deliberate openCFW compatibility choice. Authenticated G2
disassembly and reference builds prove compatibility with pristine upstream
0.4.7, 0.4.8, and 0.4.9, but cannot distinguish those point releases. This
snapshot therefore does **not** claim that Even Realities used the 0.4.9 tag
or this exact Git checkout. See
`docs/research/nanopb-point-release-recovery-audit.md` for that boundary.

## Included closure

The eight pristine upstream files are the complete minimal runtime closure:

- `pb.h`
- `pb_common.c` and `pb_common.h`
- `pb_decode.c` and `pb_decode.h`
- `pb_encode.c` and `pb_encode.h`
- `LICENSE.txt`, containing the complete Zlib license

`PROVENANCE.json`, the exact annotated-tag and commit payloads, and the root
tree closure let `verify_snapshot.py` reconstruct every relevant Git object
identity without network access or trust in a working-tree checkout.

## Recovered G2 option contract

`g2-config/pb_g2_options.h` is openCFW-authored compatibility glue, not an
upstream file and not a recovered vendor header. It records the evidence-backed
runtime settings and rejects contradictory build flags:

- allocation support off (`PB_ENABLE_MALLOC` undefined)
- 16-bit `pb_size_t` (`PB_FIELD_32BIT` undefined)
- 64-bit scalar support on (`PB_WITHOUT_64BIT` undefined)
- native FP64 (`PB_CONVERT_DOUBLE_FLOAT` undefined)
- UTF-8 validation off (`PB_VALIDATE_UTF8` undefined)
- callback streams and runtime error strings enabled
- packed structures and packed repeated scalar encoding enabled
- `PB_MAX_REQUIRED_FIELDS` fixed at 64

Fixed-count and fixed-length fields are generated-schema choices, not runtime
preprocessor options. They remain permitted by the runtime but cannot be
reconstructed without the first-party Even schemas.

## Production boundary

The pristine translation units in this subtree remain reference material and
are not linked wholesale. Production selects exactly thirty-five bounded altered
functions against the authenticated 0.4.9 compatibility baseline:
`components/shared/nanopb/runtime_nanopb_istream_from_buffer.c`,
`components/shared/nanopb/runtime_nanopb_decode_varint.c`,
`components/shared/nanopb/runtime_nanopb_decode_svarint.c`,
`components/shared/nanopb/runtime_nanopb_decode_varint32.c` plus its shared
header, providing private `pb_decode_varint32_eof` and public
`pb_decode_varint32` as two independently audited functions,
`components/shared/nanopb/runtime_nanopb_skip_varint.c`,
`components/shared/nanopb/runtime_nanopb_skip_string.c` plus its header,
`components/shared/nanopb/runtime_nanopb_skip_field.c` plus its header,
`components/shared/nanopb/runtime_nanopb_read_raw_value.c` plus its header,
`components/shared/nanopb/runtime_nanopb_make_string_substream.c` plus its header,
`components/shared/nanopb/runtime_nanopb_decode_bool.c` plus its header,
`components/shared/nanopb/runtime_nanopb_dec_bool.c` plus its header,
`components/shared/nanopb/runtime_nanopb_dec_varint.c` plus its header,
`components/shared/nanopb/runtime_nanopb_dec_bytes.c` plus its header,
`components/shared/nanopb/runtime_nanopb_dec_string.c` plus its header,
`components/shared/nanopb/runtime_nanopb_dec_submessage.c` plus its header,
`components/shared/nanopb/runtime_nanopb_decode_inner.c` plus its header,
`components/shared/nanopb/runtime_nanopb_decode_tag.c` plus its header,
`components/shared/nanopb/runtime_nanopb_iterator_cluster.c` plus its header,
`components/shared/nanopb/runtime_nanopb_defaults_pair.c` plus its header,
`components/shared/nanopb/runtime_nanopb_close_string_substream.c`,
`components/shared/nanopb/runtime_nanopb_decode_fixed32.c`, and
`components/shared/nanopb/runtime_nanopb_decode_fixed64.c`, the shared provider
`components/shared/nanopb/runtime_nanopb_read.c`, and private `buf_read` and
`pb_readbyte` adaptations. The constructor pins the exact upstream definition
at `pb_decode.c[5114:5692]`, complete 28-byte stock span, all 30 callers,
recovered 16-byte ABI, and canonical callback identity `0x0048F3A5`. The varint decode
leaf pins the recovered G2 stream ABI, exact stock span, local error-string
closure, and sole stock `pb_readbyte` seam. The skip leaf independently pins
its source and header, exact upstream `pb_skip_varint` definition, stock span
`[0x0048F628,0x0048F64C)`, and sole `pb_read` seam at `0x0048F3BE`. The close
leaf likewise pins its source and header, exact upstream
`pb_close_string_substream` definition, stock span
`[0x0048F7CA,0x0048F7F4)`, and sole `pb_read` seam at `0x0048F3BE`, including
the final Apple and Linux text contracts recorded by the production overlay.
The fixed32 leaf pins the exact upstream `pb_decode_fixed32` definition at
`pb_decode.c` bytes `[43210,43828)`, stock span
`[0x00490190,0x004901AC)`, and the same retained `pb_read` seam. The fixed64
leaf pins the exact upstream `pb_decode_fixed64` definition at `pb_decode.c`
bytes `[43854,44688)`, the complete Apollo-main stock span
`[0x004901AC,0x004901CC)`, and its sole `pb_read` ABI entry seam at
`0x0048F3BE`. The signed-varint leaf pins the authenticated upstream
`pb_decode.c[42912:43210]` definition, local production source/header/audit,
complete stock span `[0x00490150,0x00490190)`, and its sole direct relocation
to the separately source-owned unsigned-varint decoder. Its exact-root Linux
contract is a 50-byte leaf at `0x007B323C`, with only the same `+0x08`
`R_ARM_THM_CALL` relocation and no allocated writable data. The `pb_read` entry
now redirects to the 158-byte source-owned `pb_read`
leaf. The provider pins its byte-identical upstream definition across 0.4.7,
0.4.8, and 0.4.9, all 13 external direct callers, the absence of interior or
stored-pointer ingress, and its exact Apple/Linux placements. It retains only
three explicit stock seams: private `buf_read` Thumb identity `0x0048F3A5`,
`end-of-stream` at `0x00787C70`, and `io error` at `0x0078B690`. No bootloader
homolog was authenticated. The private/public varint32 pair additionally pins
the canonical upstream definitions at bytes `[5762,7483)` and `[7485,7617)`,
their independent stock patches, per-toolchain private text/literal/public text,
and direct source-to-source calls. Exact-root Linux additionally authenticates
both CANTUNWIND/PREL31 companions and the complete package/report/flash-plan
aggregate. The skip-string leaf pins the byte-identical 0.4.7--0.4.9 upstream
definition, the complete 32-byte stock patch, two source-to-source calls, and
the 34-byte Apple/Linux placements at `0x007B2C4C` / `0x007B336C`. The
`pb_skip_field` leaf pins the complete 74-byte stock dispatcher, two callers,
four source-provider calls, 66 bytes of Apple text, and its 18-byte diagnostic
closure. The private `read_raw_value` leaf pins the complete 148-byte stock
span, sole caller, three stock calls to the source-owned read provider, 134
bytes of Apple text, and its 34-byte diagnostic closure. The public
`pb_make_string_substream` leaf pins all three callers, the 76-byte stock span,
72 bytes of Apple text, 24 diagnostic bytes, and an explicit four-field copy
that removes the compiler-runtime seam. The public/private Boolean pair pins
both complete stock spans, both exact
upstream definitions, the recovered iterator `pData` offset, and its two
source-to-source provider relocations. The private field-varint, bytes-field,
string-field, and submessage adapters bring the set to twenty-two. Source-owned
`pb_decode_inner` and `pb_decode_tag` bring it to twenty-four. The descriptor
provider, seven iterator entry points, and default callback add nine more; the
paired private defaults routines add two, bringing the authenticated bounded
production set to thirty-five functions. All are closed over source-owned
providers, explicit application/schema ABI, and local diagnostic data. All
thirty-five are compatibility selections within
the authenticated pristine 0.4.7--0.4.9 range, not proof of the vendor's
historical point release. `verify_snapshot.py` permits only those thirty-five
bounded functions and still
rejects direct production use of this subtree's `pb_common.c`, `pb_decode.c`,
or `pb_encode.c`.

`pb_skip_field` is production-integrated for the Apple-Clang profile at
`0x007B2C70`, with diagnostic rodata at `0x007B2CB2`. Its full closure and the
resulting overlay, component, package, and flash ownership are hash-pinned.
Linux/Clang 22 reproduction is explicitly pending because that reviewed
compiler is unavailable on this host; no Linux pins are inferred from Apple
output. See `docs/research/nanopb-skip-field-source-candidate-audit.md`.

Private `read_raw_value` is production-integrated for the Apple-Clang profile
at `0x007B2CC4`, with diagnostic rodata at `0x007B2D4A`. Its full closure and
the resulting overlay, component, package, flash, and byte-ownership pins are
exact. Linux/Clang 22 reproduction is explicitly pending; no Linux pins are
inferred from Apple output. See
`docs/research/nanopb-raw-substream-boundary-audit.md`.

The snapshot contains no Even `.proto` schema, generated `.pb.c`/`.pb.h`
message, transport binding, application callback, allocator, or hardware
port. Those items remain first-party glue and must be recovered and reviewed
separately. Version 0.4.9 is an openCFW compatibility selection within the
authenticated 0.4.7–0.4.9 range, not proof of the vendor's historical nanopb
revision or checkout.

Run the offline verifier and focused tests with:

```sh
python3 third_party/nanopb/verify_snapshot.py
python3 -m unittest -v tests.test_nanopb_snapshot
```

## License

nanopb is distributed under the Zlib license. The complete unchanged upstream
text is retained in `LICENSE.txt`; upstream source and headers retain their
copyright notices.

## Boolean decoder-pair production boundary

The bounded production set now includes altered `pb_decode_bool` and private
`pb_dec_bool` adaptations. Their authenticated upstream definitions are
`pb_decode.c[42715:42911]` and `[44696:44844]`. Complete stock entries at
`0x0049012C` and `0x004901CC` redirect to source leaves closed only over the
already source-owned public varint32 decoder and Boolean decoder. The pair
owns no stock string, data, helper, heap, schema, or port seam. Apple pins and
the pending Linux qualification are recorded in
`docs/research/nanopb-bool-cluster-source-audit.md`.

## Private field-varint production boundary

The bounded production set now also includes altered private `pb_dec_varint`,
bringing the allowlist to nineteen functions. Its authenticated upstream
definition is `pb_decode.c[44845:47571]`. The complete stock span at
`[0x004901D6,0x00490352)` redirects to source text closed only over the
already source-owned unsigned- and signed-varint decoders; both diagnostics
are local source rodata. Apple pins and the pending Linux qualification are
recorded in `docs/research/nanopb-dec-varint-source-audit.md`.

## Private bytes-field production boundary

The bounded production set now also includes altered private `pb_dec_bytes`,
bringing the allowlist to twenty functions. Its authenticated upstream
definition is `pb_decode.c[47571:48677]`. The complete stock span at
`[0x00490358,0x004903EA)` redirects to source text closed only over the
already source-owned varint32 decoder and stream reader; all three diagnostics
are local source rodata. Apple pins and the pending Linux qualification are
recorded in `docs/research/nanopb-dec-bytes-source-audit.md`.

## Private string-field production boundary

The bounded production set now also includes altered private `pb_dec_string`,
bringing the allowlist to twenty-one functions. Its authenticated upstream
definition is `pb_decode.c[48677:49908]`. The complete stock span at
`[0x004903EA,0x00490488)` redirects to source text closed only over the
already source-owned varint32 decoder and stream reader; all three diagnostics
are local source rodata. Apple pins and the pending Linux qualification are
recorded in `docs/research/nanopb-dec-string-source-audit.md`.

## Private submessage production boundary

The bounded production set now also includes altered private
`pb_dec_submessage`, bringing the allowlist to twenty-two functions. Its
authenticated upstream definition is `pb_decode.c[49908:51557]`. The complete
stock span `[0x0049048C,0x00490538)` redirects to source text whose substream
make/close helpers, inner decoder, and diagnostic are source-owned. The indirect
message callback is retained as application/schema ABI. Apple pins and the
pending Linux qualification are recorded in
`docs/research/nanopb-dec-submessage-source-audit.md`.

## Inner decoder and tag production boundary

The source-owned `pb_decode_inner` and `pb_decode_tag` adaptations bring the
allowlist to twenty-four functions. Their complete stock entries redirect to
reviewed Apple-Clang leaves; helper calls that previously crossed into opaque
nanopb code now resolve to independently authenticated source providers. The
remaining callback seam is explicitly application/schema ABI. Evidence and
exact closure pins are recorded in
`docs/research/nanopb-decode-inner-source-audit.md` and
`docs/research/nanopb-decode-tag-source-audit.md`.

## Descriptor and iterator production boundary

The descriptor provider, mutable and const iterator begin variants, extension
variants, `next`, both `find` variants, and the default field callback bring the
allowlist to thirty-three functions. Eight complete stock entry spans redirect
to nine independently compiled leaves in the production overlay. The 536 bytes
of now-unreachable stock private implementation remain deliberately classified
as opaque rather than being overclaimed as source-owned. Exact upstream slices,
ABI recovery, call closure, placements, entry patches, and ownership accounting
are recorded in `docs/research/nanopb-iterator-cluster-source-audit.md`.

## Defaults-pair production boundary

Private `pb_message_set_to_defaults` and `pb_field_set_to_default` are now
selector-isolated from `components/shared/nanopb/runtime_nanopb_defaults_pair.c`.
Their complete 438-byte stock span redirects to 414 bytes of source-owned Apple
text plus two alignment bytes. Stream, tag, iterator, and recursive-default
edges bind to source providers; only private `decode_field @ 0x0048FBE4`
remains fixed stock. Evidence and exact pins are in
`docs/research/nanopb-message-defaults-source-audit.md` and
`docs/research/nanopb-field-default-source-audit.md`.

## Dispatch and extension production boundary

Private `decode_field`, `default_extension_decoder`, and `decode_extension`
are selector-isolated from
`components/shared/nanopb/runtime_nanopb_dispatch_extension.c`. Their exact
definitions are pinned to the selected nanopb 0.4.9 commit and are
byte-identical across the checked official 0.4.4--0.4.9.1 tags. Three complete
stock executable entries redirect to reviewed source; the 16-byte literal
island between the latter two entries remains opaque/cut-forward. Static,
pointer, and callback field decoders are the next source frontier, while the
dynamic extension callback is retained as application/schema ABI. Evidence
and exact pins are in
`docs/research/nanopb-dispatch-extension-source-audit.md`.

## Field-decoder production boundary

Private `decode_basic_field`, `decode_static_field`, the no-malloc
`decode_pointer_field`, `decode_callback_field`, and
`pb_dec_fixed_length_bytes` are selector-isolated from
`components/shared/nanopb/runtime_nanopb_field_decoder_cluster.c`, bringing
the bounded altered production allowlist to 43 functions. Five complete stock
entries totaling 1,116 bytes redirect to 1,132 bytes of reviewed Apple source
closures plus eight alignment bytes. Every fixed call binds a separately
authenticated source-owned nanopb provider; two dynamic callback sequences
remain application/schema ABI. Definition comparisons establish compatibility
with official releases from 0.4.6 through 0.4.9.1 for the complete unit but do
not uniquely prove the vendor checkout. Evidence and exact pins are in
`docs/research/nanopb-field-decoder-cluster-boundary-audit.md`.
