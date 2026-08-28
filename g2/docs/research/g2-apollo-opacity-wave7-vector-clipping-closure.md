# Apollo opacity wave 7: vector-clipping closure

Status: software-only, research admission; no hardware operation or production
routing.

## Complete graph and physical partition

Wave 6 ended at 1,388 unclassified functions / 167,922 official opaque
bytes. The largest remaining root is `[0x00564974,0x0056539A)`, with 2,598
official bytes and 2,588 decoded code-range bytes. It calls one actionable
body, `[0x005640E4,0x0056496E)`, with 2,186 official bytes and 2,174 decoded
code-range bytes. That callee has no outgoing calls.

| Depth | Functions | Official bytes |
|---:|---:|---:|
| 0 | 1 | 2,598 |
| 1 | 1 | 2,186 |
| **Total** | **2** | **4,784** |

The terminal frontier is empty. The graph is complete without importing an
unrelated address hull.

The 22-byte difference between official envelopes and decoded code ranges is
also exhaustively partitioned:

| Interior | Bytes | Classification | Accounting |
|---|---:|---|---:|
| `0x00564156–0x0056415C` | 6 | NOP + near-one float literal | 0 new |
| `0x00564556–0x0056455C` | 6 | NOP + epsilon float literal | 0 new |
| `0x00564A3E–0x00564A44` | 6 | NOP + shared context pointer | 0 new |
| `0x00564F5C–0x00564F60` | 4 | epsilon float literal | 0 new |

The pointer cell at `0x00564A40` contains `0x20074F04` and is referenced by
both functions. It lies inside the root's official envelope, so it is shared
physical evidence but not a third function or another byte charge. The
analyzer derives all four gaps from the pinned Ghidra ranges, authenticates
their exact bytes and hashes, and verifies the retained data references.

## Source and provider boundary

Observed behavior supports the bounded roles of segment/rectangle intersection
collection and clipped-segment/state-buffer coordination. Those descriptions
do not assert a named clipping algorithm or upstream symbol.

NemaGFX/NemaVG is candidate-family context only. Neither function appears in
the eleven authenticated stock Nema symbols, and the maintained public Apollo5
archive is GCC generated rather than a byte-identical match for the IAR stock.
The root has mixed ingress: one still-unresolved caller and one caller marked
first-party by medium-confidence topology. That cannot establish the linked
implementation's provider or license.

No exact maintained source is therefore admissible. Both functions remain
SHA-pinned `typed-external-provider-unavailable` boundaries with provider and
license explicitly unavailable.

## Accounting and production boundary

| State | Functions | Bytes |
|---|---:|---:|
| Before wave 7 | 1,388 | 167,922 |
| Newly typed | 2 | 4,784 |
| After wave 7 | 1,386 | 163,138 |

The next largest envelope is 2,338 bytes at `0x005A8D06`.

Production admission remains blocked on exact source/provider identity,
license, ABI/configuration closure, and a reviewed code-generation,
relocation, and placement recipe. No signing, flashing, device access, or
production routing is performed.
