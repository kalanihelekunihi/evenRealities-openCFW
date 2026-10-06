# Independent review P2-18517

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 100-byte interval `0x460AAE..0x460B12`; instruction/reference manifests match. The bit-0 and conditional bit-2 branches use separate fresh `0x43D0CE` reads. On the set route, it calls `0x460084`, then `0x45FFFE` with the full first result and a separately recomputed field pointer. It freshly reads destination byte +40 to SP4, replaces R8 with the destination offset, freshly reads word +48 to SP0, and preserves the full selector in R3 for `0x43CE9E`. The selector is copied after those field reads. The repeated lookup results are not cached.

At `0x460B00`, R7 increments with 32-bit wrap. The alternate initial-entry address `0x460B02` skips that increment. Both converge on a fresh halfword read from source base+4; the full 32-bit counter R7 is compared signed against the zero-extended halfword. The code shown has no low16 counter normalization or fixed eight-entry bound. If R7 is less, another fresh mask read tests bit 1 and branches to the diagnostic path outside this map or to the external join.

No stride restoration, next body, or loop contract is inferred; child semantics remain unresolved. Partial/unaccepted only.
