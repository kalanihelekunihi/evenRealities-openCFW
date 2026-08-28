# Apollo `0x5Dxxxx` none-group source attribution: batch 7

Status: research-only, software-only, not production-routed.

Batch 7 resolves seven census functions / 3,334 bytes from FreeType
`src/sfnt/sfobjs.c`: UTF-16BE and single-byte name conversion, face-name
selection, encoding lookup, WOFF-to-SFNT extraction, SFNT container opening,
and face initialization.

Evidence includes platform/language preference rules, replacement of
non-ASCII characters, the eleven-entry encoding map, WOFF header and aligned
table reconstruction, compressed-table expansion, TTC/version handling, and
face service discovery.  The source file, every claimed image body, and the
authenticated decompiler log are pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 106 | 20,404 |
| Exact source recovered in batch 7 | 7 | 3,334 |
| Cumulative none-group source | 99 | 16,574 |
| Typed external remainder | 99 | 17,070 |

Two census-omitted clusters / 2,468 bytes are separately pinned.  The first
is the 104-byte `sfnt_stream_close`/`compare_offsets` area before WOFF open.
The second is the 2,364-byte region after `sfnt_init_face`, source-ordered with
`sfnt_load_face` and `sfnt_done_face`.  Complete callable boundaries were not
emitted by the authenticated decompiler, so neither cluster is claimed and
the research provider rejects both.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains identity/provider metadata only.  No
production component, global census, package, overlay, Makefile, or hardware
path is modified.
