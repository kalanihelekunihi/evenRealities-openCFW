# Apollo opacity wave 9: elliptical-arc and runtime closure

Status: software-only research admission; no hardware operation and no
production routing.

## Selection and accounting

Wave 8 leaves an authoritative residual of 1,357 functions / 157,768 official
opaque bytes. Its largest envelope is `0x0051A8EC` (2,090 bytes). Walking every
static call whose target remains in that residual closes four bodies:

| Depth | Entry | Envelope | Decoded | Bounded behavior |
|---:|---:|---:|---:|---|
| 0 | `0x0051A8EC` | 2,090 | 2,078 | elliptical-arc and stroke-geometry coordinator |
| 1 | `0x0051A694` | 578 | 578 | quarter-arc cubic-segment builder |
| 2 | `0x00516CF8` | 274 | 274 | cubic-segment command emitter |
| 2 | `0x00563F40` | 366 | 366 | `tanf`-compatible runtime helper |

The graph contains 18 caller/callee pairs and 35 static call sites. Its eleven
terminals are exhaustively reconciled: seven were typed in opacity waves 1–3,
three are in the parent first-party bucket, and `0x004397A8` is the existing
MIT clean-room `sqrtf` redirect. None adds wave-9 bytes.

Subtracting the four newly typed rows leaves 1,353 functions / 154,460 bytes.
The next-largest envelope is `0x0051B140`, 1,962 bytes.

## What the evidence establishes

The root implements the characteristic center/radius normalization, square-
root correction, angular sweep selection, and quarter-angle subdivision of an
elliptical arc. The depth-1 helper uses the tangent of one quarter of an angle
and the `4/3` scale factor to form cubic control points. The depth-2 emitter
either invokes an earlier vector-path interpreter or constructs an opcode/data
record from the four point pairs. These are bounded semantic roles, not guessed
upstream symbol names.

`0x00563F40` is a complete single-precision tangent-compatible body: its range
reduction, exceptional-value handling, reciprocal branch, polynomial/rational
evaluation, and 52-byte coefficient table are all SHA-pinned. That supports
the semantic role, but not an exact maintained source identity.

## Byte partition

The root's decompiler ranges omit four physical islands totaling 12 bytes:
two referenced floats and two Thumb NOPs. They remain inside the root's
2,090-byte official envelope and are counted exactly once there.

The complete direct `DAT_` graph contains 33 distinct cells. Two are the
in-envelope floats. The remaining 31 cells are covered by five merged,
SHA-pinned support-data islands totaling 124 physical bytes. One context
pointer at `0x0051B134` is shared by the root and depth-1 helper. These support
bytes are recorded for closure but add zero function-opacity bytes.

## Provider and license boundary

The existing vector-path topology makes the authenticated NemaGFX 1.4.12 /
NemaVG 1.1.8 package relevant family context. It does not authenticate these
three function identities. All three are absent from the eleven stock symbols
resolved in the checked-in Nema provenance; its public Apollo5 archive retains
GCC metadata and is explicitly not byte-identical to the IAR-generated stock.
The original IAR archive/private source commit is unavailable. Accordingly,
no Think Silicon, Ambiq, or other upstream license is attached to these bodies.

The exact IAR DLIB release and maintained `tanf` implementation source are also
unavailable. The runtime body therefore retains
`proprietary-runtime-source-unavailable`, rather than being relabeled MIT or
silently replaced. The three vector bodies retain `unavailable`. Every new row
is `typed-external-provider-unavailable` and fail-closed.

## Production admission

There is no callable implementation or source admission in this wave. Honest
production routing would require exact maintained source/provider identity,
license clearance, ABI/configuration closure, and a reviewed Cortex-M55 IAR
or reproducible replacement code-generation, relocation, link, and placement
recipe. None is presently established. This wave performs no signing,
flashing, probing, directed hardware test, or binary-overlay edit.
