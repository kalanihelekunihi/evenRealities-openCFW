# Apollo `0x5Dxxxx` none-group source attribution: batch 6

Status: research-only, software-only, not production-routed.

Batch 6 resolves the largest next coherent community: eight census functions
/ 2,386 bytes from FreeType `src/sfnt/sfdriver.c`.  The sequence covers
MurmurHash3 finalization and 128-bit hashing, Windows/Apple name extraction,
name-record selection, fixed-point decimal formatting, variable-font
PostScript-name generation, and final PostScript-name lookup.

Evidence includes the complete MurmurHash tail mixer and four-lane
finalization, platform/encoding/language tuples, UTF-16BE filtering, the
five-digit 16.16 fractional formatter, 127-byte PostScript name cap, and
variation-axis hashing/assembly call topology.  Source, image bodies, and the
authenticated decompiler log are pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 114 | 22,790 |
| Exact source recovered in batch 6 | 8 | 2,386 |
| Cumulative none-group source | 92 | 13,240 |
| Typed external remainder | 106 | 20,404 |

Two census-omitted clusters / 148 bytes bracket the sequence: the 64-byte
`sfnt_is_postscript`/`sfnt_is_alphanumeric` predicate area and the 84-byte
`sfnt_get_charset_id` candidate.  Their source order and bytes are recorded,
but complete callable boundaries were not emitted by the authenticated
decompiler, so this batch does not claim them and the provider fails closed.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains identity/provider metadata only.  No
production component, global census, package, overlay, Makefile, or hardware
path is modified.
