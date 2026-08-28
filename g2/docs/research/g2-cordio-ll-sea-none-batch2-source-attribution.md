# Apollo `0x5Dxxxx` none-group source attribution: batch 2

Status: research-only, software-only, not production-routed.

This batch resolves the contiguous `0x005D70A4`–`0x005D7B62` community as
18 compiled routines from FreeType `src/pshinter/pshalgo.c`, totaling 2,750
bytes.  Evidence is positive rather than adjacency-only: the firmware retains
the same complete routine order, call topology, structure strides, and
distinctive arithmetic as the authenticated source.

The sequence covers hint overlap/table management, mask activation, stem
quantization and alignment, inflection discovery, glyph teardown, direction
classification, point load/save, glyph construction, and extrema discovery.
Especially discriminating invariants include the `10/32/54` fractional stem
thresholds, `40/48/64` standard-width behavior, the `12x` direction test,
orientation-sign changes across circular contours, and the paired 40-byte
point records built by glyph initialization.

Source-order gaps also agree: `ps_simple_scale` and `psh_print_zone` are debug
only, while `psh_hint_align_light` is enclosed in `#if 0`; none appears in the
release image.  The batch stops before `0x005D7B62` and does not infer the next
identity from proximity.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 188 | 32,280 |
| Exact source recovered in batch 2 | 18 | 2,750 |
| Cumulative none-group source | 28 | 4,114 |
| Typed external remainder | 170 | 29,530 |

The implementation source remains under `g2/third_party/freetype` with the
FreeType Project License and its file-specific notice.  The Apache-2.0 adapter
under `g2/research/candidates/cordio_ll_sea_none_batch2` contains identity and
provider records only; it copies no FreeType implementation.  No production
component, census output, manifest, packaging, overlay, Makefile, or hardware
path is changed.
