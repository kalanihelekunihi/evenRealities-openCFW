# Apollo `0x5Dxxxx` none-group source attribution: batch 8

Status: research-only, software-only, not production-routed.

Batch 8 closes the census-visible TrueType cmap format-4 engine: six
functions / 2,602 bytes from FreeType `src/sfnt/ttcmap.c`.  The recovered
sequence is `tt_cmap4_set_range`, its stateful iterator, validator, linear and
binary mapping engines, and the character-index wrapper.

Evidence includes exact segmented-cmap array layout, `0xFFFF` sentinel
handling, `idDelta`/`idRangeOffset` arithmetic, overlap recovery flags,
validator level behavior, cached range iteration, and dispatch between linear
and binary mapping.  Source, every claimed image body, and the authenticated
decompiler log are pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 99 | 17,070 |
| Exact source recovered in batch 8 | 6 | 2,602 |
| Cumulative none-group source | 105 | 19,176 |
| Typed external remainder | 93 | 14,468 |

Two census-omitted boundary clusters / 888 bytes are content-pinned.  The
pre-format-4 cluster contains the format-2 tail/class data and format-4 init
boundary; the post-index cluster is source-ordered with format-4 char-next,
get-info, and class data before format 6.  Since the authenticated decompiler
did not expose complete callable records, neither cluster is claimed and the
provider fails closed.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains identity/provider metadata only.  No
production component, global census, package, overlay, Makefile, or hardware
path is modified.
