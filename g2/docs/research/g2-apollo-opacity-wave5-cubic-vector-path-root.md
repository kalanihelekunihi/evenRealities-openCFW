# Apollo opacity wave 5: cubic-vector-path root

Status: software-only, research admission; no hardware operation or production
routing.

## Selection and accounting reconciliation

Wave 4 ended at 1,396 unclassified parent-census functions / 177,364 official
opaque bytes. The largest remaining envelope is
`[0x00519290,0x0051A650)`: 5,056 official bytes, with 4,998 decoded corpus
bytes. The 58-byte corpus shortfall is pinned rather than silently treated as
decoded source.

Before typing the root, the analyzer reconciles every direct target:

| Frontier state | Functions | New wave-5 bytes |
|---|---:|---:|
| Prior wave 1–3 typed boundaries | 12 | 0 |
| Source-recreated, zero-official-opaque IAR `sqrtf` | 1 | 0 |
| Still-actionable callees | 0 | 0 |

Thus the complete new positive-byte closure consists of the root alone. The
thirteen terminal calls and their multiplicities are recorded in
`reconciled_graph.tsv`; previous positive byte counts remain attributed to
their original waves and are not double-counted here.

## Bounded behavior and provider boundary

The authenticated body recursively subdivides cubic geometry, calculates
stroke/path joins, updates path state, and calls the same vector-geometry and
command-record community closed in waves 1–3. This supports the bounded role
`cubic-vector-path-subdivision-and-stroke-root`.

The three callers (`0x005171F8`, `0x0051D2E0`, and `0x0051F798`) are classified
as first-party only by medium-confidence, single-family call topology. That is
ingress context, not proof that this separately linked body is first-party.

NemaGFX/NemaVG remains relevant candidate-family context. The authenticated
Nema manifest identifies versions 1.4.12 / 1.1.8 and eleven exact stock
symbols, but this root is not among them. Its public Apollo5 archive is GCC
generated and explicitly not byte-identical to the IAR-generated stock. The
FreeType census separately records no FreeType anchor, retained string, or
call-community evidence for this body.

No exact upstream function, provider, source body, or license is therefore
claimed. The SHA-pinned row remains
`typed-external-provider-unavailable`. Assigning the Nema permissive notice,
MIT, or any other license without an authenticated identity would be
speculative.

## Accounting and production boundary

| State | Functions | Bytes |
|---|---:|---:|
| Wave-4 residual / before wave 5 | 1,396 | 177,364 |
| Newly typed | 1 | 5,056 |
| After wave 5 | 1,395 | 172,308 |

The next largest positive envelope is 3,306 bytes at `0x0051C5EC`.

Production admission remains blocked on exact provider/source identity,
license, ABI/configuration closure, and an honest code-generation,
relocation, and placement recipe. The analyzer is read-only and performs no
signing, flashing, probing, device access, or production routing.
