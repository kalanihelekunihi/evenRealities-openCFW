# Apollo opacity wave 10: round-join and MVE closure

Status: software-only research admission; no hardware operation and no
production routing.

## Selection and residual

Wave 9 leaves 1,353 functions / 154,460 official opaque bytes. The largest
remaining envelope is `[0x0051B140,0x0051B8EA)`, 1,962 bytes. Its complete
actionable closure contains only that body: every real static target already
belongs to opacity wave 1, 2, or 6.

| State | Functions | Bytes |
|---|---:|---:|
| Before wave 10 | 1,353 | 154,460 |
| Newly typed | 1 | 1,962 |
| After wave 10 | 1,352 | 152,498 |

The next-largest envelope is `0x005AF88C`, 1,912 bytes.

## Real call closure versus decoder artifacts

The decompiler body contains seven `FUN_...` targets across 26 call sites:

| Prior owner | Target | Sites | Role |
|---|---:|---:|---|
| Wave 2 | `0x0052266E` | 8 | command-state mask helper |
| Wave 1 | `0x005226B2` | 1 | state leaf |
| Wave 6 | `0x00522A24` | 1 | six-coordinate record builder |
| Wave 6 | `0x00522F1C` | 4 | tessellation-count helper |
| Wave 6 | `0x00523A34` | 4 | guarded polyline entry |
| Wave 6 | `0x0052405C` | 4 | periodic polynomial helper A |
| Wave 6 | `0x00524130` | 4 | periodic polynomial helper B |

An independent Thumb scan of the authenticated installed envelope finds the
same 26 direct `BL` sites and targets. It finds no wide non-link continuation
and no register `BLX` site.

Ghidra 12.1.2 also renders sixteen expressions named `func_0x...` in four
repeated vectorized blocks. The supposed addresses are not targets of any
machine-code branch in the body. Each occurs once and is recorded in
`reconciled_callother.tsv` as a zero-byte decompiler callother artifact. This
prevents partial MVE/Helium decoding from becoming sixteen fabricated provider
dependencies while retaining a deterministic audit if the decompiler output
changes.

## Behavior and data closure

The body derives segment counts and sine/cosine recurrence steps, generates a
fan of intermediate points between stroke-edge vectors, and passes the result
to the existing polyline/command helpers. Its bounded role is therefore
`round-stroke-join-fan-tessellation-coordinator`; this is not an upstream symbol
claim.

Its two decoded ranges omit a referenced `180.0f` literal at `0x0051B4EC`.
Those four bytes already belong to the official 1,962-byte envelope. The full
post-envelope census gap `[0x0051B8EA,0x0051B8F0)` contains two zero padding
bytes and a second referenced `180.0f`. The context-pointer cell at
`0x0051BF74` is shared with the next residual body at `0x0051B8F0`. Together
the two out-of-envelope support islands contain 10 physical bytes. All three
direct `DAT_` cells are covered, and no support byte is subtracted as a new
function byte.

## Provider and license boundary

The sole caller, `0x0051F798`, is parent-classified first-party at medium
confidence, and all real callees are in the established vector-path community.
That supports product/vector behavior only. The root is absent from the eleven
stock Nema symbols resolved by checked-in evidence. The public Apollo5 Nema
archive was generated with GCC and is explicitly not byte-identical to the
IAR-generated stock; the exact internal archive or maintained implementation
source is unavailable. The FreeType census independently records no anchor,
string, or call-community evidence for this body.

Consequently no upstream function identity, provider, source path, or license
is claimed. The body remains `typed-external-provider-unavailable` with license
status `unavailable`.

## Production admission

Honest admission requires exact maintained source and license, ABI and
configuration closure, and a reviewed Cortex-M55 code-generation, relocation,
link, and placement recipe. None is established. This wave adds no callable
replacement or binary overlay and performs no signing, flashing, probing, or
directed hardware test.
