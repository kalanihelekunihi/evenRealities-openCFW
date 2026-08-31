# Apollo opacity wave 6: vector-stroke closure

Status: software-only, research admission; no hardware operation or production
routing.

> Historical accounting note: later public-DWARF correlation identifies the
> 3,306-byte root at `0x0051C5EC` as NemaVG `draw_caps`. That coordinator is now
> production-routed to reviewed MIT source; its two endpoint providers remain
> stock-retained and unpatched over 3,308 bytes. The wave totals and the other
> typed terminal boundaries below remain provenance history, not the current
> release-readiness mask. See
> [the stroke-cap candidate audit](g2-nemavg-stroke-caps-source-candidate.md).

## Complete actionable closure

Wave 5 ended at 1,395 unclassified functions / 172,308 official opaque
bytes. The largest remaining envelope, `[0x0051C5EC,0x0051D2D6)`, contributes
3,306 official bytes and 3,298 decoded corpus bytes.

Following calls into the actionable residual and the authenticated guarded
continuation produces this complete closure:

| Depth | Functions | Bytes | Disposition |
|---:|---:|---:|---|
| 0 | 1 | 3,306 | typed external |
| 1 | 5 | 644 | typed external |
| 2 | 1 | 436 | typed external |
| **Total** | **7** | **4,386** | provider unavailable |

The non-call edge matters. The exact bytes `03 29 00 da 70 47` at
`0x00523A34` form a six-byte Thumb guard; its taken branch enters the separately
counted body at `0x00523A3A`. The static function-callee list omits that edge,
while the decompiler repeats the continuation semantics under both entry
points. The analyzer pins the instruction bytes, models the continuation once
for byte accounting, and validates both corpus bodies.

All seven terminal targets are already typed wave-1, wave-2, or wave-3
boundaries. They contribute zero new wave-6 bytes. No source-owned or
zero-official-opaque target is newly encountered.

## Source, provider, and license boundary

The root coordinates stroke caps and joins. Its closure contains a
six-coordinate command-record builder, a bounded segment-count helper, the
guarded polyline-record body, and two periodic polynomial helpers. These roles
are bounded by observed behavior; they are not upstream symbol names.

NemaGFX/NemaVG remains candidate-family context. None of the seven entries is
among the eleven authenticated stock Nema symbols. The available maintained
Apollo5 archive is GCC generated and explicitly not byte-identical to the
IAR-generated stock, so it cannot authenticate these exact bodies. Every row
also has an explicit FreeType-negative census record.

At the time of this wave there was consequently no exact maintained
implementation that could honestly be admitted for this batch. No provider,
upstream function identity, or license was claimed. All seven rows were SHA-pinned
`typed-external-provider-unavailable` boundaries. Assigning MIT or the Think
Silicon notice without source identity would fabricate provenance.

## Accounting and production boundary

| State | Functions | Bytes |
|---|---:|---:|
| Before wave 6 | 1,395 | 172,308 |
| Newly typed | 7 | 4,386 |
| After wave 6 | 1,388 | 167,922 |

The next largest envelope is 2,598 bytes at `0x00564974`.

Production admission remains blocked on exact source/provider identity,
license, ABI/configuration closure, and a reviewed code-generation,
relocation, and placement recipe. The analyzer performs no signing, flashing,
probing, device access, or production routing.
