# Apollo `0x5Dxxxx` none-group source attribution: batch 10

Status: research-only, software-only, not production-routed.

Batch 10 closes the largest remaining coherent SFNT single-object sequence:
19 census functions / 3,614 bytes from FreeType `ttcmap.c`, `ttkern.c`,
`ttload.c`, `ttmtx.c`, and `ttpost.c`.  It completes the census-visible
synthetic-Unicode/build-cmap tail, kerning teardown and lookup, table-directory
loading, generic/head/name loading, glyph metrics, and PostScript format 2.0
and 2.5 name loaders.

Evidence includes the cmap provider callback layout and class validation,
ordered/linear kerning masks, 16-byte SFNT directory records, head-table
minimum size and tags, directory allocation and duplicate rejection, name and
language-tag record strides, horizontal/vertical metric fallback, and the
PostScript `0x00020000`/`0x00025000` formats with their 258-name limit.  All
five source files, every claimed body, and the authenticated decompiler log
are content-pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 73 | 9,926 |
| Exact source recovered in batch 10 | 19 | 3,614 |
| Cumulative none-group source | 144 | 27,332 |
| Typed external remainder | 54 | 6,312 |

The complete 102-byte wrapper immediately beyond the `0x5Dxxxx` census, at
`0x005E0002`–`0x005E0068`, is separately authenticated as
`ttpost.c:load_post_names`.  Its dispatch on PostScript formats 2.0 and 2.5
and calls to the two admitted loaders make the boundary exact; it is reported
outside the none-group accounting rather than silently folded into it.

Three intervening census-omitted clusters / 1,458 bytes are content-pinned
but remain unclaimed.  They cover `tt_face_load_kern`, the bhed/maxp area,
and the remaining `ttload.c` plus `ttmtx.c` table/header loaders.  The
authenticated decompiler did not emit complete callable records for those
intervals, so the research provider continues to reject them.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains identity/provider metadata only and
copies no upstream implementation.  No production component, global census,
package, overlay, Makefile, or hardware path is modified.
