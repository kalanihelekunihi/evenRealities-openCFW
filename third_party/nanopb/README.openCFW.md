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
are not linked wholesale. Production selects exactly thirteen bounded altered
functions against the authenticated 0.4.9 compatibility baseline:
`components/shared/nanopb/runtime_nanopb_istream_from_buffer.c`,
`components/shared/nanopb/runtime_nanopb_decode_varint.c`,
`components/shared/nanopb/runtime_nanopb_decode_svarint.c`,
`components/shared/nanopb/runtime_nanopb_decode_varint32.c` plus its shared
header, providing private `pb_decode_varint32_eof` and public
`pb_decode_varint32` as two independently audited functions,
`components/shared/nanopb/runtime_nanopb_skip_varint.c`,
`components/shared/nanopb/runtime_nanopb_skip_string.c` plus its header,
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
the 34-byte Apple/Linux placements at `0x007B2C4C` / `0x007B336C`. All thirteen
are
compatibility selections within the authenticated pristine 0.4.7--0.4.9
range, not proof of the vendor's historical point release.
`verify_snapshot.py` permits only those thirteen bounded functions and still
rejects direct production use of this subtree's `pb_common.c`, `pb_decode.c`,
or `pb_encode.c`.

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
