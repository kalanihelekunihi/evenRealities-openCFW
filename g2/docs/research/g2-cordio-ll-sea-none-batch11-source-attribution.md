# Apollo `0x5Dxxxx` none-group source attribution: batch 11

Status: research-only, software-only, not production-routed.

Batch 11 closes the complete census-visible `psconv.c` and `psobjs.c`
sequence: 40 functions / 5,516 bytes.  The first six are all PostScript
conversion primitives.  The remaining 34 cover table growth, parser token
scanning and field loading, and the Type 1, CFF, and generic PostScript
builder families.

The identities are supported by full source order and distinctive complete
semantics: base-2-through-36 signed conversion and saturation, decimal fixed
point scaling, ASCIIHex and eexec state updates, 1,024-byte table growth,
PostScript literal-string escape and nesting rules, token-array restoration,
typed field conversion, and the paired builder layouts with 26.6 versus
16.16 coordinate conversion.  Both source files, each claimed image body,
and the authenticated decompiler log are content-pinned.

| State | Functions | Bytes |
|---|---:|---:|
| Prior typed-external residual | 54 | 6,312 |
| Exact source recovered in batch 11 | 40 | 5,516 |
| Cumulative none-group source | 184 | 32,848 |
| Typed external remainder | 14 | 796 |

Seven source-order omissions / 580 bytes are separately pinned.  They cover
alignment, table release, parser scalar wrappers and lifecycle calls, and the
Type 1/CFF/generic builder teardown or contour-close boundaries.  Because the
authenticated decompiler did not emit complete callable records for these
intervals, none is claimed and the provider rejects every omitted address.

The upstream implementation retains the FreeType Project License.  The
Apache-2.0 research adapter contains identity/provider metadata only and
copies no upstream implementation.  No production component, global census,
package, overlay, Makefile, or hardware path is modified.
