# Apollo `0x5Dxxxx` none-group source attribution: batch 9

Status: research-only, software-only, not production-routed.

Batch 9 closes the remaining census-visible code bodies from FreeType
`src/sfnt/ttcmap.c`: 20 functions / 4,542 bytes across cmap formats 0, 2, 8,
12, 13, and 14.  Combined with batch 8's format-4 engine, every census body
that can be positively authenticated to this upstream module is now named.

The evidence is format-specific rather than adjacency-only.  It includes the
format-0 256-byte glyph array, format-2 subheader-key layout, format-8
8,192-byte `is32` bitmap, format-12/13 twelve-byte group ordering, and the
format-14 default/non-default UVS record sizes, 24-bit Unicode values,
`0x10FFFF` ceiling, binary searches, allocation growth, and merged character
enumeration.  The source file, each claimed image body, and the authenticated
decompiler log are content-pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 93 | 14,468 |
| Exact source recovered in batch 9 | 20 | 4,542 |
| Cumulative none-group source | 125 | 23,718 |
| Typed external remainder | 73 | 9,926 |

Nine census-omitted clusters / 2,824 bytes are separately pinned.  They cover
the intervening format accessors, provider-class boundaries, format-6 and
format-10 bodies, format-12/13 mapping wrappers, and several format-14
enumeration helpers.  Their source order is strong evidence, but complete
callable records were not emitted by the authenticated decompiler.  They are
therefore not claimed, and the research provider rejects every omitted
address.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains identity/provider metadata only and
copies no upstream implementation.  No production component, global census,
package, overlay, Makefile, or hardware path is modified.
