# Apollo `0x5Dxxxx` none-group source attribution: batch 1

Status: research-only, software-only, not production-routed.

After completing the census-attributed closure, 198 functions / 33,644 bytes
remain in the `none` evidence group.  This first bounded batch recovers ten
exact FreeType PostScript/CFF identities totaling 1,364 bytes:

- `psobjs.c`: `ps_builder_add_point`, `ps_builder_add_point1`,
  `ps_builder_add_contour`, `ps_builder_start_point`, and `ps_decoder_init`.
- `t1decode.c`: `t1_decoder_parse_metrics` and `t1_decoder_init`.
- `cffdecode.c`: `cff_compute_bias`, `cff_decoder_init`, and
  `cff_decoder_prepare`.

These identities are supported by complete body semantics, exact ABI field
layouts, ordered source families, distinctive constants, and authenticated
stock ranges.  For example, `cff_compute_bias` preserves the exact 1240 and
33900 thresholds and 107, 1131, and 32768 results.  The Type 1 metrics parser
preserves its restricted operator set and `0xA0`/`0xA1` error paths.

A neighbouring 40-byte body at `0x005D1D2A` was not accepted as `t1_decrypt`:
its body is a structure accessor and does not implement decryption.  This is an
explicit example of rejecting a tempting size/order-only attribution.

The analyzer exhaustively records all 198 entries.  The ten positively
identified entries route through the named research provider; the other 188
entries / 32,280 bytes are typed unsupported externals until a later bounded
batch supplies positive evidence.

| State | Functions | Bytes |
|---|---:|---:|
| None-group baseline | 198 | 33,644 |
| Exact source recovered | 10 | 1,364 |
| Typed external remainder | 188 | 32,280 |

The actual source remains under `g2/third_party/freetype` with the FreeType
Project License and retained file-specific notices and grants.  The Apache-2.0
adapter under `g2/research/candidates/cordio_ll_sea_none_batch1` copies no
upstream implementation.  No production components, global census outputs,
manifests, packaging, overlays, Makefiles, or hardware are modified.
