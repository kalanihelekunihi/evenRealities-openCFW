# Independent review — P2-21471

Status: partial; accepted: false.

Fresh replay passed for the exact 130-byte span, and regenerated instruction/reference records match the candidate. The selector reads object+40 independently to choose 14, 12, or 10. The subsequent compare-against-zero branch is retained even though these immediate selector values make its zero case unreachable in the local flow.

On the arithmetic path, the selector is reread, object+44 is freshly loaded, and the 32-bit multiply/add wraps before signed SDIV by 160. Signed results below two select one; otherwise the selector and object word are freshly read again and the arithmetic is recomputed into R1. The final call is 4D4892(object+64,R1,live R2/R3). The 32-byte frame remains open at the boundary.

The helper contract and later continuation remain unresolved. Review remains partial/unaccepted.
