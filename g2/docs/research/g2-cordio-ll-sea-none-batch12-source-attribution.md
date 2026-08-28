# Apollo `0x5Dxxxx` none-group source attribution: batch 12 closure

Status: research-only, software-only, not production-routed.

Batch 12 closes all 14 remaining census bodies / 796 bytes.  Eight bodies /
276 bytes are authenticated FreeType source: five `t1cmap.c` Type 1 cmap
callbacks, two Adobe CF2 helpers from `psft.c`, and
`ttbdf.c:tt_face_free_bdf_props`.  Six bodies / 520 bytes are the complete
SEGGER RTT 6.18a write path from initialization through locked write.

The FreeType evidence includes exact cmap field layouts and callback slots,
CF2 instance finalization and contour-close behavior, and BDF ownership and
field clearing.  SEGGER evidence includes the 168-byte control block,
16-byte ID copy, configured channel fields, ring-buffer wrap arithmetic,
blocking/no-check writers, available-space calculation, the three mode
branches, and BASEPRI-protected public write wrapper.  Every body and all
three FreeType sources are pinned.  The SEGGER provider is pinned through the
existing vendor manifest to the Nordic SDK-bundled 6.18a source SHA-256.

| Final none-census state | Functions | Bytes |
|---|---:|---:|
| FreeType source | 192 | 33,124 |
| SEGGER RTT provider source | 6 | 520 |
| Classified total | 198 | 33,644 |
| Unclassified | 0 | 0 |

Four surrounding non-census clusters / 1,118 bytes are also explicitly
typed and SHA-pinned: the standard-cmap teardown, remaining Type 1 cmap
callbacks/classes, CF2 line/cubic callbacks, and remaining BDF load/find
area.  They are not opaque: each record states that the authenticated
decompiler corpus lacks a complete callable record.  They therefore remain
unsupported external boundaries and the provider rejects their addresses.

Licensing is provider-specific.  FreeType and Adobe-derived code retains the
FreeType Project License and file notices.  SEGGER RTT retains its
redistributable-source license from the pinned upstream bundle.  The
Apache-2.0 research adapter contains metadata only and copies no upstream
implementation.  Production routing remains disabled; no package, global
census, overlay, Makefile, or hardware path is modified.
